# 🚀 PR Codex Reviewer - 部署指南

## 📋 目录

1. [部署要求](#部署要求)
2. [本地部署](#本地部署)
3. [Docker部署](#docker部署)
4. [云平台部署](#云平台部署)
5. [GitHub Webhook配置](#github-webhook配置)
6. [监控和日志](#监控和日志)
7. [故障排除](#故障排除)

---

## 部署要求

### 系统要求

| 资源 | 最低要求 | 推荐配置 |
|------|---------|---------|
| CPU | 1核 | 2核+ |
| 内存 | 512MB | 1GB+ |
| 磁盘 | 1GB | 5GB+ |
| 网络 | 公网IP或域名 | 域名+HTTPS |

### 软件要求

- Python 3.11+
- pip
- Git
- （可选）Docker 20.10+
- （可选）Docker Compose 2.0+

### 必需账户

1. **GitHub账号** - 用于访问仓库API
2. **OpenAI账号** - 用于代码分析（可选，但推荐）

---

## 本地部署

### 1. 下载代码

```bash
# 克隆仓库
git clone https://github.com/changsheng0804-blip/pr-codex-reviewer.git
cd pr-codex-reviewer
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 安装生产依赖
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制示例文件
cp .env.example .env

# 编辑配置文件
# Windows:
notepad .env
# macOS/Linux:
nano .env
```

**最小配置**:
```env
# 必需配置
OPENAI_API_KEY=sk-your-openai-key
GITHUB_TOKEN=ghp-your-github-token

# 可选配置
PORT=8000
HOST=0.0.0.0
DEBUG=false
```

### 5. 启动服务

```bash
# 启动开发服务器
python -m src.main

# 或使用gunicorn（生产环境）
gunicorn -w 4 -b 0.0.0.0:8000 src.main:app
```

### 6. 验证部署

```bash
# 测试健康检查端点
curl http://localhost:8000/

# 预期响应
{"status":"healthy","service":"pr-codex-reviewer","version":"1.0.0"}
```

---

## Docker部署

### 1. 构建镜像

```bash
# 构建Docker镜像
docker build -t pr-codex-reviewer .

# 查看构建的镜像
docker images | grep pr-codex-reviewer
```

### 2. 运行容器

```bash
# 运行容器
docker run -d \
  --name pr-codex-reviewer \
  -p 8000:8000 \
  -e OPENAI_API_KEY=sk-your-key \
  -e GITHUB_TOKEN=ghp-your-token \
  pr-codex-reviewer

# 查看运行状态
docker ps | grep pr-codex-reviewer

# 查看日志
docker logs -f pr-codex-reviewer
```

### 3. 使用Docker Compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: pr-codex-reviewer
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - GITHUB_WEBHOOK_SECRET=${GITHUB_WEBHOOK_SECRET}
      - DEBUG=false
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # 可选：添加反向代理
  nginx:
    image: nginx:alpine
    container_name: pr-codex-reviewer-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    restart: unless-stopped
```

启动服务:

```bash
# 创建环境变量文件
echo "OPENAI_API_KEY=sk-your-key" > .env
echo "GITHUB_TOKEN=ghp-your-token" >> .env

# 启动服务
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

### 4. 更新部署

```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build

# 重启服务
docker-compose up -d

# 清理旧镜像
docker image prune -f
```

---

## 云平台部署

### Heroku部署

#### 1. 准备工作

```bash
# 安装Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 登录Heroku
heroku login

# 创建应用
heroku create your-app-name
```

#### 2. 配置环境变量

```bash
# 设置环境变量
heroku config:set OPENAI_API_KEY=sk-your-key
heroku config:set GITHUB_TOKEN=ghp-your-token
heroku config:set GITHUB_WEBHOOK_SECRET=your-secret
```

#### 3. 部署

```bash
# 添加Heroku远程仓库
heroku git:remote -a your-app-name

# 推送代码
git push heroku main

# 查看日志
heroku logs --tail
```

#### 4. 配置Webhook

```bash
# 获取应用URL
heroku info | grep Web URL

# 配置GitHub Webhook指向:
# https://your-app-name.herokuapp.com/webhook
```

### Render部署

#### 1. 创建账户

访问 https://render.com 并创建账户。

#### 2. 创建Web服务

1. 点击 "New +" → "Web Service"
2. 连接GitHub仓库
3. 配置构建命令:
   ```
   pip install -r requirements.txt
   ```
4. 配置启动命令:
   ```
   gunicorn -b 0.0.0.0:$PORT src.main:app
   ```
5. 添加环境变量:
   - `OPENAI_API_KEY`
   - `GITHUB_TOKEN`
   - `GITHUB_WEBHOOK_SECRET`

#### 3. 部署

点击 "Create Web Service"，Render会自动构建和部署。

### Railway部署

#### 1. 创建账户

访问 https://railway.app 并创建账户。

#### 2. 部署项目

```bash
# 安装Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 初始化项目
railway init

# 添加环境变量
railway variables set OPENAI_API_KEY=sk-your-key
railway variables set GITHUB_TOKEN=ghp-your-token

# 部署
railway up
```

### AWS部署

#### 使用Elastic Beanstalk

```bash
# 安装EB CLI
pip install awsebcli

# 初始化项目
eb init -p python-3.11 pr-codex-reviewer

# 创建环境
eb create pr-codex-reviewer-env

# 设置环境变量
eb setenv OPENAI_API_KEY=sk-your-key GITHUB_TOKEN=ghp-your-token

# 部署
eb deploy
```

#### 使用ECS (Docker)

```bash
# 创建ECS集群
aws ecs create-cluster --cluster-name pr-codex-reviewer

# 创建任务定义
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 创建服务
aws ecs create-service \
  --cluster pr-codex-reviewer \
  --service-name pr-codex-reviewer \
  --task-definition pr-codex-reviewer:1 \
  --desired-count 1
```

### 阿里云部署

#### 使用ECS

```bash
# 创建ECS实例（选择Ubuntu 22.04）
# 配置安全组，开放8000端口

# SSH连接到服务器
ssh root@your-server-ip

# 安装Docker
curl -fsSL https://get.docker.com | sh

# 克隆项目
git clone https://github.com/changsheng0804-blip/pr-codex-reviewer.git
cd pr-codex-reviewer

# 使用Docker Compose部署
docker-compose up -d
```

---

## GitHub Webhook配置

### 1. 获取Webhook URL

根据你的部署方式，Webhook URL可能是:

- 本地测试: `https://abc123.ngrok.io/webhook`
- Heroku: `https://your-app.herokuapp.com/webhook`
- Render: `https://your-app.onrender.com/webhook`
- 自定义域名: `https://your-domain.com/webhook`

### 2. 配置Webhook

1. 进入GitHub仓库设置
   ```
   https://github.com/owner/repo/settings/hooks
   ```

2. 点击 "Add webhook"

3. 填写配置:
   - **Payload URL**: 你的Webhook URL
   - **Content type**: `application/json`
   - **Secret**: （可选）你的Webhook密钥
   - **SSL verification**: Enable SSL verification

4. 选择事件:
   - ☑️ Pull requests
   - ☐ Pushes (不需要)
   - ☐ Everything (不推荐)

5. 点击 "Add webhook"

### 3. 验证Webhook

1. 创建测试PR
2. 查看Webhook投递记录:
   ```
   https://github.com/owner/repo/settings/hooks
   ```
3. 点击Webhook → Recent Deliveries
4. 查看响应状态码（应该返回200）

### 4. 使用ngrok本地测试

```bash
# 安装ngrok
# https://ngrok.com/download

# 启动ngrok（映射本地8000端口）
ngrok http 8000

# 获取公网URL（如 https://abc123.ngrok.io）
# 配置GitHub Webhook指向 https://abc123.ngrok.io/webhook
```

---

## 监控和日志

### 日志配置

**Python日志**:
```python
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'logs/app.log',
            maxBytes=10485760,  # 10MB
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

**Docker日志**:
```bash
# 查看实时日志
docker logs -f pr-codex-reviewer

# 查看最近100行
docker logs --tail 100 pr-codex-reviewer

# 查看特定时间段的日志
docker logs --since 2024-01-01T00:00:00 pr-codex-reviewer
```

### 健康检查

**添加健康检查端点**:
```python
@app.route("/health")
def health_check():
    """详细健康检查"""
    checks = {
        "server": "ok",
        "github_api": check_github_api(),
        "openai_api": check_openai_api(),
    }
    
    status = "healthy" if all(c == "ok" for c in checks.values()) else "degraded"
    
    return jsonify({
        "status": status,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    })
```

### 监控指标

**使用Prometheus**:
```python
from prometheus_client import Counter, Histogram, generate_latest

# 定义指标
review_counter = Counter('pr_reviews_total', 'Total PR reviews')
review_duration = Histogram('pr_review_duration_seconds', 'PR review duration')
error_counter = Counter('errors_total', 'Total errors', ['type'])

@app.route("/metrics")
def metrics():
    return generate_latest()
```

### 告警配置

**使用UptimeRobot**（免费）:
1. 注册 https://uptimerobot.com
2. 添加监控:
   - URL: `https://your-domain.com/`
   - 监控间隔: 5分钟
3. 配置告警:
   - Email通知
   - Webhook通知（如钉钉、企业微信）

---

## 故障排除

### 常见问题

#### 1. 服务无法启动

**症状**: 运行 `python -m src.main` 后报错

**排查**:
```bash
# 检查Python版本
python --version  # 需要3.11+

# 检查依赖
pip list | grep -E "flask|requests|openai"

# 检查环境变量
echo $OPENAI_API_KEY
echo $GITHUB_TOKEN

# 检查端口占用
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

**解决**:
```bash
# 安装缺失的依赖
pip install -r requirements.txt

# 设置环境变量
export OPENAI_API_KEY=sk-your-key
export GITHUB_TOKEN=ghp-your-token

# 更换端口
PORT=8080 python -m src.main
```

#### 2. GitHub API返回401

**症状**: 日志显示 "Bad credentials"

**原因**: GitHub Token无效或过期

**解决**:
1. 检查Token是否过期
2. 重新生成Token: https://github.com/settings/tokens
3. 确保Token有 `repo` 权限
4. 更新环境变量

#### 3. OpenAI API返回429

**症状**: 日志显示 "Rate limit exceeded"

**原因**: 超出API速率限制

**解决**:
```python
# 添加重试逻辑
import time
from functools import wraps

def retry_with_backoff(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "rate limit" in str(e).lower():
                        wait = 2 ** i
                        print(f"Rate limited, waiting {wait}s...")
                        time.sleep(wait)
                    else:
                        raise
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

#### 4. Webhook不触发

**症状**: 提交PR后没有收到审查评论

**排查**:
```bash
# 检查Webhook配置
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/repo/hooks

# 检查Webhook投递记录
# GitHub仓库设置 → Webhooks → Recent Deliveries

# 检查服务器日志
docker logs pr-codex-reviewer
```

**解决**:
1. 确认Webhook URL正确
2. 确认选择了 "Pull requests" 事件
3. 确认服务器可访问
4. 检查防火墙设置

#### 5. 内存不足

**症状**: 服务崩溃，日志显示 "MemoryError"

**原因**: 分析大文件时内存不足

**解决**:
```python
# 在config.py中减小限制
MAX_FILE_SIZE = 50000  # 50KB
MAX_FILES_PER_REVIEW = 5

# 使用Docker限制内存
docker run -m 512m pr-codex-reviewer
```

### 调试模式

**启用详细日志**:
```bash
# 设置调试模式
export DEBUG=true
export LOG_LEVEL=DEBUG

# 运行服务
python -m src.main
```

### 获取帮助

**查看日志**:
```bash
# 实时日志
docker logs -f pr-codex-reviewer

# 保存日志到文件
docker logs pr-codex-reviewer > logs.txt 2>&1
```

**测试API**:
```bash
# 测试健康检查
curl -v http://localhost:8000/

# 测试手动审查
curl -X POST http://localhost:8000/review/owner/repo/123

# 测试Webhook（使用示例数据）
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d @test-webhook.json
```

---

## 安全建议

### 1. 使用HTTPS

**使用Let's Encrypt**:
```bash
# 安装certbot
sudo apt install certbot

# 获取证书
sudo certbot certonly --standalone -d your-domain.com

# 配置Nginx使用证书
```

### 2. 保护API密钥

**使用密钥管理服务**:
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault

### 3. 限制访问

**IP白名单**:
```nginx
# nginx.conf
location /webhook {
    allow 192.30.252.0/22;  # GitHub IP范围
    deny all;
    proxy_pass http://localhost:8000;
}
```

### 4. 定期更新

```bash
# 更新依赖
pip install --upgrade -r requirements.txt

# 更新系统包
sudo apt update && sudo apt upgrade

# 重启服务
docker-compose restart
```

---

*文档版本: 1.0*  
*最后更新: 2026-05-31*
