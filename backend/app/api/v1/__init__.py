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

# 导入路线规划API
try:
    from app.api.v1 import route
    has_route = True
except ImportError:
    has_route = False

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

# 注册路线规划API
if has_route:
    api_router.include_router(
        route.router,
        prefix="/route",
        tags=["路线规划（v5）"]
    )
