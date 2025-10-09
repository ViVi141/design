"""
景点API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.schemas.attraction import AttractionSearch, AttractionResponse
from app.services.map_service import MapService

router = APIRouter()
map_service = MapService()


@router.post("/search", response_model=List[AttractionResponse])
async def search_attractions(request: AttractionSearch):
    """
    搜索景点
    
    Args:
        request: 搜索请求
        
    Returns:
        景点列表
    """
    try:
        attractions = await map_service.search_attractions(
            city=request.city,
            keyword=request.keyword,
            types=request.types or "110000",
            limit=request.limit
        )
        
        return [
            AttractionResponse(
                id=a['id'],
                name=a['name'],
                lng=a['lng'],
                lat=a['lat'],
                city=a.get('city'),
                address=a.get('address'),
                type=a.get('type'),
                rating=a.get('rating'),
                cost=a.get('cost'),
                tel=a.get('tel'),
                photos=a.get('photos', [])
            )
            for a in attractions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"景点搜索失败: {str(e)}")


@router.get("/recommend")
async def recommend_attractions(
    city: str = Query(..., description="城市名称"),
    preferences: str = Query("", description="偏好，逗号分隔"),
    limit: int = Query(5, ge=1, le=20)
):
    """
    推荐景点
    
    Args:
        city: 城市
        preferences: 偏好
        limit: 返回数量
        
    Returns:
        推荐景点列表
    """
    try:
        # 这里可以结合AI服务进行推荐
        # 目前先使用高德API的热门景点
        attractions = await map_service.search_attractions(
            city=city,
            keyword="景点",
            limit=limit
        )
        
        return {
            "recommendations": [
                {
                    "id": a['id'],
                    "name": a['name'],
                    "rating": a.get('rating', 0),
                    "reason": "热门景点"
                }
                for a in attractions[:limit]
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"景点推荐失败: {str(e)}")

