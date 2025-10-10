"""
API路由汇总
"""
from fastapi import APIRouter

from app.api.v1 import attraction, chat, trip
# 导入增强版行程API
try:
    from app.api.v1 import enhanced_itinerary
    has_enhanced_itinerary = True
except ImportError:
    has_enhanced_itinerary = False

# 导入Agent API
try:
    from app.api.v1 import agent
    has_agent = True
except ImportError:
    has_agent = False

# 导入流式Agent API
try:
    from app.api.v1 import agent_stream
    has_agent_stream = True
except ImportError:
    has_agent_stream = False

# 导入增强版Agent流式API
try:
    from app.api.v1 import agent_enhanced_stream
    has_agent_enhanced_stream = True
    print("[路由] ✅ agent_enhanced_stream 导入成功")
except ImportError as e:
    has_agent_enhanced_stream = False
    print(f"[路由] ❌ agent_enhanced_stream 导入失败: {e}")
except Exception as e:
    has_agent_enhanced_stream = False
    print(f"[路由] ❌ agent_enhanced_stream 加载异常: {e}")

# 导入路线规划API
try:
    from app.api.v1 import route
    has_route = True
except ImportError:
    has_route = False

# 导入性能监控API
try:
    from app.api.v1 import performance
    has_performance = True
except ImportError:
    has_performance = False

# 导入城市信息API
try:
    from app.api.v1 import city
    has_city = True
except ImportError:
    has_city = False

# 导入IP定位API
try:
    from app.api.v1 import location
    has_location = True
except ImportError:
    has_location = False

api_router = APIRouter()

# 注册现有路由
api_router.include_router(attraction.router, prefix="/attractions", tags=["景点"])
api_router.include_router(chat.router, prefix="/chat", tags=["AI对话"])
api_router.include_router(trip.router, prefix="/trips", tags=["行程"])

# 注册增强版行程API
if has_enhanced_itinerary:
    api_router.include_router(
        enhanced_itinerary.router, 
        prefix="/itinerary", 
        tags=["完整行程规划"]
    )

# 注册智能Agent API
if has_agent:
    api_router.include_router(
        agent.router,
        prefix="/agent",
        tags=["智能Agent"]
    )

# 注册流式Agent API
if has_agent_stream:
    api_router.include_router(
        agent_stream.router,
        prefix="/agent",
        tags=["智能Agent（流式）"]
    )

# 注册增强版Agent流式API
if has_agent_enhanced_stream:
    api_router.include_router(
        agent_enhanced_stream.router,
        prefix="/agent",
        tags=["智能Agent（增强流式）"]
    )
    print("[路由] ✅ agent_enhanced_stream 路由已注册: /api/v1/agent/enhanced-stream")
else:
    print("[路由] ⚠️ agent_enhanced_stream 未注册（导入失败）")

# 注册路线规划API
if has_route:
    api_router.include_router(
        route.router,
        prefix="/route",
        tags=["路线规划（v5）"]
    )

# 注册性能监控API
if has_performance:
    api_router.include_router(
        performance.router,
        prefix="/performance",
        tags=["性能监控"]
    )

# 注册城市信息API
if has_city:
    api_router.include_router(
        city.router,
        prefix="/cities",
        tags=["城市信息"]
    )

# 注册IP定位API
if has_location:
    api_router.include_router(
        location.router,
        prefix="/location",
        tags=["IP定位"]
    )
