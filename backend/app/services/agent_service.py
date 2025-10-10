"""
智能旅行规划Agent：可以主动调用工具的AI助手
类似MCP (Model Context Protocol) 的架构
"""
import asyncio
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool, StructuredTool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
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


class SearchHotelsInput(BaseModel):
    """搜索住宿输入"""
    city: str = Field(..., description="城市名称")
    location: str = Field("市中心", description="位置偏好，如：市中心、火车站附近")
    price_range: str = Field("经济型", description="价格档次：经济型/舒适型/豪华型")
    limit: int = Field(5, description="返回数量")


class GetWeatherInput(BaseModel):
    """获取天气输入"""
    city: str = Field(..., description="城市名称")


class SearchFoodInput(BaseModel):
    """搜索美食输入"""
    city: str = Field(..., description="城市名称")
    cuisine: str = Field("美食", description="美食类型，如：川菜、火锅、小吃")
    limit: int = Field(5, description="返回数量")


class TravelPlannerAgent:
    """旅行规划智能体"""
    
    def __init__(self):
        self.map_service = MapService()
        self.route_planner = RoutePlanner()
        
        # 初始化LLM - 使用优化的参数
        self.llm = ChatOpenAI(
            model=settings.DEEPSEEK_MODEL,
            openai_api_key=settings.DEEPSEEK_API_KEY,
            openai_api_base=settings.DEEPSEEK_API_BASE,
            temperature=settings.AI_TEMPERATURE_BALANCED,
            max_tokens=settings.AI_MAX_TOKENS,
            timeout=settings.AI_TIMEOUT,
            model_kwargs={"stream": False}
        )
        
        # 创建工具
        self.tools = self._create_tools()
        
        # 创建Agent
        self.agent = self._create_agent()
        
        # 对话历史
        self.chat_history = []
    
    async def _retry_tool_call(self, func, tool_name: str, max_retries: int = 2):
        """
        工具调用重试机制
        
        Args:
            func: 要执行的异步函数
            tool_name: 工具名称
            max_retries: 最大重试次数
            
        Returns:
            执行结果
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return await func()
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    delay = 1.0 * (2 ** attempt)  # 指数退避：1s, 2s, 4s
                    if settings.DEBUG_TOOLS:
                        print(f"[工具重试] {tool_name} 第{attempt + 1}次失败，{delay:.1f}秒后重试: {str(e)[:100]}")
                    await asyncio.sleep(delay)
                else:
                    if settings.DEBUG_TOOLS:
                        print(f"[工具重试] {tool_name} 达到最大重试次数({max_retries})，返回错误")
        
        return f"工具调用失败（已重试{max_retries}次）: {str(last_exception)}"
    
    def _create_tools(self) -> List[Tool]:
        """创建AI可以调用的工具"""
        
        # 工具1：搜索景点
        async def search_attractions_tool(city: str, keyword: str, limit: int = 5) -> str:
            """搜索指定城市的景点信息（带重试）
            
            参数:
                city: 城市名称
                keyword: 景点关键词
                limit: 返回数量
            
            返回:
                景点列表的JSON字符串
            """
            try:
                # 使用重试机制
                results = await self._retry_tool_call(
                    lambda: self.map_service.search_attractions(city=city, keyword=keyword, limit=limit),
                    tool_name="search_attractions"
                )
                
                # 检查返回结果
                if isinstance(results, str) and results.startswith("工具调用失败"):
                    return results  # 重试后仍失败，返回错误信息
                
                if not results:
                    return f"未找到'{keyword}'相关景点"
                
                # 格式化结果（包含照片信息）
                attractions_info = []
                for idx, attr in enumerate(results[:limit], 1):
                    info = {
                        "序号": idx,
                        "名称": attr['name'],
                        "地址": attr.get('address', '未知'),
                        "类型": attr.get('type', '未知'),
                        "评分": attr.get('rating', 0),
                        "坐标": f"({attr['lng']}, {attr['lat']})",
                        "照片": attr.get('photos', []),  # 所有照片URL列表
                        "缩略图": attr.get('thumbnail', '')  # 第一张照片作为缩略图
                    }
                    attractions_info.append(info)
                
                import json
                return json.dumps(attractions_info, ensure_ascii=False, indent=2)
                
            except Exception as e:
                return f"搜索失败: {str(e)}"
        
        # 工具2：智能路线规划（让AI决定交通方式）
        async def calculate_route_tool(origin: str, destination: str, city: str = None, mode: str = "auto") -> str:
            """计算两个地点之间的距离和路线（支持同城和跨城）
            
            参数:
                origin: 起点名称（城市名或景点名）
                destination: 终点名称（城市名或景点名）
                city: 所在城市（同城时必填，跨城时可选）
                mode: 交通方式 - "walking", "driving", "transit", "bicycling", "auto"
            
            返回:
                路线信息的JSON字符串，包含距离、时间、费用等
            """
            try:
                # 判断是否跨城市（origin或destination本身就是城市名）
                is_intercity = not city or origin != destination and (
                    len(origin) <= 4 and len(destination) <= 4  # 简单判断：短名称可能是城市
                )
                
                # 搜索起点和终点的坐标
                if is_intercity and not city:
                    # 跨城市：搜索火车站（更适合城际交通）
                    origin_results = await self.map_service.search_attractions_v5(
                        keywords=f"{origin}站",
                        region=origin,
                        types="150200",  # 火车站类型
                        city_limit=True,
                        page_size=1
                    )
                    # 如果没找到火车站，降级搜索城市地标
                    if not origin_results:
                        origin_results = await self.map_service.search_attractions(
                            city=origin, keyword=origin, limit=1
                        )
                    
                    dest_results = await self.map_service.search_attractions_v5(
                        keywords=f"{destination}站",
                        region=destination,
                        types="150200",  # 火车站类型
                        city_limit=True,
                        page_size=1
                    )
                    if not dest_results:
                        dest_results = await self.map_service.search_attractions(
                            city=destination, keyword=destination, limit=1
                        )
                else:
                    # 同城：在指定城市搜索景点
                    origin_results = await self.map_service.search_attractions(
                        city=city or origin, keyword=origin, limit=1
                    )
                    dest_results = await self.map_service.search_attractions(
                        city=city or destination, keyword=destination, limit=1
                    )
                
                if not origin_results or not dest_results:
                    return f"无法找到起点'{origin}'或终点'{destination}'的位置信息"
                
                origin_poi = origin_results[0]
                dest_poi = dest_results[0]
                origin_coords = (origin_poi['lng'], origin_poi['lat'])
                dest_coords = (dest_poi['lng'], dest_poi['lat'])
                
                # 计算直线距离以便AI参考
                straight_distance = self.map_service.calculate_distance(origin_coords, dest_coords)
                
                # 根据mode调用相应的API
                result_data = {
                    "起点": origin_poi['name'],
                    "终点": dest_poi['name'],
                    "直线距离": f"{straight_distance/1000:.2f}公里"
                }
                
                # 如果是auto模式，提供所有可能的交通方式供参考
                if mode == "auto":
                    modes_to_try = []
                    if straight_distance < 3000:
                        modes_to_try = ["walking"]
                    elif straight_distance < 15000:
                        modes_to_try = ["walking", "transit", "bicycling"]
                    else:
                        modes_to_try = ["driving", "transit"]
                    
                    result_data["建议"] = f"根据{straight_distance/1000:.1f}km的距离，建议使用: {', '.join(modes_to_try)}"
                    result_data["可选交通方式"] = ["walking", "driving", "transit", "bicycling"]
                    
                    import json
                    return json.dumps(result_data, ensure_ascii=False, indent=2)
                
                # 调用具体的交通方式API
                if mode == "walking":
                    route = await self.route_planner.route_service.get_walking_route(origin_coords, dest_coords)
                    if route:
                        result_data.update({
                            "交通方式": "步行",
                            "实际距离": f"{route['distance']/1000:.2f}公里",
                            "耗时": f"{route['duration']/60:.0f}分钟",
                            "费用": 0
                        })
                
                elif mode == "driving":
                    route = await self.route_planner.route_service.get_driving_route(origin_coords, dest_coords)
                    if route:
                        taxi_cost = route.get('taxi_cost', 0)
                        try:
                            taxi_cost = float(taxi_cost) if taxi_cost else 0
                        except:
                            taxi_cost = 0
                        if taxi_cost == 0:
                            km = route['distance'] / 1000
                            taxi_cost = 13 + km * 2.3
                        
                        result_data.update({
                            "交通方式": "出租车/驾车",
                            "实际距离": f"{route['distance']/1000:.2f}公里",
                            "耗时": f"{route['duration']/60:.0f}分钟",
                            "费用": f"{taxi_cost:.1f}元",
                            "过路费": f"{route.get('tolls', 0)}元",
                            "红绿灯": f"{route.get('traffic_lights', 0)}个"
                        })
                
                elif mode == "transit":
                    from app.core.city_mapping import get_citycode
                    
                    # 判断起终点城市
                    origin_city = origin_poi.get('city', city or origin)
                    dest_city = dest_poi.get('city', city or destination)
                    
                    # 获取城市码（跨城市时使用各自的城市码）
                    if origin_city and dest_city:
                        city_code1 = get_citycode(origin_city)
                        city_code2 = get_citycode(dest_city)
                    else:
                        # 同城或无法判断时，尝试使用传入的city参数
                        city_code1 = get_citycode(city) if city else "010"
                        city_code2 = city_code1
                    
                    print(f"[Transit] {origin_city}({city_code1}) → {dest_city}({city_code2})")
                    
                    route = await self.route_planner.route_service.get_transit_route(
                        origin_coords, dest_coords, city1=city_code1, city2=city_code2
                    )
                    if route and route.get('plans'):
                        plan = route['plans'][0]
                        
                        # 判断是否跨城市（城市码不同则是跨城）
                        is_intercity = city_code1 != city_code2
                        transport_label = "高铁/城际" if is_intercity else "公交/地铁"
                        
                        result_data.update({
                            "交通方式": transport_label,
                            "实际距离": f"{plan['distance']/1000:.2f}公里",
                            "耗时": f"{plan['duration']/60:.0f}分钟",
                            "费用": f"{plan.get('transit_fee', 3)}元",
                            "换乘次数": len(plan.get('segments', [])) - 1,
                            "起点城市": origin_city,
                            "终点城市": dest_city
                        })
                
                elif mode == "bicycling":
                    route = await self.route_planner.route_service.get_bicycling_route(origin_coords, dest_coords)
                    if route:
                        result_data.update({
                            "交通方式": "骑行",
                            "实际距离": f"{route['distance']/1000:.2f}公里",
                            "耗时": f"{route['duration']/60:.0f}分钟",
                            "费用": 0
                        })
                
                import json
                return json.dumps(result_data, ensure_ascii=False, indent=2)
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                return f"计算路线失败: {str(e)}"
        
        # 工具3：优化多个景点的游览顺序（仅优化顺序，不规划详细路线）
        async def optimize_route_tool(attractions: List[str], city: str) -> str:
            """使用TSP算法优化多个景点的游览顺序（返回最优顺序和相邻景点间的直线距离）
            
            参数:
                attractions: 景点名称列表
                city: 所在城市
            
            返回:
                优化后的顺序和相邻景点间距离（后续需要用calculate_route规划具体交通方式）
            """
            try:
                # 限制景点数量，避免过多POI查询消耗迭代次数
                if len(attractions) > 6:
                    if settings.DEBUG_TOOLS:
                        print(f"[optimize_route] 景点数量过多({len(attractions)})，仅优化前6个")
                    attractions = attractions[:6]
                
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
                
                # 使用TSP算法优化顺序（基于直线距离）
                from ortools.constraint_solver import routing_enums_pb2, pywrapcp
                
                # 计算距离矩阵
                n = len(attractions_data)
                distance_matrix = [[0] * n for _ in range(n)]
                
                for i in range(n):
                    for j in range(n):
                        if i != j:
                            dist = self.map_service.calculate_distance(
                                (attractions_data[i]['lng'], attractions_data[i]['lat']),
                                (attractions_data[j]['lng'], attractions_data[j]['lat'])
                            )
                            distance_matrix[i][j] = int(dist)
                
                # 创建路由模型
                manager = pywrapcp.RoutingIndexManager(n, 1, 0)
                routing = pywrapcp.RoutingModel(manager)
                
                def distance_callback(from_index, to_index):
                    from_node = manager.IndexToNode(from_index)
                    to_node = manager.IndexToNode(to_index)
                    return distance_matrix[from_node][to_node]
                
                transit_callback_index = routing.RegisterTransitCallback(distance_callback)
                routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
                
                search_parameters = pywrapcp.DefaultRoutingSearchParameters()
                search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
                search_parameters.time_limit.seconds = 10
                
                solution = routing.SolveWithParameters(search_parameters)
                
                if solution:
                    # 提取优化后的顺序
                    index = routing.Start(0)
                    optimal_order = []
                    route_segments = []
                    
                    while not routing.IsEnd(index):
                        node = manager.IndexToNode(index)
                        optimal_order.append(attractions_data[node]['name'])
                        
                        next_index = solution.Value(routing.NextVar(index))
                        if not routing.IsEnd(next_index):
                            next_node = manager.IndexToNode(next_index)
                            segment_distance = distance_matrix[node][next_node] / 1000  # 转为公里
                            route_segments.append({
                                "从": attractions_data[node]['name'],
                                "到": attractions_data[next_node]['name'],
                                "直线距离": f"{segment_distance:.1f}km"
                            })
                        
                        index = next_index
                    
                    import json
                    return json.dumps({
                        "优化后顺序": optimal_order,
                        "相邻景点间距离": route_segments,
                        "总直线距离": f"{solution.ObjectiveValue()/1000:.1f}公里",
                        "提示": "请使用 calculate_route 工具为每个路段规划具体交通方式"
                    }, ensure_ascii=False, indent=2)
                else:
                    return "TSP优化失败，请检查景点数据"
                
            except Exception as e:
                import traceback
                traceback.print_exc()
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
        
        # 工具5：搜索住宿
        async def search_hotels_tool(city: str, location: str = "市中心", price_range: str = "经济型", limit: int = 5) -> str:
            """搜索指定城市的酒店住宿
            
            参数:
                city: 城市名称
                location: 位置偏好
                price_range: 价格档次
                limit: 返回数量
            
            返回:
                酒店列表
            """
            try:
                # 搜索酒店POI
                results = await self.map_service.search_attractions_v5(
                    keywords=f"{location} 酒店",
                    region=city,
                    types="100000",  # 酒店类型
                    city_limit=True,
                    page_size=limit
                )
                
                if not results:
                    return f"未找到{city}{location}的酒店"
                
                hotels_info = []
                for idx, hotel in enumerate(results[:limit], 1):
                    info = {
                        "序号": idx,
                        "名称": hotel['name'],
                        "地址": hotel.get('address', '未知'),
                        "价格": hotel.get('cost', '未知'),
                        "电话": hotel.get('tel', '未知')
                    }
                    hotels_info.append(info)
                
                import json
                return json.dumps(hotels_info, ensure_ascii=False, indent=2)
                
            except Exception as e:
                return f"搜索酒店失败: {str(e)}"
        
        # 工具6：批量获取天气预报（并行查询，速度快3倍）
        async def get_multi_weather_tool(cities: List[str]) -> str:
            """批量获取多个城市的天气预报（并行查询，提升速度）
            
            参数:
                cities: 城市名称列表（最多5个）
            
            返回:
                多个城市的天气信息
            """
            try:
                import asyncio
                
                # 限制最多5个城市
                if len(cities) > 5:
                    print(f"[批量天气] 城市数量过多({len(cities)})，仅查询前5个")
                    cities = cities[:5]
                
                if settings.DEBUG_TOOLS:
                    print(f"[批量天气] 并行查询: {cities}")
                
                # 并行查询所有城市（每个都带重试）
                async def get_weather_with_retry(city):
                    return await self._retry_tool_call(
                        lambda: self.map_service.get_weather(city),
                        tool_name=f"get_weather[{city}]",
                        max_retries=2
                    )
                
                tasks = [get_weather_with_retry(city) for city in cities]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                all_weather = {}
                for city, weather_data in zip(cities, results):
                    if weather_data and not isinstance(weather_data, Exception):
                        forecasts = weather_data.get('forecasts', [])[:3]
                        all_weather[city] = {
                            "城市": weather_data.get('city', city),
                            "未来3天天气": [
                                {
                                    "日期": f.get('date'),
                                    "星期": f.get('week'),
                                    "天气": f"{f.get('day_weather')}转{f.get('night_weather')}",
                                    "温度": f"{f.get('night_temp')}~{f.get('day_temp')}°C",
                                    "风力": f"{f.get('day_wind')}{f.get('day_power')}级"
                                }
                                for f in forecasts
                            ]
                        }
                    elif isinstance(weather_data, Exception):
                        if settings.DEBUG_TOOLS:
                            print(f"[批量天气] {city}查询失败: {weather_data}")
                        all_weather[city] = {"错误": str(weather_data)}
                
                if not all_weather:
                    return "所有城市的天气信息都获取失败"
                
                import json
                return json.dumps(all_weather, ensure_ascii=False, indent=2)
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                return f"批量获取天气失败: {str(e)}"
        
        # 工具6B：单个城市天气查询（兼容旧用法）
        async def get_weather_tool(city: str) -> str:
            """获取单个城市的天气预报
            
            参数:
                city: 城市名称
            
            返回:
                天气预报信息
            """
            try:
                weather = await self.map_service.get_weather(city)
                
                if not weather:
                    return f"无法获取{city}的天气信息"
                
                forecasts = weather.get('forecasts', [])[:3]
                weather_info = {
                    "城市": weather.get('city', city),
                    "未来3天天气": [
                        {
                            "日期": f.get('date'),
                            "星期": f.get('week'),
                            "天气": f"{f.get('day_weather')}转{f.get('night_weather')}",
                            "温度": f"{f.get('night_temp')}~{f.get('day_temp')}°C",
                            "风力": f"{f.get('day_wind')}{f.get('day_power')}级"
                        }
                        for f in forecasts
                    ]
                }
                
                import json
                return json.dumps(weather_info, ensure_ascii=False, indent=2)
                
            except Exception as e:
                return f"获取天气失败: {str(e)}"
        
        # 工具7：搜索美食
        async def search_food_tool(city: str, cuisine: str = "美食", limit: int = 5) -> str:
            """搜索指定城市的特色美食
            
            参数:
                city: 城市名称
                cuisine: 美食类型
                limit: 返回数量
            
            返回:
                美食推荐列表
            """
            try:
                # 搜索餐饮POI
                results = await self.map_service.search_attractions_v5(
                    keywords=cuisine,
                    region=city,
                    types="050000",  # 餐饮服务
                    city_limit=True,
                    page_size=limit
                )
                
                if not results:
                    return f"未找到{city}的{cuisine}"
                
                food_info = []
                for idx, restaurant in enumerate(results[:limit], 1):
                    info = {
                        "序号": idx,
                        "名称": restaurant['name'],
                        "地址": restaurant.get('address', '未知'),
                        "评分": restaurant.get('rating', 0),
                        "人均": restaurant.get('cost', '未知'),
                        "电话": restaurant.get('tel', '未知')
                    }
                    food_info.append(info)
                
                import json
                return json.dumps(food_info, ensure_ascii=False, indent=2)
                
            except Exception as e:
                return f"搜索美食失败: {str(e)}"
        
        # 包装工具以处理JSON字符串输入（ReAct模式需要）
        import json as json_module
        
        async def wrapped_search_attractions(tool_input: str) -> str:
            """包装景点搜索工具"""
            try:
                params = json_module.loads(tool_input) if isinstance(tool_input, str) else tool_input
                return await search_attractions_tool(**params)
            except Exception as e:
                return f"参数解析错误: {str(e)}, 输入: {tool_input}"
        
        async def wrapped_calculate_route(tool_input: str) -> str:
            """包装路线计算工具"""
            try:
                params = json_module.loads(tool_input) if isinstance(tool_input, str) else tool_input
                # 设置默认mode
                if 'mode' not in params:
                    params['mode'] = 'auto'
                return await calculate_route_tool(**params)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return f"参数解析错误: {str(e)}, 输入: {tool_input}"
        
        async def wrapped_optimize_route(tool_input: str) -> str:
            """包装路线优化工具"""
            try:
                params = json_module.loads(tool_input) if isinstance(tool_input, str) else tool_input
                return await optimize_route_tool(**params)
            except Exception as e:
                return f"参数解析错误: {str(e)}"
        
        async def wrapped_get_weather(tool_input: str) -> str:
            """包装天气工具"""
            try:
                params = json_module.loads(tool_input) if isinstance(tool_input, str) else tool_input
                city = params.get('city', params) if isinstance(params, dict) else params
                return await get_weather_tool(city)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return f"参数解析错误: {str(e)}, 输入: {tool_input}"
        
        async def wrapped_get_multi_weather(tool_input: str) -> str:
            """包装批量天气工具"""
            try:
                params = json_module.loads(tool_input) if isinstance(tool_input, str) else tool_input
                cities = params.get('cities', params) if isinstance(params, dict) else params
                # 确保cities是列表
                if isinstance(cities, str):
                    cities = [cities]
                return await get_multi_weather_tool(cities)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return f"参数解析错误: {str(e)}, 输入: {tool_input}"
        
        async def wrapped_search_hotels(tool_input: str) -> str:
            """包装酒店搜索工具"""
            try:
                params = json_module.loads(tool_input) if isinstance(tool_input, str) else tool_input
                return await search_hotels_tool(**params)
            except Exception as e:
                return f"参数解析错误: {str(e)}"
        
        async def wrapped_search_food(tool_input: str) -> str:
            """包装美食搜索工具"""
            try:
                params = json_module.loads(tool_input) if isinstance(tool_input, str) else tool_input
                return await search_food_tool(**params)
            except Exception as e:
                return f"参数解析错误: {str(e)}"
        
        # 返回工具列表（使用简单的Tool类，适配ReAct模式）
        return [
            Tool(
                name="search_attractions",
                func=wrapped_search_attractions,
                description='搜索景点。输入JSON，例：{{"city": "北京", "keyword": "故宫", "limit": 5}}',
                coroutine=wrapped_search_attractions
            ),
            Tool(
                name="calculate_route",
                func=wrapped_calculate_route,
                description='计算路线，支持同城和跨城。输入JSON，例：同城{{"origin": "芙蓉街", "destination": "大明湖", "city": "济南", "mode": "auto"}}，跨城{{"origin": "济南", "destination": "青岛", "mode": "transit"}}。mode可选：auto/walking/driving/transit/bicycling。',
                coroutine=wrapped_calculate_route
            ),
            Tool(
                name="optimize_route",
                func=wrapped_optimize_route,
                description='优化景点顺序（TSP算法）。输入JSON，例：{{"attractions": ["景点A", "景点B"], "city": "济南"}}。只返回优化顺序，需再用calculate_route规划交通。',
                coroutine=wrapped_optimize_route
            ),
            Tool(
                name="get_city_info",
                func=lambda city: get_city_info_tool(city),
                description="获取城市信息。输入：城市名称字符串",
                coroutine=get_city_info_tool
            ),
            Tool(
                name="search_hotels",
                func=wrapped_search_hotels,
                description='搜索住宿。输入JSON，例：{{"city": "济南", "location": "市中心", "price_range": "经济型", "limit": 3}}',
                coroutine=wrapped_search_hotels
            ),
            Tool(
                name="get_weather",
                func=wrapped_get_weather,
                description='获取单个城市天气。输入JSON，例：{{"city": "济南"}}',
                coroutine=wrapped_get_weather
            ),
            Tool(
                name="get_multi_weather",
                func=wrapped_get_multi_weather,
                description='批量获取多城市天气（并行查询，推荐）。输入JSON，例：{{"cities": ["济南", "青岛", "淄博"]}}。速度快3倍。',
                coroutine=wrapped_get_multi_weather
            ),
            Tool(
                name="search_food",
                func=wrapped_search_food,
                description='搜索美食。输入JSON，例：{{"city": "济南", "cuisine": "鲁菜", "limit": 3}}',
                coroutine=wrapped_search_food
            )
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """创建Agent执行器（使用ReAct模式）"""
        
        # ReAct风格的提示词模板
        template = """你是专业旅行规划助手，拥有强大的工具，能基于真实数据规划行程。

你必须使用以下工具来获取真实数据：

{tools}

使用以下格式进行思考和行动：

Question: 用户的问题
Thought: 我需要思考该怎么做
Action: 要使用的工具名称，必须是 [{tool_names}] 中的一个
Action Input: 工具的输入参数（JSON格式）
Observation: 工具返回的结果
... (这个Thought/Action/Action Input/Observation可以重复多次)
Thought: 我现在知道最终答案了
Final Answer: 给用户的最终回复

💡 **高效工作流程**（必须严格遵守，避免超时）：

🚨 **关键原则：工具调用要少而精，避免重复搜索！**

1️⃣ 查询天气（1次）：
   ✅ 必须使用 get_multi_weather 批量查询所有城市
      示例: get_multi_weather({{"cities": ["济南", "青岛", "淄博"]}})
   ❌ 禁止：多次调用get_weather单独查询
   
2️⃣ 搜索景点（每城市最多1次）：
   ⚠️ **景点数量严格控制**：
   - 单城市3天：搜索1次，取6-9个景点即可（每天2-3个）
   - 多城市行程：每个城市搜索1次，按天数分配
   - **禁止重复搜索**：不要用不同关键词反复搜索同一城市
   
   ⚠️ **地理位置严格要求**（最重要！）：
   - 🎯 **观察坐标选景点**：必须看搜索结果的经纬度，选择坐标接近的（经度或纬度相差<0.05度）
   - 🚫 **绝对禁止偏远景点**：
     * 济南市区：117.0±0.05, 36.66±0.05（趵突泉、大明湖、千佛山区域）
     * 淄博周村：117.84±0.03, 36.80±0.03（周村古商城附近）
     * 青岛市南区：120.32±0.05, 36.06±0.05（栈桥、八大关区域）
   - ❌ **必须过滤掉**：
     * 友谊葫芦、万德文化中心（远郊，距市区50km+）
     * 热带鱼林（不知名小景点）
     * 绿野仙踪文化（远郊）
   - ✅ **只选热门核心景点**：评分4.5+，且在市区核心区域
   
   ⚠️ **多城市行程规划**：
   - 城市之间要有明确的先后顺序，不要来回跑
   - 例如：济南2天→淄博2天→青岛3天（顺序游玩）
   - **禁止**：济南→青岛→济南→淄博（来回跑）
   
3️⃣ 优化顺序（可选）：
   - 只有当同城景点≥3个时才使用optimize_route
   - 跨城市的景点绝对不要一起优化
   
4️⃣ 规划交通（仅关键路段）：
   - 跨城市：必须规划1次（如济南→淄博）
   - 同城：距离>10km时规划
   - **禁止**：为每个相邻景点都计算路线（浪费工具调用）
   
5️⃣ 搜索配套（每城市各1次）：
   - search_hotels：每城市1次
   - search_food：每城市1次
   - **禁止重复搜索**

🎯 **工具调用预算**（超过就会超时）：
- 3天单城市：≤12次工具调用
- 5天双城市：≤18次工具调用  
- 7天三城市：≤25次工具调用

🚗 **交通方式选择建议**：
- <2km: walking（步行，0元）
- 2-10km: transit（公交/地铁，2-5元）或 bicycling（骑行，0元）
- 10-50km: driving（出租车，约30-130元）或 transit（地铁，约5元）
- >50km跨城: transit（高铁），费用约0.45元/km，耗时约150km/h
  例：济南→青岛300km，高铁约135元，2小时

💰 **预算分配标准**（根据总预算合理分配）：
假设总预算B元，游玩D天，N个城市：
- 交通费：B × (0.35-0.45)，跨城市多则占比高
  * 同城游：B × 0.25（主要是市内交通）
  * 2-3城市：B × 0.35（含1-2次城际高铁）
  * 4+城市：B × 0.45（多次城际高铁）
- 住宿费：B × 0.30-0.35，约 B/(D×3) 元/晚
  * 预算紧张：150-200元/晚（经济型连锁酒店）
  * 预算宽裕：250-350元/晚（中档酒店）
- 餐饮费：B × 0.20-0.25，约 B/(D×15) 元/餐
  * 早餐：15-25元（快餐/小吃）
  * 午餐：30-50元（特色美食）
  * 晚餐：40-70元（正餐）
- 门票费：B × 0.10-0.15
  * 优先选择免费景点（公园、广场、古城）
  * 控制付费景点数量（每天1-2个）
- 应急备用：B × 0.05（用于意外支出）

💡 **预算优化技巧**：
- 预算紧张时：多选免费景点、住青旅/经济连锁、多吃小吃/快餐、市内多用公交
- 预算充裕时：可选高评分景点、住中档酒店、尝试特色餐厅、适当打车

⚠️ **景点规划要求**（最重要，必须严格遵守！）：

🎯 **核心原则**：只选市区核心景点，绝不选偏远景点！

1. **景点数量**：每天2-3个景点（严格上限）
2. **地理位置**：必须观察坐标，选择经纬度接近的景点（相差<0.05度）
3. **距离控制**：景点间直线距离<3km，绝不超过5km
4. **评分要求**：优先4.5+评分，过滤0分或低分景点
5. **必须过滤掉的偏远景点**：
   - ❌ 友谊葫芦非遗文化产业园（117.536075, 36.622176）距市区46km
   - ❌ 万德文化中心（116.920241, 36.33788）距市区63km
   - ❌ 热带鱼林高端水族文化馆（117.156335, 37.299244）距市区72km
   - ❌ 玄霆司民俗文创体验馆（117.857969, 36.814306）0分小景点
   - ❌ 绿野仙踪文化（120.422658, 36.098227）远郊景点
6. **只选核心景区**：
   - ✅ 济南：趵突泉(117.015893, 36.661087)、大明湖、千佛山、芙蓉街
   - ✅ 淄博：周村古商城(117.841013, 36.798378)及其内部景点
   - ✅ 青岛：栈桥(120.320444, 36.058475)、八大关、信号山、德国建筑群

⚠️ **时间规划标准**（必须严格遵守）：
- 🌅 上午第1个景点：start_time="09:00", duration_hours=2.5
- 🍜 午餐时间：12:00-13:30（不在景点列表中）
- ☀️ 下午第2个景点：start_time="13:30", duration_hours=2.5
- 🍽️ 晚餐时间：18:00-19:30（不在景点列表中）
- 🌙 晚上第3个景点（可选）：start_time="19:30", duration_hours=1.5

**重要**：
- 每个景点必须有不同的start_time，不能都是09:00
- duration_hours根据景点类型：大景区2.5-3小时，小景点1.5-2小时

⚠️ **输出要求**：
Final Answer必须包含两部分：
1. 详细的行程规划文本（包含每天的时间表）
2. JSON格式的结构化数据（在文本末尾）

JSON格式示例（必须严格遵守）：
```json
{{
  "destination": "目的地城市",
  "days": 天数,
  "daily_schedule": [
    {{
      "day": 1,
      "city": "当天所在城市",
      "theme": "当天主题（如：泉城文化游）",
      "attractions": [
        {{"name": "景点名", "address": "地址", "lng": 经度, "lat": 纬度, "cost": 门票, "rating": 评分, "start_time": "09:00", "duration_hours": 2}}
      ],
      "hotel": {{"name": "酒店名", "address": "地址", "lng": 经度, "lat": 纬度, "price_per_night": 价格}},
      "transportation": [{{"from_location": "起点", "to_location": "终点", "type": "交通方式", "cost": 费用, "distance": "距离", "duration": "时长"}}]
    }}
  ],
  "cost_breakdown": {{"transportation": 交通费, "accommodation": 住宿费, "food": 餐饮费, "tickets": 门票费, "total": 总计}}
}}
```

现在开始！

Question: {input}
Thought:{agent_scratchpad}"""
        
        prompt = PromptTemplate.from_template(template)
        
        # 创建ReAct Agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # 创建执行器
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=200,  # 提高到200次（支持复杂多城市规划）
            max_execution_time=240,  # 增加到4分钟（给Agent充足时间）
            return_intermediate_steps=True,
            handle_parsing_errors=True
            # 不设置early_stopping_method，让Agent自然完成
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
            # 动态计算max_iterations
            max_iterations = self._estimate_max_iterations(user_input)
            
            # 临时调整Agent的max_iterations
            original_max_iterations = self.agent.max_iterations
            self.agent.max_iterations = max_iterations
            
            # 执行Agent（ReAct不需要chat_history）
            result = await self.agent.ainvoke({
                "input": user_input
            })
            
            # 恢复原始设置
            self.agent.max_iterations = original_max_iterations
            
            # 更新对话历史（仅用于记录）
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
            import traceback
            traceback.print_exc()
            return {
                "reply": f"抱歉，处理您的请求时出错了: {str(e)}",
                "intermediate_steps": [],
                "tool_calls": []
            }
    
    def _estimate_max_iterations(self, user_input: str) -> int:
        """
        根据用户输入估算所需的max_iterations
        
        Args:
            user_input: 用户输入
            
        Returns:
            建议的max_iterations值
        """
        import re
        
        # 基础迭代次数（约5次工具调用）
        base_iterations = 10
        
        # 提取城市数量（常见关键词：去、到、游、玩）
        cities = re.findall(r'([北上广深成都杭州西安南京武汉重庆天津青岛大连厦门苏州长沙郑州济南哈尔滨沈阳昆明贵阳南昌福州石家庄太原兰州银川西宁乌鲁木齐拉萨呼和浩特南宁海口香港澳门台北高雄等][\u4e00-\u9fa5]{0,3}?(?:市|地区)?)', user_input)
        city_count = len(set(cities)) if cities else 1
        
        # 提取天数
        days_match = re.search(r'(\d+)\s*天', user_input)
        days = int(days_match.group(1)) if days_match else 3
        
        # 计算公式：基础 + 城市数*8 + 天数*3（优化后每天景点少，工具调用减少）
        estimated_tools = base_iterations + city_count * 8 + days * 3
        
        # 如果是多城市行程，额外增加路线优化和跨城交通的预留
        if city_count >= 3:
            estimated_tools += 15  # 多城市规划
        elif city_count >= 2:
            estimated_tools += 8  # 双城规划
        
        # 每次工具调用需要约3次迭代（Thought + Action + Parse）
        # 给予更大的安全边际（实际测试发现Agent需要更多尝试空间）
        max_iterations = int(estimated_tools * 3 * 2)
        
        # 设置上下限（进一步提高上限，确保复杂任务能完成）
        max_iterations = max(80, min(max_iterations, 300))
        
        print(f"[Agent] 任务分析: {city_count}个城市, {days}天")
        print(f"[Agent] 预估工具调用: {estimated_tools}次")
        print(f"[Agent] 设置max_iterations: {max_iterations}")
        
        return max_iterations
    
    async def chat_stream(self, user_input: str):
        """
        与Agent流式对话（实时显示工具调用过程）
        
        Args:
            user_input: 用户输入
            
        Yields:
            流式事件（工具调用、思考过程、最终回复）
        """
        import json
        
        try:
            if settings.DEBUG_AGENT:
                print(f"[Agent Stream] 开始执行，输入: {user_input[:50]}")
            
            # 发送初始消息
            yield {
                "type": "start",
                "content": "🤖 Agent开始执行..."
            }
            
            # 动态计算max_iterations
            max_iterations = self._estimate_max_iterations(user_input)
            
            # 临时调整Agent的max_iterations
            original_max_iterations = self.agent.max_iterations
            print(f"[Agent] 原始max_iterations: {original_max_iterations}")
            self.agent.max_iterations = max_iterations
            print(f"[Agent] 动态调整后max_iterations: {self.agent.max_iterations}")
            print(f"[Agent] 超时时间: {self.agent.max_execution_time}秒")
            
            # 执行Agent（ReAct不需要chat_history）
            import time
            start_time = time.time()
            
            result = await self.agent.ainvoke({
                "input": user_input
            })
            
            execution_time = time.time() - start_time
            
            # 恢复原始设置
            self.agent.max_iterations = original_max_iterations
            
            print(f"[Agent Stream] Agent执行完成")
            print(f"[Agent Stream] 实际执行时间: {execution_time:.1f}秒")
            print(f"[Agent Stream] 超时限制: {settings.AI_TIMEOUT}秒")
            print(f"[Agent Stream] 使用的max_iterations: {max_iterations}")
            
            # 显示工具调用记录
            intermediate_steps = result.get('intermediate_steps', [])
            print(f"[Agent Stream] 实际工具调用次数: {len(intermediate_steps)}")
            print(f"[Agent Stream] 预估需要: {len(intermediate_steps) * 2}次迭代（实际可能更多）")
            if settings.DEBUG_AGENT:
                print(f"[Agent Stream] 中间步骤数量: {len(intermediate_steps)}")
            
            if len(intermediate_steps) == 0:
                if settings.DEBUG_AGENT:
                    print("[Agent Stream] ⚠️ 警告：没有调用任何工具！")
                    print(f"[Agent Stream] 原始输出: {result.get('output', '')[:200]}")
            
            for step in intermediate_steps:
                if len(step) >= 2:
                    action, observation = step[0], step[1]
                    tool_name = action.tool
                    tool_input = action.tool_input
                    
                    if settings.DEBUG_TOOLS:
                        print(f"[工具调用] {tool_name} - 输入: {tool_input}")
                    
                    # 工具调用开始
                    yield {
                        "type": "tool_start",
                        "tool": tool_name,
                        "input": tool_input,
                        "content": f"🔧 调用工具：{tool_name}"
                    }
                    
                    # 短暂延迟，让前端能看清
                    await asyncio.sleep(0.1)
                    
                    # 工具调用完成
                    output_preview = str(observation)[:200] + '...' if len(str(observation)) > 200 else str(observation)
                    yield {
                        "type": "tool_end",
                        "tool": tool_name,
                        "output": output_preview,
                        "content": f"✅ {tool_name} 完成"
                    }
                    
                    await asyncio.sleep(0.1)
            
            # 最终回复（分段发送，模拟流式）
            final_output = result.get('output', '')
            print(f"[Agent Stream] 最终输出长度: {len(final_output)}")
            
            # 检查是否因为迭代限制而停止
            if "Agent stopped" in final_output or len(final_output) < 100:
                print(f"[Agent Stream] ⚠️ Agent提前停止！")
                print(f"[Agent Stream] 输出内容: {final_output}")
            
            # 自动构建行程JSON（基于工具调用结果）
            itinerary_json = self._build_itinerary_from_steps(intermediate_steps, user_input)
            
            if itinerary_json:
                print(f"[Agent Stream] 成功构建行程JSON: {len(itinerary_json.get('daily_schedule', []))}天")
            else:
                print(f"[Agent Stream] 未能构建行程JSON")
            
            # 分段发送文本（每50个字符）
            for i in range(0, len(final_output), 50):
                chunk = final_output[i:i+50]
                yield {
                    "type": "llm_stream",
                    "content": chunk
                }
                await asyncio.sleep(0.05)
            
            # 如果提取到了JSON，发送itinerary事件
            if itinerary_json:
                yield {
                    "type": "itinerary",
                    "data": itinerary_json
                }
            
            # 更新对话历史（仅用于记录）
            self.chat_history.append(HumanMessage(content=user_input))
            self.chat_history.append(AIMessage(content=final_output))
            
            # 限制历史长度
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]
            
            yield {
                "type": "done",
                "content": "✅ 完成"
            }
            
        except Exception as e:
            import traceback
            print(f"[Agent Stream] 异常: {e}")
            traceback.print_exc()
            yield {
                "type": "error",
                "content": f"❌ Agent执行失败: {str(e)}"
            }
    
    def _build_itinerary_from_steps(self, intermediate_steps: List, user_input: str) -> Optional[Dict]:
        """
        从工具调用结果构建结构化行程JSON
        
        Args:
            intermediate_steps: Agent的工具调用记录
            user_input: 用户输入（用于提取目的地和天数）
            
        Returns:
            结构化行程JSON
        """
        try:
            import re
            import json as json_module
            
            # 提取目的地和天数
            cities_match = re.findall(r'([北上广深成都杭州西安南京武汉重庆天津青岛大连厦门苏州长沙郑州济南哈尔滨沈阳昆明贵阳南昌福州石家庄太原兰州银川西宁乌鲁木齐拉萨呼和浩特南宁海口香港澳门台北高雄淄博中山等][\u4e00-\u9fa5]{0,3})', user_input)
            days_match = re.search(r'(\d+)\s*天', user_input)
            
            destination = cities_match[0] if cities_match else "目的地"
            days = int(days_match.group(1)) if days_match else 3
            
            # 收集所有工具调用结果
            all_attractions = []
            all_hotels = []
            all_routes = []
            
            for step in intermediate_steps:
                if len(step) >= 2:
                    action, observation = step[0], step[1]
                    tool_name = action.tool
                    
                    try:
                        # 解析工具输出
                        if isinstance(observation, str) and observation.strip().startswith('['):
                            data = json_module.loads(observation)
                            
                            if tool_name == "search_attractions" and isinstance(data, list):
                                for item in data:
                                    if '坐标' in item:
                                        coord_str = item['坐标'].strip('()')
                                        coords = coord_str.split(',')
                                        
                                        # 提取照片信息
                                        photos = item.get('照片', [])
                                        thumbnail = item.get('缩略图', '')
                                        
                                        # 确保photos是列表
                                        if not isinstance(photos, list):
                                            photos = []
                                        
                                        # 如果有照片但没有缩略图，使用第一张作为缩略图
                                        if photos and not thumbnail:
                                            thumbnail = photos[0]
                                        
                                        # 根据景点在当天的位置分配时间
                                        # 简单策略：上午09:00，下午13:30，晚上19:30
                                        time_slots = ["09:00", "13:30", "19:30"]
                                        attraction_index = len([a for a in all_attractions if a.get('day') == len(all_attractions) // (days or 1) + 1])
                                        start_time = time_slots[min(attraction_index, 2)]
                                        
                                        all_attractions.append({
                                            "name": item.get('名称', ''),
                                            "address": item.get('地址', ''),
                                            "lng": float(coords[0].strip()) if len(coords) > 0 else 0,
                                            "lat": float(coords[1].strip()) if len(coords) > 1 else 0,
                                            "cost": 0,
                                            "rating": item.get('评分', 0),
                                            "type": item.get('类型', ''),
                                            "start_time": start_time,  # 动态分配时间
                                            "duration_hours": 2.5,
                                            "photos": photos,  # 所有照片URL列表
                                            "thumbnail": thumbnail  # 缩略图URL
                                        })
                            
                            elif tool_name == "search_hotels" and isinstance(data, list):
                                for item in data:
                                    all_hotels.append({
                                        "name": item.get('名称', ''),
                                        "address": item.get('地址', ''),
                                        "lng": 0,
                                        "lat": 0,
                                        "price_per_night": 200,
                                        "rating": item.get('评分', 0) if '评分' in item else 0
                                    })
                    except:
                        pass
            
            # 如果没有收集到数据，返回None
            if not all_attractions:
                return None
            
            # 按天数分配景点
            attractions_per_day = max(1, len(all_attractions) // days)
            daily_schedule = []
            
            for day in range(1, days + 1):
                start_idx = (day - 1) * attractions_per_day
                end_idx = start_idx + attractions_per_day if day < days else len(all_attractions)
                day_attractions = all_attractions[start_idx:end_idx]
                
                # 为当天的景点重新分配时间
                time_slots = ["09:00", "13:30", "19:30"]
                for idx, attr in enumerate(day_attractions):
                    attr['start_time'] = time_slots[min(idx, 2)]
                    # 大景区2.5小时，小景点1.5-2小时
                    attr['duration_hours'] = 2.5 if idx < 2 else 1.5
                
                # 分配酒店
                hotel_idx = min(day - 1, len(all_hotels) - 1) if all_hotels else 0
                day_hotel = all_hotels[hotel_idx] if all_hotels and hotel_idx < len(all_hotels) else {
                    "name": f"待定酒店",
                    "address": "",
                    "lng": 0,
                    "lat": 0,
                    "price_per_night": 200
                }
                
                daily_schedule.append({
                    "day": day,
                    "attractions": day_attractions,
                    "hotel": day_hotel,
                    "transportation": []
                })
            
            return {
                "destination": destination,
                "days": days,
                "daily_schedule": daily_schedule,
                "cost_breakdown": {
                    "transportation": 0,
                    "accommodation": len(all_hotels) * 200,
                    "food": days * 100,
                    "tickets": len(all_attractions) * 30,
                    "total": 0
                }
            }
            
        except Exception as e:
            print(f"[构建行程JSON] 失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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

