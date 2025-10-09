"""
AI对话API
"""
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, GuideRequest, TravelRequirements
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    AI对话接口
    
    Args:
        request: 聊天请求
        
    Returns:
        AI回复
    """
    try:
        # AI对话
        reply = await ai_service.chat(
            message=request.message,
            history=[msg.model_dump() for msg in request.history]
        )
        
        return ChatResponse(
            message=reply,
            action="reply"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI对话失败: {str(e)}")


@router.post("/extract", response_model=TravelRequirements)
async def extract_requirements(request: ChatRequest):
    """
    提取旅行需求
    
    Args:
        request: 用户输入
        
    Returns:
        结构化的旅行需求
    """
    try:
        requirements = await ai_service.extract_requirements(request.message)
        return requirements
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"需求提取失败: {str(e)}")


@router.post("/guide")
async def generate_guide(request: GuideRequest):
    """
    生成旅行攻略
    
    Args:
        request: 攻略生成请求
        
    Returns:
        旅行攻略文本
    """
    try:
        trip_data = {
            'destination': request.destination,
            'days': request.days,
            'attractions': request.attractions
        }
        
        guide = await ai_service.generate_guide(trip_data)
        
        return {
            "guide": guide
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"攻略生成失败: {str(e)}")

