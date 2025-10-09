"""
AI服务：使用LangChain封装DeepSeek API
"""
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

from app.core.config import settings
from app.schemas.chat import TravelRequirements


class AIService:
    """AI服务：使用LangChain封装DeepSeek API"""
    
    def __init__(self):
        # 配置DeepSeek作为LLM后端
        self.llm = ChatOpenAI(
            model=settings.DEEPSEEK_MODEL,
            openai_api_key=settings.DEEPSEEK_API_KEY,
            openai_api_base=settings.DEEPSEEK_API_BASE,
            temperature=0.7
        )
        
        # 创建输出解析器
        self.parser = PydanticOutputParser(pydantic_object=TravelRequirements)
    
    async def chat(self, message: str, history: List[Dict] = None) -> str:
        """
        AI对话
        
        Args:
            message: 用户消息
            history: 历史对话
            
        Returns:
            AI回复
        """
        if history is None:
            history = []
        
        # 构建消息列表
        messages = [
            ("system", """你是一个专业的旅行规划助手。
你的任务是：
1. 友好地与用户交流，了解他们的旅行需求
2. 提出合理的建议和问题
3. 帮助用户规划完美的旅行

请用简洁、友好的语气回复。""")
        ]
        
        # 添加历史消息
        for msg in history:
            messages.append((msg['role'], msg['content']))
        
        # 添加当前消息
        messages.append(("user", message))
        
        # 创建提示模板
        prompt = ChatPromptTemplate.from_messages(messages)
        
        # 执行对话
        chain = prompt | self.llm
        response = await chain.ainvoke({})
        
        return response.content
    
    async def extract_requirements(self, user_input: str) -> TravelRequirements:
        """
        从用户输入中提取旅行需求
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            结构化的旅行需求
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的旅行规划助手。
请从用户的输入中提取旅行需求信息。

{format_instructions}

如果某些信息缺失，请使用合理的默认值或null。"""),
            ("user", "{user_input}")
        ])
        
        chain = prompt | self.llm | self.parser
        
        result = await chain.ainvoke({
            "user_input": user_input,
            "format_instructions": self.parser.get_format_instructions()
        })
        
        return result
    
    async def generate_guide(self, trip_data: Dict) -> str:
        """
        生成旅行攻略
        
        Args:
            trip_data: 行程数据
            
        Returns:
            旅行攻略文本
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的旅行规划师，擅长编写详细的旅行攻略。"),
            ("user", """根据以下行程安排，生成一份详细的旅行攻略：

目的地：{destination}
天数：{days}天
景点列表：
{attractions}

请包含：
1. 每日详细行程安排
2. 景点游玩建议
3. 交通方式推荐
4. 美食推荐
5. 注意事项

请用Markdown格式输出。""")
        ])
        
        chain = prompt | self.llm
        
        attractions_text = "\n".join([
            f"- {a['name']} ({a.get('type', '未知')})"
            for a in trip_data.get('attractions', [])
        ])
        
        response = await chain.ainvoke({
            "destination": trip_data.get('destination', ''),
            "days": trip_data.get('days', 0),
            "attractions": attractions_text
        })
        
        return response.content
    
    async def recommend_attractions(
        self, 
        city: str, 
        preferences: List[str],
        existing_attractions: List[str]
    ) -> List[str]:
        """
        推荐景点
        
        Args:
            city: 城市
            preferences: 用户偏好
            existing_attractions: 已选景点
            
        Returns:
            推荐景点名称列表
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的旅行规划师，熟悉各地景点。"),
            ("user", """请根据以下信息推荐5个景点：

城市：{city}
用户偏好：{preferences}
已选景点：{existing}

请只返回景点名称，每行一个，不要其他说明文字。""")
        ])
        
        chain = prompt | self.llm
        
        response = await chain.ainvoke({
            "city": city,
            "preferences": "、".join(preferences) if preferences else "无特殊偏好",
            "existing": "、".join(existing_attractions) if existing_attractions else "无"
        })
        
        # 解析返回的景点列表
        recommendations = [
            line.strip().lstrip('1234567890.- ')
            for line in response.content.strip().split('\n')
            if line.strip()
        ]
        
        return recommendations[:5]

