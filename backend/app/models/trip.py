"""
行程模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class Trip(Base):
    """行程表"""
    
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="行程标题")
    destination = Column(String(100), nullable=False, comment="目的地")
    days = Column(Integer, nullable=False, comment="天数")
    budget = Column(Float, nullable=True, comment="预算")
    
    # 行程数据（JSON格式）
    attractions = Column(JSON, comment="景点列表")
    routes = Column(JSON, comment="路线数据")
    summary = Column(JSON, comment="行程摘要")
    
    # 状态
    status = Column(String(20), default="draft", comment="状态：draft/confirmed")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<Trip {self.title} - {self.destination}>"

