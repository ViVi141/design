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


@router.get("/tips")
async def get_input_tips(
    keywords: str = Query(..., description="查询关键词"),
    city: str = Query(None, description="城市"),
    datatype: str = Query("all", description="数据类型"),
    citylimit: bool = Query(False, description="仅返回指定城市")
):
    """
    获取输入提示（自动补全）
    
    Args:
        keywords: 查询关键词
        city: 城市
        datatype: all/poi/bus/busline
        citylimit: 是否仅返回指定城市数据
        
    Returns:
        建议列表
    """
    try:
        tips = await map_service.get_input_tips(
            keywords=keywords,
            city=city,
            datatype=datatype,
            citylimit=citylimit
        )
        
        return {
            'count': len(tips),
            'tips': tips
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取提示失败: {str(e)}")


@router.get("/around")
async def search_around(
    location: str = Query(..., description="中心点坐标 lng,lat"),
    keywords: str = Query(None, description="关键词"),
    types: str = Query(None, description="POI类型"),
    radius: int = Query(5000, ge=0, le=50000, description="搜索半径(米)"),
    sortrule: str = Query("distance", description="排序规则 distance/weight"),
    page_size: int = Query(10, ge=1, le=25, description="每页数量")
):
    """
    周边搜索（v5 API）
    
    Args:
        location: 中心点坐标
        keywords: 关键词
        types: POI类型
        radius: 半径
        sortrule: 排序规则
        page_size: 每页数量
        
    Returns:
        周边POI列表
    """
    try:
        coords = location.split(',')
        location_tuple = (float(coords[0]), float(coords[1]))
        
        pois = await map_service.search_around(
            location=location_tuple,
            keywords=keywords,
            types=types,
            radius=radius,
            sortrule=sortrule,
            page_size=page_size
        )
        
        return {
            'count': len(pois),
            'pois': pois
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"周边搜索失败: {str(e)}")


@router.get("/detail")
async def get_poi_detail(
    ids: str = Query(..., description="POI ID，多个用|分隔，最多10个")
):
    """
    POI详情查询（v5 API）
    
    Args:
        ids: POI ID列表
        
    Returns:
        POI详情
    """
    try:
        poi_ids = ids.split('|')
        pois = await map_service.get_poi_detail(poi_ids)
        
        return {
            'count': len(pois),
            'pois': pois
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"POI详情查询失败: {str(e)}")


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
        # 使用v5 API搜索热门景点
        attractions = await map_service.search_attractions_v5(
            keywords="景点",
            region=city,
            types="110000",
            city_limit=True,
            page_size=limit,
            show_fields="business,photos"
        )
        
        # 按评分排序
        sorted_attractions = sorted(
            attractions, 
            key=lambda x: x.get('rating', 0), 
            reverse=True
        )
        
        return {
            "recommendations": [
                {
                    "id": a['id'],
                    "name": a['name'],
                    "rating": a.get('rating', 0),
                    "cost": a.get('cost', ''),
                    "reason": f"评分{a.get('rating', 0)}" if a.get('rating') else "热门景点"
                }
                for a in sorted_attractions[:limit]
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"景点推荐失败: {str(e)}")

