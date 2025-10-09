# 部署文档

## Docker部署（推荐）

### 1. 准备工作

确保服务器已安装：
- Docker 20+
- Docker Compose 2.0+

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# 高德地图API
AMAP_API_KEY=你的高德API密钥

# DeepSeek API
DEEPSEEK_API_KEY=你的DeepSeek API密钥

# 数据库
DATABASE_URL=sqlite:///./data/app.db
```

### 3. 启动服务

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 4. 访问应用

- 前端：http://localhost:3000
- 后端API文档：http://localhost:8000/docs

### 5. 停止服务

```bash
docker-compose down
```

## 手动部署

### 后端部署

#### 1. 环境准备

```bash
# 安装Python 3.10+
sudo apt update
sudo apt install python3.10 python3.10-venv

# 创建用户
sudo useradd -m -s /bin/bash travelapp
sudo su - travelapp
```

#### 2. 部署应用

```bash
# 克隆代码
git clone <repository_url>
cd travel-planning-system/backend

# 创建虚拟环境
python3.10 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 初始化数据库
cd ..
python scripts/init_db.py
```

#### 3. 使用Systemd管理服务

创建 `/etc/systemd/system/travelapp.service`：

```ini
[Unit]
Description=Travel Planning API
After=network.target

[Service]
Type=simple
User=travelapp
WorkingDirectory=/home/travelapp/travel-planning-system/backend
Environment="PATH=/home/travelapp/travel-planning-system/backend/venv/bin"
ExecStart=/home/travelapp/travel-planning-system/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable travelapp
sudo systemctl start travelapp
sudo systemctl status travelapp
```

### 前端部署

#### 1. 构建前端

```bash
cd frontend

# 安装依赖
pnpm install

# 构建生产版本
pnpm build
```

#### 2. Nginx配置

安装Nginx：

```bash
sudo apt install nginx
```

创建配置文件 `/etc/nginx/sites-available/travelapp`：

```nginx
server {
    listen 80;
    server_name your_domain.com;

    root /var/www/travelapp;
    index index.html;

    # 前端静态文件
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 代理API请求到后端
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Gzip压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

启用站点：

```bash
# 复制构建文件
sudo mkdir -p /var/www/travelapp
sudo cp -r frontend/dist/* /var/www/travelapp/

# 启用站点
sudo ln -s /etc/nginx/sites-available/travelapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL证书（可选）

使用Let's Encrypt免费证书：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

## 监控和日志

### 查看后端日志

```bash
# Systemd服务日志
sudo journalctl -u travelapp -f

# 或查看应用日志
tail -f /home/travelapp/travel-planning-system/backend/logs/app.log
```

### 查看Nginx日志

```bash
# 访问日志
sudo tail -f /var/log/nginx/access.log

# 错误日志
sudo tail -f /var/log/nginx/error.log
```

### 性能监控

使用 `htop` 监控系统资源：

```bash
sudo apt install htop
htop
```

## 备份

### 数据库备份

```bash
# 备份SQLite数据库
cp /home/travelapp/travel-planning-system/data/app.db \
   /home/travelapp/backups/app_$(date +%Y%m%d).db
```

### 自动备份脚本

创建 `/home/travelapp/backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/home/travelapp/backups"
DB_PATH="/home/travelapp/travel-planning-system/data/app.db"

mkdir -p $BACKUP_DIR

# 备份数据库
cp $DB_PATH $BACKUP_DIR/app_$(date +%Y%m%d_%H%M%S).db

# 删除7天前的备份
find $BACKUP_DIR -name "app_*.db" -mtime +7 -delete
```

添加定时任务：

```bash
crontab -e

# 每天凌晨2点备份
0 2 * * * /home/travelapp/backup.sh
```

## 安全建议

1. **防火墙配置**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

2. **限制API访问频率**
   - 在Nginx中配置rate limiting

3. **定期更新**
   ```bash
   sudo apt update
   sudo apt upgrade
   ```

4. **API密钥安全**
   - 不要将密钥提交到Git
   - 使用环境变量管理
   - 定期轮换密钥

## 故障排查

### 后端无法启动

```bash
# 检查服务状态
sudo systemctl status travelapp

# 查看详细日志
sudo journalctl -u travelapp -n 50

# 检查端口占用
sudo lsof -i :8000
```

### 前端无法访问

```bash
# 检查Nginx状态
sudo systemctl status nginx

# 测试配置
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

### 数据库问题

```bash
# 检查数据库文件
ls -lh /home/travelapp/travel-planning-system/data/

# 重新初始化
python scripts/init_db.py
```

## 性能优化

### 后端优化

1. **使用Gunicorn运行**
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **配置进程数**
   - CPU密集：进程数 = CPU核心数
   - IO密集：进程数 = CPU核心数 × 2

### 前端优化

1. **启用CDN**
   - 使用阿里云OSS存储静态资源

2. **资源压缩**
   - 已在Nginx中配置Gzip

3. **浏览器缓存**
   ```nginx
   location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

## 扩展方案

### 负载均衡

使用Nginx实现负载均衡：

```nginx
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

### 数据库升级

如需升级到PostgreSQL：

1. 安装PostgreSQL
2. 修改 `DATABASE_URL`
3. 运行迁移脚本

