"""
AI性能监控API
"""
from fastapi import APIRouter
from typing import Dict, Any

from app.services.optimized_ai_base import get_monitor, get_cache

router = APIRouter()


@router.get("/stats", response_model=Dict[str, Any])
async def get_performance_stats():
    """
    获取AI服务性能统计
    
    Returns:
        性能统计数据，包括调用次数、成功率、平均耗时等
    """
    monitor = get_monitor()
    
    # 获取总体统计
    overall_stats = monitor.get_stats()
    
    # 获取各操作的统计
    operations = set(m['operation'] for m in monitor.metrics)
    operation_stats = {}
    
    for operation in operations:
        operation_stats[operation] = monitor.get_stats(operation)
    
    return {
        "overall": overall_stats,
        "by_operation": operation_stats,
        "total_metrics": len(monitor.metrics)
    }


@router.post("/cache/clear")
async def clear_cache():
    """
    清空AI缓存
    
    用于调试或释放内存
    """
    cache = get_cache()
    cache.clear()
    
    return {
        "message": "缓存已清空",
        "status": "success"
    }


@router.get("/cache/info")
async def get_cache_info():
    """
    获取缓存信息
    
    Returns:
        缓存使用情况
    """
    cache = get_cache()
    
    return {
        "cache_size": len(cache._cache),
        "cache_enabled": True,
        "ttl_seconds": 3600
    }

