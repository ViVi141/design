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
│   │   ├── chat.py      # AI对话接口
│   │   ├── attraction.py # 景点接口
│   │   └── trip.py      # 行程接口
│   ├── services/        # 业务逻辑
│   │   ├── ai_service.py       # AI服务
│   │   ├── map_service.py      # 地图服务
│   │   ├── route_planner.py    # 路径规划
│   │   └── trip_service.py     # 行程服务
│   ├── models/          # 数据库模型
│   │   ├── trip.py      # 行程模型
│   │   └── attraction.py # 景点模型
│   ├── schemas/         # Pydantic数据模式
│   ├── core/            # 核心配置
│   │   ├── config.py    # 配置管理
│   │   └── database.py  # 数据库连接
│   └── main.py          # 应用入口
└── requirements.txt     # 依赖列表
```

### 前端结构

```
frontend/
├── src/
│   ├── views/           # 页面组件
│   │   ├── dashboard/   # 首页
│   │   ├── map/         # 地图规划
│   │   ├── chat/        # AI对话
│   │   └── trip/        # 行程管理
│   ├── api/             # API封装
│   ├── stores/          # Pinia状态管理
│   ├── router/          # 路由配置
│   ├── App.vue          # 根组件
│   └── main.ts          # 应用入口
└── package.json         # 依赖列表
```

## 开发规范

### 代码风格

- **Python**: 遵循PEP 8规范
- **TypeScript**: 使用Google代码风格
- **Vue**: 使用Vue 3 Composition API

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

## 常见问题

### Q: 高德API调用失败？

A: 检查以下几点：
1. API密钥是否正确配置
2. 是否超过每日配额限制
3. 网络连接是否正常

### Q: TSP求解超时？

A: 优化策略：
1. 限制景点数量（建议≤12个）
2. 调整时间限制参数
3. 使用贪心算法作为备用

### Q: DeepSeek API费用问题？

A: 控制成本：
1. 缓存常见问题的回复
2. 优化Prompt减少token消耗
3. 设置API调用次数限制

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

