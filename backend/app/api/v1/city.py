"""
城市信息API
"""
from fastapi import APIRouter
from typing import Dict, List

from app.core.city_mapping import (
    get_citycode, 
    get_adcode, 
    get_city_info,
    list_supported_cities,
    get_stats,
    SUPPORTED_CITIES,
    STATS
)

router = APIRouter()


@router.get("/supported", response_model=Dict)
async def get_supported_cities():
    """
    获取所有支持的城市列表
    
    Returns:
        支持的城市列表和统计信息
    """
    return {
        'cities': SUPPORTED_CITIES,
        'stats': STATS
    }


@router.get("/search/{city_name}")
async def search_city(city_name: str):
    """
    查询城市编码信息
    
    Args:
        city_name: 城市名称（如"北京"、"上海市"）
        
    Returns:
        城市编码信息，包含adcode和citycode
    """
    city_info = get_city_info(city_name)
    
    if city_info:
        return {
            'city': city_name,
            'adcode': city_info['adcode'],
            'citycode': city_info['citycode'],
            'found': True
        }
    else:
        return {
            'city': city_name,
            'found': False,
            'message': f'未找到城市"{city_name}"的编码信息'
        }


@router.get("/stats")
async def get_city_stats():
    """
    获取城市支持统计信息
    
    Returns:
        统计数据
    """
    return get_stats()


@router.post("/batch-search")
async def batch_search_cities(cities: List[str]):
    """
    批量查询城市编码
    
    Args:
        cities: 城市名称列表
        
    Returns:
        城市编码列表
    """
    results = []
    
    for city_name in cities:
        city_info = get_city_info(city_name)
        if city_info:
            results.append({
                'city': city_name,
                'adcode': city_info['adcode'],
                'citycode': city_info['citycode'],
                'found': True
            })
        else:
            results.append({
                'city': city_name,
                'found': False
            })
    
    return {
        'total': len(cities),
        'found': sum(1 for r in results if r['found']),
        'results': results
    }

