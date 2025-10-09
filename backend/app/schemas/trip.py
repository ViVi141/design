"""
行程数据模式
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AttractionBase(BaseModel):
    """景点基础信息"""
    name: str
    lng: float
    lat: float
    type: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = None
    cost: Optional[str] = None


class RouteSegment(BaseModel):
    """路线段"""
    from_idx: int
    to_idx: int
    distance: float  # 米
    duration: float  # 秒
    mode: str = "walking"  # walking, driving, transit


class TripSummary(BaseModel):
    """行程摘要"""
    num_attractions: int
    total_distance_km: float
    total_duration_hours: float
    total_cost: float
    optimization_rate: Optional[float] = None  # 优化率


class TripCreate(BaseModel):
    """创建行程"""
    title: str = Field(..., description="行程标题")
    destination: str = Field(..., description="目的地")
    days: int = Field(..., ge=1, le=30, description="天数")
    budget: Optional[float] = Field(None, ge=0, description="预算")
    attractions: List[AttractionBase] = Field(..., description="景点列表")


class TripUpdate(BaseModel):
    """更新行程"""
    title: Optional[str] = None
    status: Optional[str] = None
    attractions: Optional[List[AttractionBase]] = None


class TripResponse(BaseModel):
    """行程响应"""
    id: int
    title: str
    destination: str
    days: int
    budget: Optional[float]
    attractions: List[Dict[str, Any]]
    routes: Optional[List[Dict[str, Any]]]
    summary: Optional[TripSummary]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

