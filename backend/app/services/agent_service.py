"""
智能旅行规划Agent：可以主动调用工具的AI助手
类似MCP (Model Context Protocol) 的架构
"""
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool, StructuredTool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.map_service import MapService
from app.services.route_planner import RoutePlanner


class SearchAttractionInput(BaseModel):
    """搜索景点输入"""
    city: str = Field(..., description="城市名称，如：北京、上海")
    keyword: str = Field(..., description="景点关键词，如：故宫、长城")
    limit: int = Field(5, description="返回数量，默认5个")


class CalculateRouteInput(BaseModel):
    """计算路线输入"""
    origin: str = Field(..., description="起点名称")
    destination: str = Field(..., description="终点名称")
    city: str = Field(..., description="所在城市")


class OptimizeRouteInput(BaseModel):
    """优化路线输入"""
    attractions: List[str] = Field(..., description="景点名称列表")
    city: str = Field(..., description="所在城市")


class TravelPlannerAgent:
    """旅行规划智能体"""
    
    def __init__(self):
        self.map_service = MapService()
        self.route_planner = RoutePlanner()
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model=settings.DEEPSEEK_MODEL,
            openai_api_key=settings.DEEPSEEK_API_KEY,
            openai_api_base=settings.DEEPSEEK_API_BASE,
            temperature=0.7,
            model_kwargs={"stream": False}
        )
        
        # 创建工具
        self.tools = self._create_tools()
        
        # 创建Agent
        self.agent = self._create_agent()
        
        # 对话历史
        self.chat_history = []
    
    def _create_tools(self) -> List[Tool]:
        """创建AI可以调用的工具"""
        
        # 工具1：搜索景点
        async def search_attractions_tool(city: str, keyword: str, limit: int = 5) -> str:
            """搜索指定城市的景点信息
            
            参数:
                city: 城市名称
                keyword: 景点关键词
                limit: 返回数量
            
            返回:
                景点列表的JSON字符串
            """
            try:
                results = await self.map_service.search_attractions(
                    city=city,
                    keyword=keyword,
                    limit=limit
                )
                
                if not results:
                    return f"未找到'{keyword}'相关景点"
                
                # 格式化结果
                attractions_info = []
                for idx, attr in enumerate(results[:limit], 1):
                    info = {
                        "序号": idx,
                        "名称": attr['name'],
                        "地址": attr.get('address', '未知'),
                        "类型": attr.get('type', '未知'),
                        "评分": attr.get('rating', 0),
                        "坐标": f"({attr['lng']}, {attr['lat']})"
                    }
                    attractions_info.append(info)
                
                import json
                return json.dumps(attractions_info, ensure_ascii=False, indent=2)
                
            except Exception as e:
                return f"搜索失败: {str(e)}"
        
        # 工具2：计算两点距离和路线
        async def calculate_route_tool(origin: str, destination: str, city: str) -> str:
            """计算两个地点之间的距离和路线
            
            参数:
                origin: 起点名称
                destination: 终点名称
                city: 所在城市
            
            返回:
                路线信息的JSON字符串
            """
            try:
                # 先搜索起点和终点的坐标
                origin_results = await self.map_service.search_attractions(
                    city=city, keyword=origin, limit=1
                )
                dest_results = await self.map_service.search_attractions(
                    city=city, keyword=destination, limit=1
                )
                
                if not origin_results or not dest_results:
                    return "无法找到起点或终点的位置信息"
                
                origin_poi = origin_results[0]
                dest_poi = dest_results[0]
                
                # 计算路线
                route = await self.map_service.get_route(
                    origin=(origin_poi['lng'], origin_poi['lat']),
                    destination=(dest_poi['lng'], dest_poi['lat']),
                    mode='walking'
                )
                
                import json
                return json.dumps({
                    "起点": origin_poi['name'],
                    "终点": dest_poi['name'],
                    "距离": f"{route['distance']/1000:.2f}公里",
                    "步行时间": f"{route['duration']/60:.0f}分钟",
                    "建议": "距离较近，建议步行" if route['distance'] < 2000 else "距离较远，建议乘车"
                }, ensure_ascii=False, indent=2)
                
            except Exception as e:
                return f"计算路线失败: {str(e)}"
        
        # 工具3：优化多个景点的游览顺序
        async def optimize_route_tool(attractions: List[str], city: str) -> str:
            """使用TSP算法优化多个景点的游览顺序
            
            参数:
                attractions: 景点名称列表
                city: 所在城市
            
            返回:
                优化后的顺序和总距离
            """
            try:
                # 搜索所有景点的坐标
                attractions_data = []
                for name in attractions:
                    results = await self.map_service.search_attractions(
                        city=city, keyword=name, limit=1
                    )
                    if results:
                        attractions_data.append(results[0])
                
                if len(attractions_data) < 2:
                    return "至少需要2个景点才能优化路线"
                
                # TSP优化
                optimized = await self.route_planner.optimize_route(attractions_data)
                
                # 格式化结果
                optimal_order = [a['name'] for a in optimized['attractions']]
                summary = optimized['summary']
                
                import json
                return json.dumps({
                    "优化前顺序": attractions,
                    "优化后顺序": optimal_order,
                    "总距离": f"{summary['total_distance_km']}公里",
                    "预计步行时间": f"{summary['total_duration_hours']*60:.0f}分钟",
                    "优化效果": f"节省{summary.get('optimization_rate', 0):.1f}%的路程" if summary.get('optimization_rate') else "首次优化"
                }, ensure_ascii=False, indent=2)
                
            except Exception as e:
                return f"优化路线失败: {str(e)}"
        
        # 工具4：获取城市信息
        async def get_city_info_tool(city: str) -> str:
            """获取城市的基本旅游信息
            
            参数:
                city: 城市名称
            
            返回:
                城市信息
            """
            # 搜索该城市的热门景点作为参考
            try:
                results = await self.map_service.search_attractions(
                    city=city, keyword="景点", limit=10
                )
                
                import json
                return json.dumps({
                    "城市": city,
                    "热门景点数量": len(results),
                    "推荐游玩天数": "3-5天" if len(results) > 15 else "2-3天",
                    "部分热门景点": [r['name'] for r in results[:5]]
                }, ensure_ascii=False, indent=2)
                
            except Exception as e:
                return f"获取城市信息失败: {str(e)}"
        
        # 返回工具列表
        return [
            StructuredTool.from_function(
                func=search_attractions_tool,
                name="search_attractions",
                description="搜索指定城市的景点。当用户询问某个城市有什么景点、想去某个地方玩、需要景点推荐时使用此工具。",
                args_schema=SearchAttractionInput,
                coroutine=search_attractions_tool
            ),
            StructuredTool.from_function(
                func=calculate_route_tool,
                name="calculate_route",
                description="计算两个地点之间的距离和路线。当需要知道两个景点之间有多远、怎么走、需要多长时间时使用。",
                args_schema=CalculateRouteInput,
                coroutine=calculate_route_tool
            ),
            StructuredTool.from_function(
                func=optimize_route_tool,
                name="optimize_route",
                description="优化多个景点的游览顺序，使用TSP算法找到最短路线。当有3个以上景点需要安排顺序、想知道最佳游览路线时使用。",
                args_schema=OptimizeRouteInput,
                coroutine=optimize_route_tool
            ),
            Tool(
                name="get_city_info",
                func=lambda city: get_city_info_tool(city),
                description="获取城市的基本旅游信息。当用户询问某个城市适合玩几天、有多少景点时使用。",
                coroutine=get_city_info_tool
            )
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """创建Agent执行器"""
        
        # Agent系统提示
        system_message = """你是一个专业的旅行规划助手，可以使用各种工具来帮助用户规划旅行。

你的能力：
1. 🔍 搜索景点 - 使用search_attractions工具搜索城市景点
2. 📏 计算路线 - 使用calculate_route工具计算两点距离
3. 🚀 优化顺序 - 使用optimize_route工具优化游览路线（TSP算法）
4. 🏙️ 城市信息 - 使用get_city_info工具了解城市概况

工作流程：
1. 理解用户需求（目的地、天数、偏好等）
2. 主动调用工具搜索景点信息
3. 根据工具返回的结果思考和规划
4. 可以多次调用工具来完善方案
5. 向用户展示完整的行程建议

注意事项：
- 优先使用工具获取真实数据，不要凭空编造景点
- 考虑景点之间的距离，合理安排顺序
- 每天安排2-4个景点，不要太累
- 提供具体的时间安排和游玩建议
- 计算费用预算（门票、交通、住宿、餐饮）

回复风格：
- 友好、专业、有条理
- 使用表格或列表清晰展示信息
- 给出理由和建议
- 询问用户是否满意，是否需要调整
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 创建Agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # 创建执行器
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            max_execution_time=120,
            return_intermediate_steps=True,
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    async def chat(self, user_input: str) -> Dict[str, Any]:
        """
        与Agent对话
        
        Args:
            user_input: 用户输入
            
        Returns:
            包含回复和中间步骤的字典
        """
        try:
            # 执行Agent
            result = await self.agent.ainvoke({
                "input": user_input,
                "chat_history": self.chat_history
            })
            
            # 更新对话历史
            self.chat_history.append(HumanMessage(content=user_input))
            self.chat_history.append(AIMessage(content=result['output']))
            
            # 限制历史长度
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]
            
            # 返回结果
            return {
                "reply": result['output'],
                "intermediate_steps": result.get('intermediate_steps', []),
                "tool_calls": self._format_tool_calls(result.get('intermediate_steps', []))
            }
            
        except Exception as e:
            return {
                "reply": f"抱歉，处理您的请求时出错了: {str(e)}",
                "intermediate_steps": [],
                "tool_calls": []
            }
    
    def _format_tool_calls(self, intermediate_steps: List) -> List[Dict]:
        """格式化工具调用记录"""
        tool_calls = []
        
        for step in intermediate_steps:
            if len(step) >= 2:
                action, observation = step[0], step[1]
                tool_calls.append({
                    "tool": action.tool,
                    "input": action.tool_input,
                    "output": observation[:200] + "..." if len(str(observation)) > 200 else observation
                })
        
        return tool_calls
    
    def reset_history(self):
        """重置对话历史"""
        self.chat_history = []


# 全局Agent实例
_agent_instance = None

def get_agent() -> TravelPlannerAgent:
    """获取Agent单例"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = TravelPlannerAgent()
    return _agent_instance

