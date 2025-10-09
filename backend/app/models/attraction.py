"""
景点模型
"""
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Attraction(Base):
    """景点表（缓存高德API数据）"""
    
    __tablename__ = "attractions"
    
    id = Column(Integer, primary_key=True, index=True)
    amap_id = Column(String(50), unique=True, index=True, comment="高德POI ID")
    name = Column(String(200), nullable=False, comment="景点名称")
    
    # 地理信息
    lng = Column(Float, nullable=False, comment="经度")
    lat = Column(Float, nullable=False, comment="纬度")
    city = Column(String(50), comment="城市")
    address = Column(String(500), comment="地址")
    
    # 分类信息
    type = Column(String(100), comment="类型")
    typecode = Column(String(20), comment="类型编码")
    
    # 详细信息
    rating = Column(Float, comment="评分")
    cost = Column(String(50), comment="门票价格")
    tel = Column(String(100), comment="电话")
    photos = Column(JSON, comment="照片列表")
    
    # 扩展信息
    biz_ext = Column(JSON, comment="商业信息")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<Attraction {self.name} - {self.city}>"

