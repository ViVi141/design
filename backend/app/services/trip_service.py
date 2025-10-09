"""
行程服务：管理行程CRUD
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripUpdate


class TripService:
    """行程服务"""
    
    @staticmethod
    def create_trip(db: Session, trip_data: TripCreate, optimized_data: dict = None) -> Trip:
        """
        创建行程
        
        Args:
            db: 数据库会话
            trip_data: 行程数据
            optimized_data: 优化后的数据（景点、路线、摘要）
            
        Returns:
            创建的行程对象
        """
        # 准备数据
        attractions = [a.model_dump() for a in trip_data.attractions]
        
        if optimized_data:
            attractions = optimized_data.get('attractions', attractions)
            routes = optimized_data.get('routes', [])
            summary = optimized_data.get('summary', {})
        else:
            routes = []
            summary = {}
        
        # 创建行程对象
        trip = Trip(
            title=trip_data.title,
            destination=trip_data.destination,
            days=trip_data.days,
            budget=trip_data.budget,
            attractions=attractions,
            routes=routes,
            summary=summary,
            status='draft'
        )
        
        db.add(trip)
        db.commit()
        db.refresh(trip)
        
        return trip
    
    @staticmethod
    def get_trip(db: Session, trip_id: int) -> Optional[Trip]:
        """获取单个行程"""
        return db.query(Trip).filter(Trip.id == trip_id).first()
    
    @staticmethod
    def get_trips(db: Session, skip: int = 0, limit: int = 20) -> List[Trip]:
        """获取行程列表"""
        return db.query(Trip).order_by(desc(Trip.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_trip(db: Session, trip_id: int, trip_data: TripUpdate) -> Optional[Trip]:
        """
        更新行程
        
        Args:
            db: 数据库会话
            trip_id: 行程ID
            trip_data: 更新数据
            
        Returns:
            更新后的行程对象
        """
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            return None
        
        # 更新字段
        update_data = trip_data.model_dump(exclude_unset=True)
        
        if 'attractions' in update_data:
            update_data['attractions'] = [
                a.model_dump() if hasattr(a, 'model_dump') else a
                for a in update_data['attractions']
            ]
        
        for key, value in update_data.items():
            setattr(trip, key, value)
        
        db.commit()
        db.refresh(trip)
        
        return trip
    
    @staticmethod
    def delete_trip(db: Session, trip_id: int) -> bool:
        """删除行程"""
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            return False
        
        db.delete(trip)
        db.commit()
        return True
    
    @staticmethod
    def search_trips(db: Session, destination: str = None, skip: int = 0, limit: int = 20) -> List[Trip]:
        """搜索行程"""
        query = db.query(Trip)
        
        if destination:
            query = query.filter(Trip.destination.contains(destination))
        
        return query.order_by(desc(Trip.created_at)).offset(skip).limit(limit).all()

