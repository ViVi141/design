"""
AI对话数据模式
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class TravelRequirements(BaseModel):
    """旅行需求（AI提取的结构化数据）"""
    destination: str = Field(..., description="目的地城市")
    days: int = Field(..., ge=1, le=30, description="旅行天数")
    budget: Optional[float] = Field(None, description="预算（元）")
    preferences: List[str] = Field(default_factory=list, description="偏好类型")
    start_date: Optional[str] = Field(None, description="出发日期")


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="角色：user/assistant/system")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")
    history: List[ChatMessage] = Field(default_factory=list, description="历史消息")


class ChatResponse(BaseModel):
    """聊天响应"""
    message: str = Field(..., description="AI回复")
    requirements: Optional[TravelRequirements] = Field(None, description="提取的需求")
    action: str = Field(default="reply", description="动作类型：reply/extract/generate")


class GuideRequest(BaseModel):
    """攻略生成请求"""
    destination: str
    days: int
    attractions: List[dict]

