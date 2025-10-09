"""
API v1 路由
"""
from fastapi import APIRouter
from app.api.v1 import chat, attraction, trip

api_router = APIRouter()

# 注册子路由
api_router.include_router(chat.router, prefix="/chat", tags=["AI对话"])
api_router.include_router(attraction.router, prefix="/attractions", tags=["景点"])
api_router.include_router(trip.router, prefix="/trips", tags=["行程"])

