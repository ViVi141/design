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

### 2.1 搜索景点

```http
POST /attractions/search
```

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

### 2.2 推荐景点

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

## 3. 行程模块

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

