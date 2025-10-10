"""
增强版Agent流式规划：结合工具调用能力
AI可以自主决定调用7种工具获取真实数据
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import json
import asyncio

from app.services.agent_service import get_agent
from app.core.tool_monitor import get_monitor

router = APIRouter()


class EnhancedStreamRequest(BaseModel):
    """增强流式请求"""
    message: str
    destination: str = None
    days: int = 3
    budget: float = 5000
    preferences: list = None


@router.post("/enhanced-stream")
async def enhanced_agent_stream(request: EnhancedStreamRequest):
    """
    增强版Agent流式规划
    
    特点：
    1. AI自主决定需要哪些工具
    2. 实时显示工具调用过程
    3. 基于真实数据生成行程
    4. 支持天气、住宿、美食等查询
    
    使用示例：
    ```
    {
      "message": "我想去北京玩3天，预算5000元",
      "destination": "北京",
      "days": 3,
      "budget": 5000
    }
    ```
    
    Agent会自动：
    - 查询北京天气
    - 搜索热门景点
    - 推荐住宿
    - 推荐美食
    - 优化游览路线
    - 计算总费用
    """
    
    async def event_generator():
        try:
            monitor = get_monitor()
            agent = get_agent()
            
            # 构建增强的提示
            enhanced_message = f"""
用户需求：{request.message}

目标信息：
- 目的地：{request.destination or '待确定'}
- 天数：{request.days}天
- 预算：¥{request.budget}
- 偏好：{', '.join(request.preferences) if request.preferences else '无'}

请按照以下步骤规划：
1. 先获取天气信息（使用get_weather工具）
2. 搜索热门景点（使用search_attractions工具）
3. 推荐住宿（使用search_hotels工具）
4. 推荐美食（使用search_food工具）
5. 优化路线（使用optimize_route工具，如果有3+景点）
6. 综合以上信息，生成详细行程

要求：
- 主动调用所有相关工具
- 给出具体的景点、住宿、美食推荐
- 合理分配每天的景点数量
- 计算总费用，确保在预算内
"""
            
            # 发送开始信号
            yield f"data: {json.dumps({'type': 'start', 'content': '🤖 AI Agent开始工作...'}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'thinking', 'content': 'AI正在分析您的需求，准备调用工具...'}, ensure_ascii=False)}\n\n"
            
            # Agent流式对话
            final_reply = ""
            async for event in agent.chat_stream(enhanced_message):
                # 转发所有事件
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                
                # 收集最终回复
                if event['type'] == 'llm_stream':
                    final_reply += event['content']
                
                # 心跳包（每15秒）
                await asyncio.sleep(0.01)
            
            # 发送完成信号
            yield f"data: {json.dumps({'type': 'complete', 'content': '✅ 行程规划完成', 'reply': final_reply}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'content': f'Agent执行失败: {str(e)}'}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

