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

## 4. 行程模块

### 3.1 创建行程

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

### 3.2 获取行程列表

```http
GET /trips/?skip=0&limit=20&destination=成都
```

### 3.3 获取单个行程

```http
GET /trips/{trip_id}
```

### 3.4 更新行程

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

### 3.5 删除行程

```http
DELETE /trips/{trip_id}
```

### 3.6 优化行程路径

```http
POST /trips/{trip_id}/optimize
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

