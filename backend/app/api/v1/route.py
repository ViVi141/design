"""
路线规划API（使用v5）
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Tuple
from app.services.route_service import RouteService, DrivingStrategy, TransitStrategy

router = APIRouter()
route_service = RouteService()


class RouteRequest(BaseModel):
    """路线请求"""
    origin: Tuple[float, float]
    destination: Tuple[float, float]
    mode: str = "driving"  # driving/walking/bicycling/electrobike/transit
    strategy: Optional[int] = None
    city: Optional[str] = None


@router.post("/plan")
async def plan_route(request: RouteRequest):
    """
    规划路线
    
    支持：驾车、步行、骑行、电动车、公交
    """
    try:
        if request.mode == "driving":
            strategy = DrivingStrategy(request.strategy) if request.strategy else DrivingStrategy.DEFAULT
            result = await route_service.get_driving_route(
                origin=request.origin,
                destination=request.destination,
                strategy=strategy
            )
        elif request.mode == "walking":
            result = await route_service.get_walking_route(
                origin=request.origin,
                destination=request.destination
            )
        elif request.mode == "bicycling":
            result = await route_service.get_bicycling_route(
                origin=request.origin,
                destination=request.destination
            )
        elif request.mode == "electrobike":
            result = await route_service.get_electrobike_route(
                origin=request.origin,
                destination=request.destination
            )
        elif request.mode == "transit":
            city = request.city or "010"
            result = await route_service.get_transit_route(
                origin=request.origin,
                destination=request.destination,
                city1=city,
                city2=city,
                strategy=TransitStrategy.RECOMMEND
            )
        else:
            raise HTTPException(status_code=400, detail=f"不支持的出行方式: {request.mode}")
        
        if not result:
            raise HTTPException(status_code=500, detail="路线规划失败")
        
        return {
            'success': True,
            'mode': request.mode,
            'data': result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"路线规划失败: {str(e)}")


@router.get("/strategies")
async def get_strategies():
    """获取可用的策略列表"""
    return {
        'driving': [
            {'value': s.value, 'name': s.name, 'description': get_strategy_desc(s)}
            for s in DrivingStrategy
        ],
        'transit': [
            {'value': s.value, 'name': s.name, 'description': get_transit_desc(s)}
            for s in TransitStrategy
        ]
    }


def get_strategy_desc(strategy: DrivingStrategy) -> str:
    """获取驾车策略描述"""
    desc_map = {
        DrivingStrategy.SPEED_PRIORITY: "速度优先",
        DrivingStrategy.FEE_PRIORITY: "费用优先",
        DrivingStrategy.NORMAL_FAST: "常规最快",
        DrivingStrategy.DEFAULT: "默认推荐（高德推荐）",
        DrivingStrategy.AVOID_CONGESTION: "躲避拥堵",
        DrivingStrategy.HIGHWAY_PRIORITY: "高速优先",
        DrivingStrategy.NO_HIGHWAY: "不走高速",
        DrivingStrategy.LESS_FEE: "少收费",
        DrivingStrategy.MAIN_ROAD: "大路优先",
        DrivingStrategy.FASTEST: "速度最快"
    }
    return desc_map.get(strategy, "未知")


def get_transit_desc(strategy: TransitStrategy) -> str:
    """获取公交策略描述"""
    desc_map = {
        TransitStrategy.RECOMMEND: "推荐模式",
        TransitStrategy.CHEAPEST: "最经济",
        TransitStrategy.LEAST_TRANSFER: "最少换乘",
        TransitStrategy.LEAST_WALKING: "最少步行",
        TransitStrategy.COMFORTABLE: "最舒适",
        TransitStrategy.NO_SUBWAY: "不乘地铁",
        TransitStrategy.SUBWAY_MAP: "地铁图模式",
        TransitStrategy.SUBWAY_PRIORITY: "地铁优先",
        TransitStrategy.TIME_SHORT: "时间短"
    }
    return desc_map.get(strategy, "未知")

