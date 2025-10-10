"""
景点数据模式
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class AttractionSearch(BaseModel):
    """景点搜索请求"""
    city: str = Field(..., description="城市名称")
    keyword: str = Field(default="景点", description="搜索关键词")
    types: Optional[str] = Field(None, description="类型编码")
    limit: int = Field(default=25, ge=1, le=50, description="返回数量")


class AttractionFilter(BaseModel):
    """景点筛选条件"""
    city: str
    type: Optional[str] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    max_price: Optional[float] = None
    max_distance: Optional[float] = None  # 距离中心点的最大距离（km）
    center_lng: Optional[float] = None
    center_lat: Optional[float] = None


class AttractionResponse(BaseModel):
    """景点响应（优化版：包含缩略图）"""
    id: str
    name: str
    lng: float
    lat: float
    city: Optional[str]
    address: Optional[str]
    type: Optional[str]
    rating: Optional[float] = None
    cost: Optional[str] = None
    tel: Optional[str] = None
    photos: List[str] = []  # 所有图片URL列表
    thumbnail: Optional[str] = None  # 缩略图（第一张图片）
    distance: Optional[float] = None  # 距离（米）
    
    class Config:
        from_attributes = True

