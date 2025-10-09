"""
增强版AI服务：生成完整行程（景点+住宿+交通）
"""
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import json
import httpx

from app.core.config import settings


class AttractionSchedule(BaseModel):
    """景点时间安排"""
    name: str = Field(..., description="景点名称")
    start_time: str = Field(..., description="开始时间，如'09:00'")
    duration_hours: float = Field(..., description="游玩时长（小时）")
    cost: float = Field(..., description="门票费用")
    tips: str = Field("", description="游玩提示")
    # 以下字段由后端填充（v5 POI 2.0新增字段）
    address: Optional[str] = Field(None, description="景点地址")
    lng: Optional[float] = Field(None, description="经度")
    lat: Optional[float] = Field(None, description="纬度")
    type: Optional[str] = Field(None, description="景点类型")
    rating: Optional[float] = Field(None, description="评分（v5新增）")
    tel: Optional[str] = Field(None, description="电话（v5新增）")
    opentime: Optional[str] = Field(None, description="营业时间（v5新增）")
    business_area: Optional[str] = Field(None, description="所属商圈（v5新增）")


class HotelInfo(BaseModel):
    """住宿信息"""
    name: str = Field(..., description="酒店名称")
    price_per_night: float = Field(..., description="每晚价格")
    address: str = Field(..., description="酒店地址")
    reason: str = Field("", description="推荐理由")


class TransportInfo(BaseModel):
    """交通信息"""
    type: str = Field(..., description="交通方式：地铁/公交/出租车/步行/高铁/飞机")
    route: Optional[str] = Field(None, description="线路号或车次")
    from_location: str = Field(..., description="出发地")
    to_location: str = Field(..., description="目的地")
    cost: float = Field(..., description="费用")
    tips: str = Field("", description="交通提示")


class DaySchedule(BaseModel):
    """每日行程"""
    day: int = Field(..., description="第几天")
    date: Optional[str] = Field(None, description="日期")
    attractions: List[AttractionSchedule] = Field(..., description="景点安排")
    hotel: Optional[HotelInfo] = Field(None, description="住宿信息（最后一天无住宿）")
    transportation: List[TransportInfo] = Field(default_factory=list, description="交通方式")
    meals_budget: float = Field(..., description="餐饮预算")


class CostBreakdown(BaseModel):
    """费用明细"""
    attractions: float = Field(..., description="景点门票总计")
    hotels: float = Field(..., description="住宿总计")
    transportation: float = Field(..., description="交通总计")
    meals: float = Field(..., description="餐饮总计")
    total: float = Field(..., description="总计")
    remaining: float = Field(..., description="剩余预算")


class CompleteItinerary(BaseModel):
    """完整行程方案"""
    daily_schedule: List[DaySchedule] = Field(..., description="每日行程")
    cost_breakdown: CostBreakdown = Field(..., description="费用明细")
    packing_list: List[str] = Field(default_factory=list, description="行李清单")
    travel_tips: str = Field("", description="旅行建议")


class EnhancedAIService:
    """增强版AI服务"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.DEEPSEEK_MODEL,
            openai_api_key=settings.DEEPSEEK_API_KEY,
            openai_api_base=settings.DEEPSEEK_API_BASE,
            temperature=0.7,
            model_kwargs={"response_format": {"type": "json_object"}}  # 强制JSON输出
        )
        
        # 流式LLM（不强制JSON格式）
        self.streaming_llm = ChatOpenAI(
            model=settings.DEEPSEEK_MODEL,
            openai_api_key=settings.DEEPSEEK_API_KEY,
            openai_api_base=settings.DEEPSEEK_API_BASE,
            temperature=0.7,
            streaming=True  # 启用流式输出
        )
    
    async def generate_complete_itinerary_stream(
        self,
        destination: str,
        days: int,
        budget: float,
        preferences: List[str] = None,
        start_date: Optional[str] = None
    ):
        """
        流式生成行程（直接调用OpenAI兼容API获取实时输出）
        
        Yields:
            str: DeepSeek的实时输出片段
        """
        print(f"[流式API] 开始生成行程: {destination}, {days}天, ¥{budget}")
        
        # 构建提示词
        prompt = self._build_prompt_template()
        
        # 计算参数
        hotel_nights = max(0, days - 1)
        preferences_str = "、".join(preferences) if preferences else "无特殊偏好，推荐必游景点"
        start_date_str = start_date if start_date else "待定"
        
        # 格式化消息
        messages = prompt.format_messages(
            destination=destination,
            days=days,
            budget=budget,
            preferences=preferences_str,
            start_date=start_date_str,
            hotel_nights=hotel_nights
        )
        
        # 转换为字典格式（OpenAI API格式）
        messages_dict = []
        for m in messages:
            role = "system" if m.type == "system" else "user" if m.type == "human" else "assistant"
            messages_dict.append({"role": role, "content": m.content})
        
        print(f"[流式API] 准备发送 {len(messages_dict)} 条消息到DeepSeek")
        
        # 使用httpx直接调用DeepSeek流式API
        import httpx
        
        try:
            print("[流式API] 直接调用DeepSeek API...")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    'POST',
                    f"{settings.DEEPSEEK_API_BASE}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.DEEPSEEK_MODEL,
                        "messages": messages_dict,
                        "temperature": 0.7,
                        "stream": True
                    }
                ) as response:
                    print(f"[流式API] DeepSeek响应状态: {response.status_code}")
                    
                    if response.status_code != 200:
                        error_text = await response.aread()
                        print(f"[流式API] 错误响应: {error_text}")
                        raise Exception(f"DeepSeek API错误: {response.status_code}")
                    
                    chunk_count = 0
                    async for line in response.aiter_lines():
                        if line.strip():
                            if line.startswith('data: '):
                                data_str = line[6:]
                                if data_str == '[DONE]':
                                    print("[流式API] DeepSeek发送完成信号")
                                    break
                                
                                try:
                                    data = json.loads(data_str)
                                    if 'choices' in data and len(data['choices']) > 0:
                                        delta = data['choices'][0].get('delta', {})
                                        content = delta.get('content', '')
                                        
                                        if content:
                                            chunk_count += 1
                                            if chunk_count <= 5 or chunk_count % 10 == 0:
                                                print(f"[流式API] Chunk {chunk_count}: {content[:30]}...")
                                            yield content
                                except json.JSONDecodeError:
                                    continue
                    
                    print(f"[流式API] 完成，共收到 {chunk_count} 个有效chunks")
                    
        except Exception as e:
            print(f"[流式API] 错误: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def generate_complete_itinerary(
        self,
        destination: str,
        days: int,
        budget: float,
        preferences: List[str] = None,
        start_date: Optional[str] = None
    ) -> CompleteItinerary:
        """
        生成完整行程方案
        
        Args:
            destination: 目的地城市
            days: 旅行天数
            budget: 总预算（元）
            preferences: 用户偏好，如["历史文化", "自然风光", "美食"]
            start_date: 出发日期（可选）
            
        Returns:
            完整结构化的行程方案
        """
        
        # 构建详细的提示词
        prompt = self._build_prompt_template()
        
        # 计算住宿晚数
        hotel_nights = max(0, days - 1)
        
        # 格式化偏好
        preferences_str = "、".join(preferences) if preferences else "无特殊偏好，推荐必游景点"
        start_date_str = start_date if start_date else "待定"
        
        # 调用AI
        try:
            response = await self.llm.ainvoke(
                prompt.format_messages(
                    destination=destination,
                    days=days,
                    budget=budget,
                    preferences=preferences_str,
                    start_date=start_date_str,
                    hotel_nights=hotel_nights
                )
            )
            
            # 解析JSON响应
            content = response.content
            
            # 如果返回的内容包含markdown代码块，提取JSON部分
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # 解析为字典
            data = json.loads(content)
            
            # 验证和转换为Pydantic模型
            itinerary = CompleteItinerary.model_validate(data)
            
            return itinerary
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"原始响应: {content}")
            raise ValueError(f"AI返回的不是有效JSON格式: {str(e)}")
        
        except Exception as e:
            print(f"生成行程失败: {e}")
            raise
    
    def _build_prompt_template(self) -> ChatPromptTemplate:
        """构建提示词模板"""
        return ChatPromptTemplate.from_messages([
            ("system", """你是一位经验丰富的旅行规划专家。
你的任务是为用户生成一份详细、实用、可直接执行的旅行计划。

核心原则：
1. 行程安排要紧凑但不紧张，每天2-4个景点
2. 景点之间距离合理，交通便利
3. 住宿位置优先考虑交通便利性
4. 严格控制预算，留10%余量
5. 提供实用的旅行建议

【输出要求】
第一步：简要说明你的规划思路（1-2句话）
第二步：返回完整的JSON格式数据

例如：
根据您的需求，我为您规划了一个3天的北京之旅，重点游览历史文化景点，总预算控制在3000元以内。

```json
{...}
```
"""),
            
               ("user", """请为我生成{destination}{days}天的详细旅行计划。
       
       【我的需求】
       - 目的地：{destination}
       - 天数：{days}天
       - 总预算：{budget}元（含景点、住宿、交通、餐饮）
       - 偏好：{preferences}
       - 出发日期：{start_date}
       
       【重要提示】
       如果目的地包含多个城市（用"、"分隔），请按以下原则规划：
       1. 合理分配每个城市的天数（根据总天数和城市数量）
       2. 每个城市安排该城市的特色景点，不要混淆
       3. 城际交通要考虑从一个城市到另一个城市的转移
       4. 住宿安排要考虑城市切换的时机
       
       【具体要求】
       1. **景点安排**：
          - 每天安排2-4个景点，标注开始时间和游玩时长
          - 景点必须属于当天所在的城市，不要跨城市安排
          - 景点之间距离不要太远，优化游览路线
          - 包含门票价格和游玩提示
          - 考虑景点的最佳游览时间
       
       2. **住宿推荐**：
          - 推荐{hotel_nights}晚住宿
          - 选择性价比高的酒店（经济型或快捷酒店）
          - 位置要交通便利，靠近地铁或景区
          - 如果第二天要换城市，选择靠近火车站/机场的酒店
          - 说明推荐理由
       
       3. **交通方式**：
          - 城际交通（如从外地到{destination}，或城市间转移）
          - 市内交通建议（地铁/公交优先，考虑换乘便利性）
          - 景点间交通方式（根据距离选择步行1.5km以内/地铁公交1.5-10km/出租车10km以上）
          - 标注交通费用
          - 提供实用的交通提示（如推荐交通卡、换乘站点等）

4. **费用控制**：
   - 景点门票总计
   - 住宿费用总计
   - 交通费用总计
   - 餐饮费用预估（早中晚餐）
   - 总费用应在预算{budget}元以内，留出10%余量

5. **实用建议**：
   - 行李打包清单
   - 旅行注意事项
   - 天气和穿衣建议

【输出格式】严格按以下JSON格式输出：

```json
{{
  "daily_schedule": [
    {{
      "day": 1,
      "date": "2025-10-10",
      "attractions": [
        {{
          "name": "天安门广场",
          "start_time": "09:00",
          "duration_hours": 1.0,
          "cost": 0,
          "tips": "建议早上8点前到达，避开人流高峰，可以看升旗仪式"
        }},
        {{
          "name": "故宫博物院",
          "start_time": "10:30",
          "duration_hours": 3.0,
          "cost": 60,
          "tips": "提前网上购票，从午门进入，建议租讲解器"
        }},
        {{
          "name": "景山公园",
          "start_time": "14:00",
          "duration_hours": 1.5,
          "cost": 2,
          "tips": "可以俯瞰故宫全景，拍照的好地方"
        }}
      ],
      "hotel": {{
        "name": "7天连锁酒店(王府井店)",
        "price_per_night": 200,
        "address": "东城区王府井大街88号",
        "reason": "地铁1号线王府井站A口100米，去各景点都方便，周边餐饮丰富"
      }},
      "transportation": [
        {{
          "type": "地铁",
          "route": "1号线",
          "from_location": "天安门广场",
          "to_location": "故宫博物院",
          "cost": 3,
          "tips": "1号线天安门东站下，A口出，步行5分钟。建议购买北京市政交通一卡通可打折"
        }},
        {{
          "type": "步行",
          "route": null,
          "from_location": "故宫博物院",
          "to_location": "景山公园",
          "cost": 0,
          "tips": "从故宫神武门出，过马路即到景山公园南门，步行约5分钟"
        }},
        {{
          "type": "地铁",
          "route": "5号线",
          "from_location": "景山公园",
          "to_location": "酒店",
          "cost": 3,
          "tips": "景山东街站乘5号线，2站后到东单站换乘1号线"
        }}
      ],
      "meals_budget": 150
    }}
  ],
  "cost_breakdown": {{
    "attractions": 300,
    "hotels": 400,
    "transportation": 200,
    "meals": 600,
    "total": 1500,
    "remaining": 500
  }},
  "packing_list": ["身份证", "充电器", "充电宝", "雨伞", "防晒霜", "常用药品", "相机"],
  "travel_tips": "北京秋季早晚温差大，建议带件外套。故宫周一闭馆，注意避开。建议下载高德地图和大众点评APP。"
}}
```

请严格按照上述JSON格式返回，确保所有字段都存在，不要有任何额外的文字说明。
""")
        ])
    
    async def optimize_itinerary_with_context(
        self,
        current_itinerary: CompleteItinerary,
        optimization_goal: str
    ) -> CompleteItinerary:
        """
        基于现有行程进行优化
        
        Args:
            current_itinerary: 当前行程
            optimization_goal: 优化目标，如"减少预算"、"增加景点"、"优化路线"
            
        Returns:
            优化后的行程
        """
        
        prompt = f"""
        当前行程：
        {current_itinerary.model_dump_json(indent=2)}
        
        优化目标：{optimization_goal}
        
        请基于当前行程进行优化，返回新的完整行程JSON。
        """
        
        # 调用AI优化
        response = await self.llm.ainvoke(prompt)
        optimized = CompleteItinerary.model_validate_json(response.content)
        
        return optimized
    
    async def add_hotel_recommendation(
        self,
        destination: str,
        central_location: str,
        budget_per_night: float,
        nights: int
    ) -> List[HotelInfo]:
        """
        推荐住宿
        
        Args:
            destination: 目的地
            central_location: 中心区域
            budget_per_night: 每晚预算
            nights: 住宿晚数
            
        Returns:
            酒店推荐列表
        """
        
        prompt = f"""
        请推荐{destination}{central_location}附近的3家酒店：
        - 每晚预算：{budget_per_night}元
        - 住{nights}晚
        - 要求：交通便利、性价比高、评价好
        
        返回JSON格式：
        [
          {{"name": "酒店名", "price_per_night": 200, "address": "地址", "reason": "推荐理由"}}
        ]
        """
        
        response = await self.llm.ainvoke(prompt)
        hotels = [HotelInfo.model_validate(h) for h in json.loads(response.content)]
        
        return hotels
    
    async def suggest_transportation(
        self,
        from_city: str,
        to_city: str,
        date: str,
        budget: float
    ) -> List[TransportInfo]:
        """
        建议城际交通方式
        
        Args:
            from_city: 出发城市
            to_city: 目的地城市
            date: 出发日期
            budget: 交通预算
            
        Returns:
            交通建议列表
        """
        
        prompt = f"""
        请推荐从{from_city}到{to_city}的交通方式：
        - 日期：{date}
        - 预算：{budget}元
        
        推荐2-3种方案（高铁、飞机、大巴），说明：
        1. 车次/航班号（示例即可）
        2. 大概时间和价格
        3. 优缺点
        
        返回JSON格式：
        [
          {{
            "type": "高铁",
            "route": "G101（示例）",
            "from_location": "{from_city}",
            "to_location": "{to_city}",
            "cost": 500,
            "tips": "耗时5小时，舒适便捷，建议提前订票"
          }}
        ]
        """
        
        response = await self.llm.ainvoke(prompt)
        transport_options = [TransportInfo.model_validate(t) for t in json.loads(response.content)]
        
        return transport_options

