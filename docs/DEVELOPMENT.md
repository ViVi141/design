# 开发文档

## 环境准备

### 后端环境

1. **安装Python 3.10+**
   ```bash
   python --version  # 确保 >= 3.10
   ```

2. **创建虚拟环境**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   # 复制示例文件
   cp .env.example .env
   
   # 编辑 .env 文件，填入API密钥
   AMAP_API_KEY=你的高德地图API密钥
   DEEPSEEK_API_KEY=你的DeepSeek API密钥
   ```

5. **初始化数据库**
   ```bash
   cd ..
   python scripts/init_db.py
   ```

6. **启动后端服务**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

   访问 http://localhost:8000/docs 查看API文档

### 前端环境

1. **安装Node.js 18+**
   ```bash
   node --version  # 确保 >= 18
   ```

2. **安装pnpm**
   ```bash
   npm install -g pnpm
   ```

3. **安装依赖**
   ```bash
   cd frontend
   pnpm install
   ```

4. **配置环境变量**
   ```bash
   # 编辑 .env.development
   VITE_AMAP_KEY=你的高德地图Web端API密钥
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

5. **启动前端服务**
   ```bash
   pnpm dev
   ```

   访问 http://localhost:3000

## 项目结构

### 后端结构

```
backend/
├── app/
│   ├── api/v1/          # API路由
│   │   ├── agent.py                    # Agent基础API
│   │   ├── agent_stream.py             # Agent流式API
│   │   ├── agent_enhanced_stream.py    # Agent增强流式API
│   │   ├── attraction.py               # 景点API
│   │   ├── route.py                    # 路径规划API
│   │   ├── trip.py                     # 行程API
│   │   ├── chat.py                     # AI对话API
│   │   ├── city.py                     # 城市信息API
│   │   ├── location.py                 # IP定位API
│   │   ├── performance.py              # 性能监控API
│   │   └── enhanced_itinerary.py       # 完整行程API
│   ├── services/        # 业务逻辑
│   │   ├── agent_service.py (1297行)  # Agent服务(核心)
│   │   ├── map_service.py (789行)      # 地图服务
│   │   ├── route_planner.py (600行)    # 路径规划
│   │   ├── route_service.py            # 路线服务
│   │   ├── ai_service.py               # AI服务
│   │   ├── enhanced_ai_service.py      # 增强AI服务
│   │   ├── optimized_ai_base.py        # AI优化基类
│   │   ├── trip_service.py             # 行程服务
│   │   └── itinerary_validator.py      # 行程验证
│   ├── models/          # 数据库模型
│   │   ├── trip.py      # 行程模型
│   │   └── attraction.py # 景点模型
│   ├── schemas/         # Pydantic数据模式
│   │   ├── trip.py      # 行程Schema
│   │   ├── attraction.py # 景点Schema
│   │   └── chat.py      # 对话Schema
│   ├── core/            # 核心配置
│   │   ├── config.py    # 配置管理
│   │   ├── database.py  # 数据库连接
│   │   ├── city_mapping.py # 城市映射
│   │   ├── ip_utils.py  # IP工具
│   │   └── tool_monitor.py # 工具监控
│   └── main.py          # 应用入口
└── requirements.txt     # 依赖列表
```

### 前端结构

```
frontend/
├── src/
│   ├── views/           # 页面组件
│   │   ├── dashboard/   # 首页
│   │   │   └── DashboardView.vue
│   │   ├── planner/     # 智能规划器(核心)
│   │   │   └── UltimatePlannerView.vue (5400行)
│   │   ├── map/         # 地图浏览
│   │   │   └── MapView.vue
│   │   ├── chat/        # AI对话
│   │   │   └── ChatView.vue
│   │   └── trip/        # 行程管理
│   │       ├── TripList.vue
│   │       └── TripDetail.vue
│   ├── components/      # 组件库
│   │   ├── AttractionCard.vue
│   │   ├── airportCodes.ts
│   │   └── chinaRegions.ts
│   ├── api/             # API封装
│   │   ├── index.ts
│   │   ├── attraction.ts
│   │   ├── route.ts
│   │   ├── trip.ts
│   │   ├── chat.ts
│   │   ├── itinerary.ts
│   │   └── location.ts
│   ├── stores/          # Pinia状态管理
│   │   └── map.ts
│   ├── types/           # TypeScript类型
│   │   └── index.ts
│   ├── router/          # 路由配置
│   │   └── index.ts
│   ├── App.vue          # 根组件
│   └── main.ts          # 应用入口
├── package.json         # 依赖列表
└── vite.config.ts       # Vite配置
```

## 开发规范

### 代码风格

- **Python**: 遵循PEP 8规范
  - 使用type hints
  - 函数和类添加docstring
  - 4空格缩进
  
- **TypeScript**: 使用Google代码风格
  - 使用interface定义类型
  - 严格模式(strict: true)
  - 2空格缩进
  
- **Vue**: 使用Vue 3 Composition API
  - `<script setup lang="ts">`语法
  - 使用ref和reactive管理状态
  - 组件命名采用PascalCase

### Git提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具链相关
```

示例：
```bash
git commit -m "feat: 添加景点搜索功能"
git commit -m "fix: 修复TSP算法性能问题"
```

## 核心功能开发

### 1. 开发新的Agent工具

```python
# 1. 定义输入Schema
class NewToolInput(BaseModel):
    param1: str = Field(..., description="参数描述")
    param2: int = Field(10, description="默认值10")

# 2. 实现工具函数
async def new_tool_func(param1: str, param2: int = 10) -> str:
    """工具功能描述（供LLM理解）"""
    try:
        # 实现逻辑
        result = await some_api_call(param1, param2)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"工具调用失败: {str(e)}"

# 3. 包装工具
async def wrapped_new_tool(tool_input: str) -> str:
    params = json.loads(tool_input)
    return await new_tool_func(**params)

# 4. 添加到工具列表
Tool(
    name="new_tool",
    func=wrapped_new_tool,
    description='工具描述。输入JSON，例：{"param1": "值", "param2": 10}',
    coroutine=wrapped_new_tool
)
```

### 2. 开发新的API端点

```python
# backend/app/api/v1/new_module.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/list")
async def get_list(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """获取列表"""
    # 实现逻辑
    return {"data": []}

@router.post("/create")
async def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db)
):
    """创建项目"""
    # 实现逻辑
    return {"id": 1}
```

### 3. 添加新的Vue页面

```vue
<template>
  <div class="new-page">
    <el-card>
      <template #header>
        <h2>新页面标题</h2>
      </template>
      <div class="content">
        <!-- 页面内容 -->
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 状态管理
const data = ref([])

// 生命周期
onMounted(async () => {
  await loadData()
})

// 方法
async function loadData() {
  try {
    // API调用
    const response = await api.getData()
    data.value = response.data
  } catch (error) {
    ElMessage.error('加载失败')
  }
}
</script>

<style scoped>
.new-page {
  padding: 20px;
}
</style>
```

---

## 常见问题

### Q: 高德API调用失败？

A: 检查以下几点：
1. API密钥是否正确配置
2. 是否超过每日配额限制（300万次/天免费）
3. 网络连接是否正常
4. 检查citycode/adcode是否正确

### Q: TSP求解超时？

A: 优化策略：
1. 限制景点数量（建议≤12个）
2. 调整时间限制参数（settings.TSP_TIME_LIMIT）
3. 超过12个景点自动使用贪心算法
4. 检查距离矩阵是否正确

### Q: DeepSeek API费用问题？

A: 控制成本：
1. 启用智能缓存（默认开启，1小时TTL）
2. 优化Prompt减少token消耗
3. 设置AI_MAX_TOKENS限制输出长度
4. 查看缓存命中率：GET /api/v1/performance/cache/info

### Q: Agent执行超时？

A: 解决方案：
1. 检查AI_TIMEOUT配置（默认120秒）
2. 查看max_iterations是否足够
3. 使用简化的Prompt
4. 减少城市数量或天数

### Q: 前端build失败？

A: 检查：
1. Node.js版本 >= 18
2. 清理node_modules重新安装
3. 检查TypeScript类型错误
4. 查看Vite配置是否正确

## 调试技巧

### 后端调试

1. **查看日志**
   ```bash
   # FastAPI会在终端输出详细日志
   ```

2. **使用API文档测试**
   - 访问 http://localhost:8000/docs
   - 直接在Swagger UI中测试接口

3. **Python调试器**
   ```python
   import pdb; pdb.set_trace()
   ```

### 前端调试

1. **Vue DevTools**
   - 安装Chrome扩展
   - 查看组件状态和Pinia store

2. **网络请求**
   - Chrome DevTools -> Network
   - 查看API请求和响应

3. **Console日志**
   ```typescript
   console.log('调试信息', data)
   ```

## 性能优化

### 后端优化

1. **数据库查询**
   - 使用索引
   - 避免N+1查询
   - 实现分页

2. **API响应**
   - 启用GZIP压缩
   - 实现缓存机制
   - 异步处理耗时操作

3. **TSP算法**
   - 限制景点数量
   - 设置求解时间上限
   - 缓存距离矩阵

### 前端优化

1. **组件加载**
   - 路由懒加载
   - 图片懒加载

2. **地图性能**
   - 使用地图聚合
   - 限制同时显示的标记数量

3. **打包优化**
   - 代码分割
   - Tree shaking
   - 压缩资源

## 测试

### 后端测试

```bash
cd backend
pytest tests/
```

### 前端测试

```bash
cd frontend
pnpm test
```

## 调试技巧（扩展）

### Agent调试

```python
# 1. 启用详细日志
# backend/.env
DEBUG_AGENT=true      # Agent执行日志
DEBUG_TOOLS=true      # 工具调用日志
DEBUG_POI=true        # POI搜索日志
DEBUG_ROUTE=true      # 路线规划日志

# 2. 查看Agent思考过程
# 日志输出示例:
[Agent] 任务分析: 3个城市, 7天
[Agent] 预估工具调用: 28次
[Agent] 设置max_iterations: 140
[工具调用] search_attractions - 输入: {"city": "北京", ...}
[工具重试] get_weather 第1次失败，1.0秒后重试
[性能] ✓ chat: 45.2秒
```

### 性能分析

```bash
# 1. 查看性能统计
curl http://localhost:8000/api/v1/performance/stats

# 2. 查看缓存命中率
curl http://localhost:8000/api/v1/performance/cache/info

# 3. 清空缓存（测试用）
curl -X POST http://localhost:8000/api/v1/performance/cache/clear
```

### 前端调试

```javascript
// 1. 在浏览器控制台
// 查看Pinia状态
app._instance.appContext.config.globalProperties.$pinia.state.value

// 2. Vue DevTools
// 安装扩展后可以查看：
// - 组件树
// - 状态管理(Pinia)
// - 路由信息
// - 性能分析

// 3. 网络请求调试
// F12 -> Network -> XHR
// 查看所有API请求和响应
```

---

## 部署

### Docker部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 手动部署

参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## 贡献指南

### Pull Request流程

1. Fork项目
2. 创建feature分支
3. 提交代码
4. 创建Pull Request
5. 等待Review

### 代码审查标准

- [ ] 代码符合规范
- [ ] 添加了必要的注释
- [ ] 通过所有测试
- [ ] 更新了相关文档
- [ ] 没有引入新的linter错误

