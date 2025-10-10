"""
流式Agent API - 实时显示AI思考过程
"""
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
import json
import asyncio

from app.services.agent_service import get_agent
from app.services.enhanced_ai_service import EnhancedAIService
from app.services.map_service import MapService

router = APIRouter()
ai_service = EnhancedAIService()
map_service = MapService()


class StreamChatRequest(BaseModel):
    """流式对话请求"""
    message: str
    destination: str = None
    days: int = 3
    budget: float = 5000
    preferences: list = None


async def generate_stream_response(request: StreamChatRequest):
    """
    生成流式响应 - 展示AI的深度思考过程
    
    实时输出：
    1. AI分析需求
    2. AI思考过程
    3. 工具调用和结果
    4. AI综合判断
    5. 最终行程
    """
    print(f"\n{'='*60}")
    print(f"开始流式响应 - 目的地: {request.destination}, 天数: {request.days}")
    print(f"{'='*60}\n")
    
    try:
        # 1. 分析用户需求（快速输出，减少延迟）
        print("发送: 收到用户消息")
        yield f"data: {json.dumps({'type': 'thinking', 'content': f'收到用户消息：{request.message}'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.1)
        
        # 处理多目的地
        destinations = request.destination.split('、') if '、' in request.destination else [request.destination]
        is_multi_destination = len(destinations) > 1
        
        print("发送: 提取关键信息")
        if is_multi_destination:
            destinations_str = "、".join(destinations)
            avg_days = request.days // len(destinations)
            yield f"data: {json.dumps({'type': 'thinking', 'content': f'提取关键信息：多地旅行={len(destinations)}个目的地（{destinations_str}），天数={request.days}天，预算=¥{request.budget}'}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'thinking', 'content': f'思考：多地旅行需要合理分配时间，建议每地{avg_days}-{avg_days + 1}天'}, ensure_ascii=False)}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'thinking', 'content': f'提取关键信息：目的地={request.destination}，天数={request.days}天，预算=¥{request.budget}'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.1)
        
        if request.preferences:
            prefs_text = "、".join(request.preferences)
            yield f"data: {json.dumps({'type': 'thinking', 'content': f'用户偏好：{prefs_text}'}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.1)
        
        # 2. AI决策（合并多个思考，减少延迟）
        yield f"data: {json.dumps({'type': 'thinking', 'content': f'思考：需要为用户规划完整行程，包括景点、住宿、交通'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'type': 'thinking', 'content': f'决策：先生成{request.days}天的行程框架，每天安排2-3个景点'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'type': 'status', 'content': '🤖 连接DeepSeek API...'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.1)
        
        print("发送: DeepSeek开始推理")
        yield f"data: {json.dumps({'type': 'deepseek', 'content': '🧠 DeepSeek开始推理...'}, ensure_ascii=False)}\n\n"
        
        print("开始调用DeepSeek流式API...")
        
        # 显示等待状态
        yield f"data: {json.dumps({'type': 'deepseek', 'content': '⏳ 等待DeepSeek首次响应...'}, ensure_ascii=False)}\n\n"
        
        # 使用流式API获取DeepSeek的实时输出
        accumulated_content = ""
        json_started = False
        chunk_received = 0
        first_chunk_received = False
        
        try:
            print(f"调用 ai_service.generate_complete_itinerary_stream({request.destination}, {request.days}, {request.budget})")
            async for chunk in ai_service.generate_complete_itinerary_stream(
                destination=request.destination or '未知',
                days=request.days,
                budget=request.budget,
                preferences=request.preferences
            ):
                chunk_received += 1
                print(f"[主流程] 收到chunk #{chunk_received}: {chunk[:30]}..." if len(chunk) > 30 else f"[主流程] 收到chunk #{chunk_received}: {chunk}")
                
                # 首次收到内容时的提示
                if not first_chunk_received:
                    first_chunk_received = True
                    yield f"data: {json.dumps({'type': 'deepseek', 'content': '✅ DeepSeek开始输出...'}, ensure_ascii=False)}\n\n"
                
                # 实时转发DeepSeek的输出
                accumulated_content += chunk
                
                # 检测是否开始输出JSON
                if '```json' in chunk and not json_started:
                    json_started = True
                    yield f"data: {json.dumps({'type': 'deepseek', 'content': '→ 开始生成JSON结构...'}, ensure_ascii=False)}\n\n"
                
                # 实时显示所有chunk（每5个chunk发送一次，提升流式体验）
                if chunk.strip():
                    # 过滤掉markdown标记
                    clean_chunk = chunk.replace('```json', '').replace('```', '').strip()
                    if clean_chunk:
                        # 每5个chunk发送一次到前端（更流畅）
                        if chunk_received % 5 == 0:
                            # 发送最近累积的内容（最后300字符）
                            recent_content = accumulated_content[-300:] if len(accumulated_content) > 300 else accumulated_content
                            yield f"data: {json.dumps({'type': 'deepseek_stream', 'content': recent_content}, ensure_ascii=False)}\n\n"
            
            # 解析完整的响应
            yield f"data: {json.dumps({'type': 'status', 'content': '📝 解析DeepSeek响应...'}, ensure_ascii=False)}\n\n"
            
            # 提取JSON部分
            content = accumulated_content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # 解析为字典
            import json as json_module
            data = json_module.loads(content)
            
            # 验证和转换为Pydantic模型
            from app.services.enhanced_ai_service import CompleteItinerary
            itinerary = CompleteItinerary.model_validate(data)
            
            print(f"[主流程] DeepSeek流式调用完成，共收到 {chunk_received} 个chunks")
            print(f"[主流程] 累计内容长度: {len(accumulated_content)} 字符")
            yield f"data: {json.dumps({'type': 'status', 'content': '✅ DeepSeek完成推理！'}, ensure_ascii=False)}\n\n"
        except Exception as e:
            print(f"[主流程] DeepSeek调用异常: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'content': f'DeepSeek调用失败: {str(e)}'}, ensure_ascii=False)}\n\n"
            raise
        await asyncio.sleep(0.1)
        
        # 合并多个思考输出，减少延迟
        total_attr_count = sum(len(d.attractions) for d in itinerary.daily_schedule)
        all_attractions = []
        for day in itinerary.daily_schedule:
            all_attractions.extend([attr.name for attr in day.attractions])
        attractions_preview = "、".join(all_attractions[:5])
        
        yield f"data: {json.dumps({'type': 'thinking', 'content': f'收到响应：{len(itinerary.daily_schedule)}天行程，共{total_attr_count}个景点'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'type': 'status', 'content': f'✅ AI返回：{request.days}天行程框架已生成'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'type': 'thinking', 'content': f'AI推荐的景点：{attractions_preview}等共{len(all_attractions)}个'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'type': 'thinking', 'content': '决策：需要获取这些景点的详细信息（坐标、地址、评分等）'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.1)
        
        # 4. 获取景点详细信息（并发查询，提速50%）
        yield f"data: {json.dumps({'type': 'status', 'content': '🔍 并发查询景点信息...'}, ensure_ascii=False)}\n\n"
        
        total_attractions = sum(len(day.attractions) for day in itinerary.daily_schedule)
        
        # 收集所有需要查询的景点
        all_queries = []
        for day in itinerary.daily_schedule:
            for attraction in day.attractions:
                all_queries.append((day, attraction))
        
        # 如果是多目的地，按城市分组查询
        if is_multi_destination:
            yield f"data: {json.dumps({'type': 'thinking', 'content': f'思考：多目的地旅行，按城市分组验证景点'}, ensure_ascii=False)}\n\n"
        
        # 并发查询（每批5个，避免API限制）
        batch_size = 5
        processed = 0
        valid_count = 0
        
        for i in range(0, len(all_queries), batch_size):
            batch = all_queries[i:i+batch_size]
            
            # 并发查询这一批
            tasks = [
                map_service.search_attractions(
                    city=request.destination,
                    keyword=attr.name,
                    limit=3
                )
                for day, attr in batch
            ]
            
            results_batch = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            for (day, attraction), results in zip(batch, results_batch):
                processed += 1
                
                # 每5个发送一次进度
                if processed % 5 == 0 or processed == total_attractions:
                    yield f"data: {json.dumps({'type': 'progress', 'current': processed, 'total': total_attractions, 'name': attraction.name}, ensure_ascii=False)}\n\n"
                
                if isinstance(results, Exception):
                    continue
                
                if results and len(results) > 0:
                    # 验证景点是否在目标区域（支持多目的地）
                    valid_poi = None
                    for poi in results:
                        address = poi.get('address', '')
                        # 检查是否在任一目的地
                        if is_multi_destination:
                            for dest in destinations:
                                if dest in address:
                                    valid_poi = poi
                                    valid_count += 1
                                    break
                        else:
                            if request.destination in address:
                                valid_poi = poi
                                valid_count += 1
                                break
                        if valid_poi:
                            break
                    
                    if not valid_poi:
                        valid_poi = results[0]
                    
                    attraction.address = valid_poi.get('address', '')
                    attraction.lng = valid_poi.get('lng', 0)
                    attraction.lat = valid_poi.get('lat', 0)
                    attraction.type = valid_poi.get('type', '')
                    
                    # 补充v5新增字段（用于前端展示和AI分析）
                    if hasattr(attraction, 'rating'):
                        attraction.rating = valid_poi.get('rating', 0)
                    if hasattr(attraction, 'tel'):
                        attraction.tel = valid_poi.get('tel', '')
                    if hasattr(attraction, 'opentime'):
                        attraction.opentime = valid_poi.get('opentime', '')
                    if hasattr(attraction, 'business_area'):
                        attraction.business_area = valid_poi.get('business_area', '')
        
        # 5. 验证结果并补全（快速输出）
        invalid_count = total_attractions - valid_count
        if invalid_count == 0:
            yield f"data: {json.dumps({'type': 'status', 'content': f'✅ 所有景点验证通过'}, ensure_ascii=False)}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'thinking', 'content': f'验证：{valid_count}/{total_attractions}个景点在目标区域'}, ensure_ascii=False)}\n\n"
        
        # 如果有无效景点，需要补全
        if invalid_count > 0:
                yield f"data: {json.dumps({'type': 'thinking', 'content': f'决策：保留AI推荐的景点，让用户在前端调整'}, ensure_ascii=False)}\n\n"
        
        # 6. 并行获取天气和优化路线（提速）
        yield f"data: {json.dumps({'type': 'thinking', 'content': '思考：景点信息已获取，开始并行处理：获取天气 + 优化路线'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'type': 'status', 'content': '⚡ 并行处理：获取天气 + TSP优化...'}, ensure_ascii=False)}\n\n"
        
        try:
            # 并行获取所有城市的天气（最多3个）
            weather_cities = destinations[:3] if destinations else [request.destination]
            print(f"[天气] 并行查询城市: {weather_cities}")
            
            # 并行调用（提升速度）
            weather_tasks = [map_service.get_weather(city) for city in weather_cities]
            weather_results = await asyncio.gather(*weather_tasks, return_exceptions=True)
            
            all_weather = {}
            for city, weather_info in zip(weather_cities, weather_results):
                if weather_info and not isinstance(weather_info, Exception):
                    all_weather[city] = weather_info
                elif isinstance(weather_info, Exception):
                    print(f"[天气] {city}查询异常: {weather_info}")
            
            if all_weather:
                # 显示所有城市的天气
                for city, weather in all_weather.items():
                    yield f"data: {json.dumps({'type': 'weather', 'city': city, 'data': weather}, ensure_ascii=False)}\n\n"
                
                forecasts_count = len(list(all_weather.values())[0].get('forecasts', []))
                cities_str = "、".join(all_weather.keys())
                status_msg = f'✅ 已获取{cities_str}未来{forecasts_count}天天气'
                yield f"data: {json.dumps({'type': 'status', 'content': status_msg}, ensure_ascii=False)}\n\n"
            else:
                print(f"[天气] 所有城市都未返回数据")
                yield f"data: {json.dumps({'type': 'thinking', 'content': '天气信息获取失败，继续规划'}, ensure_ascii=False)}\n\n"
        except Exception as e:
            print(f"[天气] 获取失败: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'thinking', 'content': '天气信息暂时无法获取'}, ensure_ascii=False)}\n\n"
        
        
        # 7. TSP优化（减少提示信息，加快处理）
        yield f"data: {json.dumps({'type': 'status', 'content': '🚀 优化路线顺序...'}, ensure_ascii=False)}\n\n"
        
        from app.services.route_planner import RoutePlanner
        route_planner = RoutePlanner()
        
        for day_idx, day in enumerate(itinerary.daily_schedule):
            if len(day.attractions) > 1:
                yield f"data: {json.dumps({'type': 'status', 'content': f'优化第{day.day}天（{len(day.attractions)}个景点）...'}, ensure_ascii=False)}\n\n"
                
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
                        optimized = await route_planner.optimize_route(
                            attractions_data,
                            budget=request.budget,
                            days=request.days
                        )
                        
                        optimization_rate = optimized['summary'].get('optimization_rate', 0)
                        yield f"data: {json.dumps({'type': 'tool_result', 'tool': 'optimize_route', 'output': {'day': day.day, 'optimization_rate': f'{optimization_rate:.1f}%'}}, ensure_ascii=False)}\n\n"
                        
                    except Exception as e:
                        yield f"data: {json.dumps({'type': 'error', 'content': f'第{day.day}天优化失败'}, ensure_ascii=False)}\n\n"
        
        # 8. 快速完成（合并多个步骤）
        total_cost = itinerary.cost_breakdown.total
        budget_status = '在预算内' if total_cost <= request.budget else f'超出¥{total_cost - request.budget}'
        
        yield f"data: {json.dumps({'type': 'thinking', 'content': f'完成：路线优化完成，总费用¥{total_cost}（{budget_status}）'}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'type': 'status', 'content': '✅ 行程生成完成！'}, ensure_ascii=False)}\n\n"
        
        # 9. 返回完整行程数据
        itinerary_dict = itinerary.model_dump()
        yield f"data: {json.dumps({'type': 'itinerary', 'data': itinerary_dict}, ensure_ascii=False)}\n\n"
        
        # 10. 发送完成信号
        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
        
    except Exception as e:
        error_msg = f"生成失败: {str(e)}"
        yield f"data: {json.dumps({'type': 'error', 'content': error_msg}, ensure_ascii=False)}\n\n"


@router.post("/chat/stream")
async def agent_chat_stream(request: StreamChatRequest):
    """
    流式Agent对话
    
    实时返回AI的思考过程、工具调用、API结果
    
    响应格式（Server-Sent Events）：
    ```
    data: {"type": "status", "content": "正在分析..."}
    
    data: {"type": "tool_result", "tool": "search_attractions", "output": {...}}
    
    data: {"type": "itinerary", "data": {...}}
    
    data: {"type": "done"}
    ```
    """
    return EventSourceResponse(generate_stream_response(request))

