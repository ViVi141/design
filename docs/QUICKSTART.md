# ⚡ 快速开始

## 5分钟启动项目

### 前置要求

- **Python**: 3.13+
- **Node.js**: 18+
- **pnpm**: 8+

### 步骤1: 克隆项目

```bash
git clone <your-repo-url>
cd design
```

### 步骤2: 配置环境变量

#### 后端 `.env`

```bash
# 创建 backend/.env
cat > backend/.env << EOF
PROJECT_NAME=智能旅行规划系统
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
DATABASE_URL=sqlite:///./data/app.db

# 高德地图API
AMAP_API_KEY=你的高德地图KEY
AMAP_SECRET_KEY=你的安全密钥

# DeepSeek AI
DEEPSEEK_API_KEY=你的DeepSeekKEY
DEEPSEEK_API_BASE=https://api.deepseek.com
EOF
```

#### 前端 `.env`

```bash
# 创建 frontend/.env
cat > frontend/.env << EOF
VITE_API_BASE_URL=/api/v1
VITE_AMAP_KEY=你的高德地图KEY
VITE_AMAP_SECRET=你的安全密钥
EOF
```

### 步骤3: 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
pnpm install
```

### 步骤4: 初始化数据库

```bash
cd scripts
python init_db.py
```

### 步骤5: 启动服务

#### 方式1：一键启动（推荐）

```powershell
.\start_all.ps1
```

#### 方式2：手动启动

```bash
# 终端1 - 后端
cd backend
uvicorn app.main:app --reload

# 终端2 - 前端
cd frontend
pnpm dev
```

### 步骤6: 访问应用

- **前端**: http://localhost:3000
- **API文档**: http://localhost:8000/docs
- **智能规划器**: http://localhost:3000/planner

---

## 🎯 第一次使用

### 1. 打开智能规划器

访问：http://localhost:3000/planner

### 2. 快速生成行程

```
1. 输入目的地：北京
2. 输入天数：3
3. 输入预算：5000
4. 点击"AI一键生成行程"
5. 等待30秒
6. ✅ 完成！10个景点自动添加
```

### 3. 手动调整

```
- 从"待安排"拖拽景点到各天
- 点击"智能优化"优化路线
- 添加备注
- 保存行程
```

---

## 🐛 常见问题

### Q1: 后端启动失败？

**检查**：
```bash
# 确认Python版本
python --version  # 应该是3.13+

# 确认依赖已安装
pip list | grep fastapi
```

### Q2: 前端启动失败？

**检查**：
```bash
# 确认Node版本
node --version  # 应该是18+

# 重新安装依赖
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Q3: AI功能不工作？

**检查**：
1. 确认 `DEEPSEEK_API_KEY` 已配置
2. 查看后端日志
3. 测试API：http://localhost:8000/docs

### Q4: 地图不显示？

**检查**：
1. 确认高德地图API密钥
2. 确认安全密钥配置
3. F12查看控制台错误

---

## 📚 下一步

- [开发指南](DEVELOPMENT.md) - 详细开发文档
- [API文档](API.md) - 后端API说明
- [智能规划器](SMART_PLANNER_GUIDE.md) - V3使用指南
- [部署指南](DEPLOYMENT.md) - 生产环境部署

---

**更新时间**: 2025-10-09  
**版本**: V3.0

