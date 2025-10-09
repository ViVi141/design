"""
行程API
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.trip import TripCreate, TripUpdate, TripResponse
from app.services.trip_service import TripService
from app.services.route_planner import RoutePlanner

router = APIRouter()
trip_service = TripService()
route_planner = RoutePlanner()


@router.post("/", response_model=TripResponse)
async def create_trip(trip_data: TripCreate, optimize: bool = True, db: Session = Depends(get_db)):
    """
    创建行程
    
    Args:
        trip_data: 行程数据
        optimize: 是否优化路径
        db: 数据库会话
        
    Returns:
        创建的行程
    """
    try:
        optimized_data = None
        
        if optimize and len(trip_data.attractions) > 1:
            # 转换为字典格式
            attractions = [a.model_dump() for a in trip_data.attractions]
            
            # 路径优化
            optimized_data = await route_planner.optimize_route(attractions)
        
        # 创建行程
        trip = trip_service.create_trip(db, trip_data, optimized_data)
        
        return trip
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建行程失败: {str(e)}")


@router.get("/", response_model=List[TripResponse])
def get_trips(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    destination: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取行程列表
    
    Args:
        skip: 跳过数量
        limit: 限制数量
        destination: 目的地筛选
        db: 数据库会话
        
    Returns:
        行程列表
    """
    try:
        if destination:
            trips = trip_service.search_trips(db, destination, skip, limit)
        else:
            trips = trip_service.get_trips(db, skip, limit)
        
        return trips
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行程列表失败: {str(e)}")


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    """
    获取单个行程
    
    Args:
        trip_id: 行程ID
        db: 数据库会话
        
    Returns:
        行程详情
    """
    trip = trip_service.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")
    return trip


@router.put("/{trip_id}", response_model=TripResponse)
def update_trip(trip_id: int, trip_data: TripUpdate, db: Session = Depends(get_db)):
    """
    更新行程
    
    Args:
        trip_id: 行程ID
        trip_data: 更新数据
        db: 数据库会话
        
    Returns:
        更新后的行程
    """
    trip = trip_service.update_trip(db, trip_id, trip_data)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")
    return trip


@router.delete("/{trip_id}")
def delete_trip(trip_id: int, db: Session = Depends(get_db)):
    """
    删除行程
    
    Args:
        trip_id: 行程ID
        db: 数据库会话
        
    Returns:
        删除结果
    """
    success = trip_service.delete_trip(db, trip_id)
    if not success:
        raise HTTPException(status_code=404, detail="行程不存在")
    return {"message": "删除成功"}


@router.post("/{trip_id}/optimize")
async def optimize_trip(trip_id: int, db: Session = Depends(get_db)):
    """
    重新优化行程路径
    
    Args:
        trip_id: 行程ID
        db: 数据库会话
        
    Returns:
        优化后的行程
    """
    try:
        # 获取行程
        trip = trip_service.get_trip(db, trip_id)
        if not trip:
            raise HTTPException(status_code=404, detail="行程不存在")
        
        # 优化路径
        optimized_data = await route_planner.optimize_route(trip.attractions)
        
        # 更新行程
        trip.attractions = optimized_data['attractions']
        trip.routes = optimized_data['routes']
        trip.summary = optimized_data['summary']
        
        db.commit()
        db.refresh(trip)
        
        return trip
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"路径优化失败: {str(e)}")

