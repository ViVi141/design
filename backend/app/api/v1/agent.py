"""
智能Agent API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from app.services.agent_service import get_agent
from app.core.tool_monitor import get_monitor

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


@router.post("/chat/stream")
async def agent_chat_stream(request: AgentChatRequest):
    """
    与智能Agent流式对话（实时显示工具调用过程）
    
    返回Server-Sent Events (SSE)流式响应
    
    事件类型：
    - start: Agent开始思考
    - thinking: AI决策过程
    - tool_start: 开始调用工具
    - tool_end: 工具调用完成
    - llm_stream: AI回复的流式输出
    - done: 完成
    - error: 错误
    
    示例：
    ```
    data: {"type": "start", "content": "🤖 Agent开始思考..."}
    data: {"type": "tool_start", "tool": "search_attractions", "content": "🔧 调用工具：search_attractions"}
    data: {"type": "tool_end", "tool": "search_attractions", "content": "✅ search_attractions 完成"}
    data: {"type": "llm_stream", "content": "根据查询结果..."}
    data: {"type": "done", "content": "✅ 完成"}
    ```
    """
    from fastapi.responses import StreamingResponse
    import json
    
    async def event_generator():
        try:
            agent = get_agent()
            async for event in agent.chat_stream(request.message):
                # 转换为SSE格式
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
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


@router.get("/stats")
async def get_agent_stats():
    """
    获取Agent工具调用统计
    
    返回：
    - 总调用次数
    - 成功/失败次数
    - 平均耗时
    - 各工具统计
    - 工具排名
    """
    try:
        monitor = get_monitor()
        stats = monitor.get_stats()
        ranking = monitor.get_tool_ranking()
        
        return {
            "summary": {
                "total_calls": stats['total_calls'],
                "success_calls": stats['success_calls'],
                "failed_calls": stats['failed_calls'],
                "success_rate": stats['success_rate'],
                "avg_duration": f"{stats.get('avg_duration', 0):.2f}秒",
                "total_duration": f"{stats['total_duration']:.2f}秒"
            },
            "tool_ranking": ranking,
            "tool_details": stats['tool_stats']
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取统计失败: {str(e)}"
        )


@router.post("/stats/reset")
async def reset_agent_stats():
    """
    重置Agent统计数据
    """
    try:
        monitor = get_monitor()
        monitor.reset_stats()
        return {"message": "统计已重置"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"重置统计失败: {str(e)}"
        )

