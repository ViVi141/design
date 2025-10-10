"""
AI服务：使用LangChain封装DeepSeek API（优化版）
"""
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

from app.core.config import settings
from app.schemas.chat import TravelRequirements
from app.services.optimized_ai_base import OptimizedAIBase


class AIService(OptimizedAIBase):
    """AI服务：使用LangChain封装DeepSeek API（优化版）"""
    
    def __init__(self):
        super().__init__()
        
        # 对话LLM - 平衡模式
        self.llm = self.create_llm(
            temperature=settings.AI_TEMPERATURE_BALANCED,
            max_tokens=2000  # 对话不需要太长
        )
        
        # 精确LLM - 用于需求提取
        self.precise_llm = self.create_llm(
            temperature=settings.AI_TEMPERATURE_PRECISE,
            max_tokens=1000
        )
        
        # 创意LLM - 用于生成攻略
        self.creative_llm = self.create_llm(
            temperature=settings.AI_TEMPERATURE_CREATIVE,
            max_tokens=4000
        )
        
        # 创建输出解析器
        self.parser = PydanticOutputParser(pydantic_object=TravelRequirements)
    
    async def chat(self, message: str, history: List[Dict] = None) -> str:
        """
        AI对话（优化版：带缓存和重试）
        
        Args:
            message: 用户消息
            history: 历史对话
            
        Returns:
            AI回复
        """
        if history is None:
            history = []
        
        # 生成缓存键
        cache_key = self.generate_cache_key("chat", message, len(history))
        
        async def _execute():
            # 构建消息列表
            messages = [
                ("system", """你是一个专业的旅行规划助手。
你的任务是：
1. 友好地与用户交流，了解他们的旅行需求
2. 提出合理的建议和问题
3. 帮助用户规划完美的旅行

请用简洁、友好的语气回复，控制在200字以内。""")
            ]
            
            # 添加历史消息（只保留最近5轮）
            recent_history = history[-10:] if len(history) > 10 else history
            for msg in recent_history:
                messages.append((msg['role'], msg['content']))
            
            # 添加当前消息
            messages.append(("user", message))
            
            # 创建提示模板
            prompt = ChatPromptTemplate.from_messages(messages)
            
            # 执行对话
            chain = prompt | self.llm
            response = await chain.ainvoke({})
            
            return response.content
        
        # 使用缓存和重试
        return await self.call_with_cache_and_retry(
            operation="chat",
            func=_execute,
            cache_key=cache_key,
            enable_cache=True
        )
    
    async def extract_requirements(self, user_input: str) -> TravelRequirements:
        """
        从用户输入中提取旅行需求（优化版：使用精确模式）
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            结构化的旅行需求
        """
        cache_key = self.generate_cache_key("extract", user_input)
        
        async def _execute():
            prompt = ChatPromptTemplate.from_messages([
                ("system", """你是一个专业的旅行规划助手。
请从用户的输入中精确提取旅行需求信息。

{format_instructions}

如果某些信息缺失，请使用合理的默认值或null。"""),
                ("user", "{user_input}")
            ])
            
            # 使用精确模式的LLM
            chain = prompt | self.precise_llm | self.parser
            
            result = await chain.ainvoke({
                "user_input": user_input,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            return result
        
        return await self.call_with_cache_and_retry(
            operation="extract_requirements",
            func=_execute,
            cache_key=cache_key,
            enable_cache=True
        )
    
    async def generate_guide(self, trip_data: Dict) -> str:
        """
        生成旅行攻略（优化版：使用创意模式）
        
        Args:
            trip_data: 行程数据
            
        Returns:
            旅行攻略文本
        """
        attractions_text = "\n".join([
            f"- {a['name']} ({a.get('type', '未知')})"
            for a in trip_data.get('attractions', [])
        ])
        
        cache_key = self.generate_cache_key(
            "guide",
            trip_data.get('destination', ''),
            trip_data.get('days', 0),
            attractions_text[:100]  # 使用前100字符避免键太长
        )
        
        async def _execute():
            prompt = ChatPromptTemplate.from_messages([
                ("system", """你是一个专业的旅行规划师，擅长编写详细实用的旅行攻略。
请生成内容丰富但简洁明了的攻略，控制在1000字以内。"""),
                ("user", """根据以下行程安排，生成一份详细的旅行攻略：

目的地：{destination}
天数：{days}天
景点列表：
{attractions}

请包含：
1. 每日详细行程安排（精简版）
2. 景点游玩建议（重点提示）
3. 交通方式推荐（最优方案）
4. 美食推荐（特色推荐）
5. 注意事项（重要提醒）

请用Markdown格式输出，语言简洁。""")
            ])
            
            # 使用创意模式的LLM
            chain = prompt | self.creative_llm
            
            response = await chain.ainvoke({
                "destination": trip_data.get('destination', ''),
                "days": trip_data.get('days', 0),
                "attractions": attractions_text
            })
            
            return response.content
        
        return await self.call_with_cache_and_retry(
            operation="generate_guide",
            func=_execute,
            cache_key=cache_key,
            enable_cache=True
        )
    
    async def recommend_attractions(
        self, 
        city: str, 
        preferences: List[str],
        existing_attractions: List[str]
    ) -> List[str]:
        """
        推荐景点（优化版：使用创意模式）
        
        Args:
            city: 城市
            preferences: 用户偏好
            existing_attractions: 已选景点
            
        Returns:
            推荐景点名称列表
        """
        cache_key = self.generate_cache_key(
            "recommend",
            city,
            str(preferences),
            str(existing_attractions)
        )
        
        async def _execute():
            prompt = ChatPromptTemplate.from_messages([
                ("system", """你是一个专业的旅行规划师，熟悉各地景点。
请推荐真实存在的热门景点，避免重复。"""),
                ("user", """请根据以下信息推荐5个景点：

城市：{city}
用户偏好：{preferences}
已选景点：{existing}

要求：
1. 只返回景点名称，每行一个
2. 不要编号、不要说明文字
3. 确保景点真实存在
4. 避免与已选景点重复""")
            ])
            
            # 使用创意模式的LLM
            chain = prompt | self.creative_llm
            
            response = await chain.ainvoke({
                "city": city,
                "preferences": "、".join(preferences) if preferences else "无特殊偏好",
                "existing": "、".join(existing_attractions) if existing_attractions else "无"
            })
            
            # 解析返回的景点列表
            recommendations = [
                line.strip().lstrip('1234567890.- ').rstrip('。，')
                for line in response.content.strip().split('\n')
                if line.strip()
            ]
            
            return recommendations[:5]
        
        return await self.call_with_cache_and_retry(
            operation="recommend_attractions",
            func=_execute,
            cache_key=cache_key,
            enable_cache=True
        )

