"""
增强版行程API：完整行程生成
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.services.enhanced_ai_service import (
    EnhancedAIService, 
    CompleteItinerary,
    HotelInfo,
    TransportInfo
)
from app.services.map_service import MapService
from app.services.route_planner import RoutePlanner
from app.services.itinerary_validator import get_validator

router = APIRouter()
ai_service = EnhancedAIService()
map_service = MapService()
route_planner = RoutePlanner()


class GenerateRequest(BaseModel):
    """生成完整行程请求"""
    destination: str
    days: int
    budget: float
    preferences: Optional[List[str]] = None
    start_date: Optional[str] = None


class HotelRecommendRequest(BaseModel):
    """住宿推荐请求"""
    destination: str
    central_location: str
    budget_per_night: float
    nights: int


class TransportSuggestionRequest(BaseModel):
    """交通建议请求"""
    from_city: str
    to_city: str
    date: str
    budget: float


@router.post("/generate/complete")
async def generate_complete_itinerary(request: GenerateRequest):
    """
    AI一键生成完整行程（景点+住宿+交通+费用）
    
    这是核心API，替代原来只生成景点的功能。
    
    流程：
    1. AI生成结构化行程框架
    2. 调用高德API获取景点详细坐标
    3. TSP算法优化每天的景点顺序
    4. 计算实际路线和距离
    5. 返回可直接使用的完整行程
    
    示例请求：
    ```json
    {
      "destination": "北京",
      "days": 3,
      "budget": 3000,
      "preferences": ["历史文化", "美食"],
      "start_date": "2025-10-15"
    }
    ```
    """
    try:
        print(f"开始生成{request.destination}{request.days}天完整行程...")
        
        # 步骤1：AI生成行程框架
        print("步骤1: AI生成行程框架...")
        itinerary = await ai_service.generate_complete_itinerary(
            destination=request.destination,
            days=request.days,
            budget=request.budget,
            preferences=request.preferences,
            start_date=request.start_date
        )
        
        # 步骤2：填充景点详细信息（坐标、地址等）
        print("步骤2: 获取景点详细信息...")
        for day in itinerary.daily_schedule:
            for attraction in day.attractions:
                try:
                    # 调用高德POI搜索获取景点详细信息
                    results = await map_service.search_attractions(
                        city=request.destination,
                        keyword=attraction.name,
                        limit=1
                    )
                    
                    if results and len(results) > 0:
                        poi = results[0]  # 取第一个结果
                        # 更新景点信息（包含图片）
                        attraction.address = poi.get('address', '')
                        attraction.lng = poi.get('lng', 0)
                        attraction.lat = poi.get('lat', 0)
                        attraction.type = poi.get('type', '')
                        attraction.rating = poi.get('rating', 0)
                        attraction.tel = poi.get('tel', '')
                        attraction.photos = poi.get('photos', [])
                        attraction.thumbnail = poi.get('thumbnail', '')
                        
                        print(f"  ✓ {attraction.name}: {attraction.address} {'📷' if attraction.thumbnail else ''}")
                    else:
                        print(f"  ✗ {attraction.name}: 未找到详细信息")
                        
                except Exception as e:
                    print(f"  ✗ {attraction.name}: 获取信息失败 - {e}")
                    continue
        
        # 步骤3：优化每天的景点顺序（TSP）
        print("步骤3: 优化每天景点顺序...")
        for day in itinerary.daily_schedule:
            if len(day.attractions) > 1:
                # 转换为字典格式供TSP算法使用
                attractions_data = [
                    {
                        'name': attr.name,
                        'lng': getattr(attr, 'lng', 0),
                        'lat': getattr(attr, 'lat', 0),
                        'cost': attr.cost
                    }
                    for attr in day.attractions
                    if hasattr(attr, 'lng') and hasattr(attr, 'lat')
                ]
                
                if len(attractions_data) > 1:
                    try:
                        # 使用TSP优化顺序（传入预算和城市用于智能选择交通方式）
                        optimized = await route_planner.optimize_route(
                            attractions_data,
                            budget=request.budget,
                            days=request.days,
                            city=request.destination  # 传递城市参数
                        )
                        
                        # 更新景点顺序
                        optimized_names = [a['name'] for a in optimized['attractions']]
                        day.attractions.sort(
                            key=lambda x: optimized_names.index(x.name) 
                            if x.name in optimized_names else 999
                        )
                        
                        print(f"  ✓ 第{day.day}天: 优化完成，节省{optimized['summary'].get('optimization_rate', 0):.1f}%路程")
                    except Exception as e:
                        print(f"  ✗ 第{day.day}天: 优化失败 - {e}")
        
        print("✅ 完整行程生成成功！")
        
        # 步骤4：AI验证行程合理性
        print("步骤4: AI验证行程合理性...")
        try:
            validator = get_validator()
            validation = await validator.validate_itinerary({
                'destination': request.destination,
                'days': request.days,
                'budget': request.budget,
                'daily_schedule': [day.model_dump() for day in itinerary.daily_schedule],
                'cost_breakdown': itinerary.cost_breakdown.model_dump()
            })
            
            print(f"  验证评分: {validation.get('overall_score', 0)}/100")
            if validation.get('issues'):
                print(f"  发现问题: {len(validation['issues'])}个")
            print(f"  {validation.get('summary', '验证完成')}")
            
            # 将验证结果添加到响应中
            itinerary_dict = itinerary.model_dump()
            itinerary_dict['validation'] = validation
            
            return itinerary_dict
            
        except Exception as e:
            print(f"  ✗ AI验证失败: {e}")
            # 验证失败不影响行程返回
            return itinerary
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"生成完整行程失败: {str(e)}"
        )


@router.post("/hotels/recommend", response_model=List[HotelInfo])
async def recommend_hotels(request: HotelRecommendRequest):
    """
    推荐住宿
    
    结合高德POI搜索和AI推荐，返回性价比高的酒店列表。
    
    示例请求：
    ```json
    {
      "destination": "北京",
      "central_location": "王府井",
      "budget_per_night": 300,
      "nights": 2
    }
    ```
    """
    try:
        # AI推荐
        hotels = await ai_service.add_hotel_recommendation(
            destination=request.destination,
            central_location=request.central_location,
            budget_per_night=request.budget_per_night,
            nights=request.nights
        )
        
        return hotels
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"推荐住宿失败: {str(e)}"
        )


@router.post("/transportation/suggest", response_model=List[TransportInfo])
async def suggest_transportation(request: TransportSuggestionRequest):
    """
    建议城际交通方式
    
    AI推荐高铁、飞机等交通方式，包含大概价格和时间。
    
    示例请求：
    ```json
    {
      "from_city": "上海",
      "to_city": "北京",
      "date": "2025-10-15",
      "budget": 1000
    }
    ```
    """
    try:
        transport_options = await ai_service.suggest_transportation(
            from_city=request.from_city,
            to_city=request.to_city,
            date=request.date,
            budget=request.budget
        )
        
        return transport_options
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"推荐交通方式失败: {str(e)}"
        )


@router.post("/optimize")
async def optimize_existing_itinerary(
    itinerary: CompleteItinerary,
    goal: str = "优化路线"
):
    """
    优化现有行程
    
    Args:
        itinerary: 当前行程
        goal: 优化目标，如"减少预算"、"增加景点"、"优化路线"
    """
    try:
        optimized = await ai_service.optimize_itinerary_with_context(
            current_itinerary=itinerary,
            optimization_goal=goal
        )
        
        return optimized
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"优化行程失败: {str(e)}"
        )


@router.post("/validate")
async def validate_itinerary(itinerary: CompleteItinerary):
    """
    验证已有行程的合理性和可行性
    
    使用AI分析行程，评估：
    - 时间合理性（景点数量、路程时间）
    - 路线合理性（顺序优化、交通方式）
    - 预算可行性（费用分配、隐性开支）
    - 体验合理性（景点类型、劳逸结合）
    - 实际可行性（季节天气、紧急预案）
    
    返回评分、问题和改进建议
    """
    try:
        validator = get_validator()
        validation = await validator.validate_itinerary(itinerary.model_dump())
        
        return validation
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"验证失败: {str(e)}"
        )


@router.post("/quick-check")
async def quick_check_params(
    destination: str,
    days: int,
    budget: float,
    num_attractions: int = 10
):
    """
    快速检查基本参数的合理性
    
    在生成行程前，先检查基本参数是否合理
    """
    try:
        validator = get_validator()
        result = await validator.quick_check(
            destination, days, budget, num_attractions
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"检查失败: {str(e)}"
        )


@router.get("/preview/{destination}")
async def preview_destination(destination: str):
    """
    预览目的地信息
    
    返回目的地的基本信息、推荐景点数量、平均预算等。
    """
    try:
        # 简单的AI咨询
        from langchain_openai import ChatOpenAI
        from app.core.config import settings
        
        llm = ChatOpenAI(
            model=settings.DEEPSEEK_MODEL,
            openai_api_key=settings.DEEPSEEK_API_KEY,
            openai_api_base=settings.DEEPSEEK_API_BASE
        )
        
        prompt = f"""
        请简要介绍{destination}作为旅游目的地的信息：
        1. 推荐游玩天数
        2. 必去景点数量（Top 10）
        3. 平均每天预算
        4. 最佳旅游季节
        
        以JSON格式返回：
        {{
          "recommended_days": 3,
          "top_attractions_count": 10,
          "avg_daily_budget": 800,
          "best_season": "秋季（9-11月）",
          "brief": "简短介绍"
        }}
        """
        
        response = await llm.ainvoke(prompt)
        
        import json
        preview = json.loads(response.content)
        
        return preview
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取目的地信息失败: {str(e)}"
        )

