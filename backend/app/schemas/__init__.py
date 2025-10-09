"""
数据模式模块
"""
from app.schemas.trip import TripCreate, TripUpdate, TripResponse
from app.schemas.chat import ChatRequest, ChatResponse, TravelRequirements
from app.schemas.attraction import AttractionSearch, AttractionResponse

__all__ = [
    "TripCreate",
    "TripUpdate", 
    "TripResponse",
    "ChatRequest",
    "ChatResponse",
    "TravelRequirements",
    "AttractionSearch",
    "AttractionResponse"
]

