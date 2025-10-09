"""
智能Agent API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from app.services.agent_service import get_agent

router = APIRouter()


class AgentChatRequest(BaseModel):
    """Agent对话请求"""
    message: str


class AgentChatResponse(BaseModel):
    """Agent对话响应"""
    reply: str
    tool_calls: List[Dict[str, Any]]
    intermediate_steps: List[Any]


@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(request: AgentChatRequest):
    """
    与智能Agent对话
    
    Agent可以主动调用工具：
    - 搜索景点（高德地图API）
    - 计算路线
    - 优化顺序（TSP算法）
    - 获取城市信息
    
    示例请求：
    ```json
    {
      "message": "我想去北京玩3天，帮我规划一下行程"
    }
    ```
    
    Agent会：
    1. 调用search_attractions搜索北京景点
    2. 根据结果规划3天行程
    3. 调用optimize_route优化每天的路线
    4. 返回完整的行程建议
    """
    try:
        agent = get_agent()
        result = await agent.chat(request.message)
        
        return AgentChatResponse(
            reply=result['reply'],
            tool_calls=result['tool_calls'],
            intermediate_steps=result['intermediate_steps']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent处理失败: {str(e)}"
        )


@router.post("/reset")
async def reset_agent():
    """
    重置Agent对话历史
    """
    try:
        agent = get_agent()
        agent.reset_history()
        return {"message": "对话历史已重置"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"重置失败: {str(e)}"
        )

