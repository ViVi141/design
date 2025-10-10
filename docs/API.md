# API 文档

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **内容类型**: `application/json`

## 1. AI对话模块

### 1.1 AI对话

```http
POST /chat/chat
```

**请求体**:
```json
{
  "message": "我想去成都玩3天",
  "history": [
    {
      "role": "user",
      "content": "你好"
    },
    {
      "role": "assistant",
      "content": "你好！我是AI旅行助手"
    }
  ]
}
```

**响应**:
```json
{
  "message": "好的，我来帮你规划成都3日游...",
  "action": "reply"
}
```

### 1.2 提取旅行需求

```http
POST /chat/extract
```

**请求体**:
```json
{
  "message": "我想去成都玩3天，预算5000元，喜欢历史文化"
}
```

**响应**:
```json
{
  "destination": "成都",
  "days": 3,
  "budget": 5000,
  "preferences": ["历史", "文化"],
  "start_date": null
}
```

### 1.3 生成旅行攻略

```http
POST /chat/guide
```

**请求体**:
```json
{
  "destination": "成都",
  "days": 3,
  "attractions": [
    {"name": "宽窄巷子", "type": "历史"},
    {"name": "武侯祠", "type": "历史"}
  ]
}
```

**响应**:
```json
{
  "guide": "# 成都3日游攻略\n\n## 第一天\n..."
}
```

## 2. 景点模块

### 2.1 搜索景点 (POI Search 2.0 - v5) 🆕

```http
POST /attractions/search
```

**说明**: 使用高德地图v5 POI搜索2.0，返回更丰富的信息（评分、电话、营业时间、商圈等）

**请求体**:
```json
{
  "city": "成都",
  "keyword": "景点",
  "types": "110000",
  "limit": 25
}
```

**响应**:
```json
[
  {
    "id": "B001D0DH23",
    "name": "宽窄巷子",
    "lng": 104.065735,
    "lat": 30.673239,
    "city": "成都市",
    "address": "青羊区金河路口宽窄巷子",
    "type": "风景名胜",
    "rating": 4.5,
    "cost": "免费",
    "tel": "028-86259233"
  }
]
```

### 2.2 输入提示 (Input Tips) 🆕

```http
GET /attractions/tips?keywords=宽窄&city=成都&citylimit=true
```

**说明**: 实时搜索建议，用于自动补全

**参数**:
- `keywords`: 查询关键词
- `city`: 城市（可选）
- `datatype`: 数据类型 (all/poi/bus/busline)
- `citylimit`: 仅返回指定城市数据

**响应**:
```json
{
  "count": 5,
  "tips": [
    {
      "id": "B001D0DH23",
      "name": "宽窄巷子",
      "district": "青羊区",
      "adcode": "510105",
      "location": "104.065735,30.673239",
      "address": "青羊区金河路口",
      "typecode": "110000"
    }
  ]
}
```

### 2.3 周边搜索 (Around Search - v5) 🆕

```http
GET /attractions/around?location=104.065735,30.673239&keywords=美食&radius=1000
```

**说明**: 搜索指定坐标周边的POI

**参数**:
- `location`: 中心点坐标 "lng,lat"
- `keywords`: 搜索关键词
- `radius`: 搜索半径（米，默认1000）
- `sortrule`: 排序规则 (distance/weight)

**响应**: 同搜索景点

### 2.4 POI详情查询 (Detail Query - v5) 🆕

```http
GET /attractions/detail?ids=B001D0DH23|B001D0DH24
```

**说明**: 批量查询POI详细信息（最多10个）

**参数**:
- `ids`: POI ID，用|分隔

**响应**: 同搜索景点，但包含更详细信息

### 2.5 推荐景点

```http
GET /attractions/recommend?city=成都&preferences=历史,美食&limit=5
```

**响应**:
```json
{
  "recommendations": [
    {
      "id": "B001D0DH23",
      "name": "宽窄巷子",
      "rating": 4.5,
      "reason": "热门景点"
    }
  ]
}
```

## 3. 路径规划模块 🆕

### 3.1 路径规划 (Route Planning 2.0 - v5)

```http
POST /route/plan
```

**说明**: 使用高德地图v5路径规划2.0，支持5种出行方式

**请求体**:
```json
{
  "origin": "104.065735,30.673239",
  "destination": "104.079114,30.663297",
  "mode": "driving",
  "strategy": 0,
  "show_fields": "cost,tmcs,navi,cities"
}
```

**参数说明**:
- `mode`: 出行方式
  - `driving`: 驾车
  - `walking`: 步行
  - `transit`: 公共交通
  - `bicycling`: 骑行
  - `electrobike`: 电动车
- `strategy`: 策略（不同模式有不同策略）
  - 驾车: 0=速度优先, 1=费用优先, 2=距离优先, 3=不走高速等
  - 步行: 0=推荐路线
  - 公交: 0=最快捷, 1=最经济, 2=最少换乘等

**响应**:
```json
{
  "status": "success",
  "count": 1,
  "routes": [
    {
      "distance": 2500,
      "duration": 480,
      "strategy": "速度优先",
      "tolls": 0,
      "toll_distance": 0,
      "steps": [...],
      "cost": {
        "tolls": 0,
        "traffic_lights": 3,
        "duration": 480
      }
    }
  ]
}
```

### 3.2 获取策略列表

```http
GET /route/strategies
```

**响应**:
```json
{
  "driving": [
    {"value": 0, "label": "速度优先"},
    {"value": 1, "label": "费用优先"}
  ],
  "transit": [
    {"value": 0, "label": "最快捷"},
    {"value": 1, "label": "最经济"}
  ]
}
```

## 4. Agent智能规划模块 🤖

### 4.1 Agent对话 (基础版)

```http
POST /agent/chat
```

**说明**: 与AI Agent对话,Agent可主动调用工具获取真实数据

**请求体**:
```json
{
  "message": "我想去北京玩3天"
}
```

**响应**:
```json
{
  "reply": "好的,我来帮你规划北京3日游...",
  "intermediate_steps": [
    {
      "tool": "search_attractions",
      "input": {"city": "北京", "keyword": "景点", "limit": 10},
      "output": "[...]"
    }
  ],
  "tool_calls": [...]
}
```

### 4.2 Agent流式对话 🆕

```http
POST /agent/stream
```

**说明**: 实时展示Agent思考过程,使用SSE流式推送

**请求体**:
```json
{
  "message": "规划成都3日游,预算3000元",
  "destination": "成都",
  "days": 3,
  "budget": 3000,
  "preferences": ["美食", "历史"]
}
```

**响应(SSE流式)**:
```
data: {"type": "start", "content": "🤖 Agent开始执行..."}

data: {"type": "tool_start", "tool": "search_attractions", "input": {...}}

data: {"type": "tool_end", "tool": "search_attractions", "output": "..."}

data: {"type": "llm_stream", "content": "根据您的需求..."}

data: {"type": "itinerary", "data": {...}}

data: {"type": "done", "content": "✅ 完成"}
```

### 4.3 Agent增强流式 🆕

```http
POST /agent/enhanced-stream
```

**说明**: 增强版流式响应,展示更详细的AI思考过程

**请求体**: 同4.2

**响应类型**:
- `thinking` - AI思考过程
- `deepseek` - DeepSeek推理状态
- `tool_start` - 工具调用开始
- `tool_end` - 工具调用完成
- `llm_stream` - LLM输出流
- `itinerary` - 结构化行程数据
- `status` - 状态更新
- `done` - 完成

### 4.4 Agent可用工具

AI Agent可以主动调用以下工具:

#### 1. search_attractions - 搜索景点

```json
{
  "city": "北京",
  "keyword": "故宫",
  "limit": 5
}
```

#### 2. calculate_route - 计算路线

```json
{
  "origin": "故宫",
  "destination": "天安门",
  "city": "北京",
  "mode": "walking"  // walking, driving, transit, bicycling
}
```

#### 3. optimize_route - 优化顺序(TSP)

```json
{
  "attractions": ["故宫", "天安门", "王府井"],
  "city": "北京"
}
```

#### 4. search_hotels - 搜索住宿

```json
{
  "city": "北京",
  "location": "市中心",
  "price_range": "经济型",
  "limit": 5
}
```

#### 5. get_weather - 获取天气

```json
{
  "city": "北京"
}
```

#### 6. get_multi_weather - 批量获取天气(并行)

```json
{
  "cities": ["北京", "上海", "广州"]
}
```

#### 7. search_food - 搜索美食

```json
{
  "city": "北京",
  "cuisine": "烤鸭",
  "limit": 5
}
```

#### 8. get_city_info - 获取城市信息

```json
{
  "city": "北京"
}
```

---

## 5. 行程模块

### 5.1 创建行程

```http
POST /trips/?optimize=true
```

**请求体**:
```json
{
  "title": "成都3日游",
  "destination": "成都",
  "days": 3,
  "budget": 5000,
  "attractions": [
    {
      "name": "宽窄巷子",
      "lng": 104.065735,
      "lat": 30.673239,
      "type": "风景名胜",
      "address": "青羊区金河路口宽窄巷子"
    }
  ]
}
```

**响应**:
```json
{
  "id": 1,
  "title": "成都3日游",
  "destination": "成都",
  "days": 3,
  "budget": 5000,
  "attractions": [...],
  "routes": [...],
  "summary": {
    "num_attractions": 5,
    "total_distance_km": 12.5,
    "total_duration_hours": 3.2,
    "total_cost": 200,
    "optimization_rate": 35.5
  },
  "status": "draft",
  "created_at": "2025-10-09T12:00:00",
  "updated_at": "2025-10-09T12:00:00"
}
```

### 5.2 获取行程列表

```http
GET /trips/?skip=0&limit=20&destination=成都
```

### 5.3 获取单个行程

```http
GET /trips/{trip_id}
```

### 5.4 更新行程

```http
PUT /trips/{trip_id}
```

**请求体**:
```json
{
  "title": "成都4日游",
  "status": "confirmed"
}
```

### 5.5 删除行程

```http
DELETE /trips/{trip_id}
```

### 5.6 优化行程路径

```http
POST /trips/{trip_id}/optimize
```

---

## 6. 性能监控模块 🆕

### 6.1 获取性能统计

```http
GET /performance/stats
```

**响应**:
```json
{
  "overall": {
    "total_calls": 150,
    "success_rate": 98.5,
    "avg_duration": 2.3,
    "min_duration": 0.01,
    "max_duration": 8.5
  },
  "by_operation": {
    "chat": {
      "total_calls": 80,
      "success_rate": 99.0,
      "avg_duration": 1.5
    }
  }
}
```

### 6.2 获取缓存信息

```http
GET /performance/cache/info
```

**响应**:
```json
{
  "cache_size": 45,
  "cache_hits": 120,
  "cache_misses": 30,
  "hit_rate": 80.0
}
```

### 6.3 清空缓存

```http
POST /performance/cache/clear
```

---

## 7. 城市信息模块 🆕

### 7.1 获取支持的城市列表

```http
GET /cities/supported
```

**响应**:
```json
{
  "cities": [
    {"name": "北京", "citycode": "010", "adcode": "110000"},
    {"name": "上海", "citycode": "021", "adcode": "310000"}
  ],
  "total": 100
}
```

---

## 8. IP定位模块 🆕

### 8.1 根据IP获取位置

```http
GET /location/by-ip?ip=1.2.3.4
```

**说明**: 如果不传ip参数,高德API会自动使用请求来源IP

**响应**:
```json
{
  "province": "北京",
  "city": "北京市",
  "adcode": "110000",
  "location": [116.4074, 39.9042]
}
```

## 错误响应

所有API在发生错误时返回以下格式：

```json
{
  "detail": "错误信息"
}
```

常见HTTP状态码：
- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

