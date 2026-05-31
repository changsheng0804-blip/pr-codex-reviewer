# 📚 PR Codex Reviewer - API文档

## 📋 目录

1. [概述](#概述)
2. [Webhook API](#webhook-api)
3. [手动审查API](#手动审查api)
4. [健康检查API](#健康检查api)
5. [错误处理](#错误处理)
6. [Webhook事件格式](#webhook事件格式)

---

## 概述

### 基础URL

```
开发环境: http://localhost:8000
生产环境: https://your-domain.com
```

### 认证

目前API不需要额外认证，但建议：
- 使用HTTPS
- 配置防火墙规则
- 使用Webhook密钥验证

### 内容类型

所有请求和响应使用 `application/json`。

---

## Webhook API

### 接收GitHub Webhook

接收并处理GitHub的Pull Request事件。

**Endpoint**: `POST /webhook`

**Headers**:
```
Content-Type: application/json
X-GitHub-Event: pull_request
X-GitHub-Delivery: uuid
```

**请求体**:
```json
{
  "action": "opened",
  "number": 123,
  "pull_request": {
    "id": 1,
    "number": 123,
    "title": "Add new feature",
    "body": "PR描述",
    "user": {
      "login": "username"
    },
    "head": {
      "sha": "abc123"
    }
  },
  "repository": {
    "id": 1,
    "name": "repo-name",
    "full_name": "owner/repo-name",
    "owner": {
      "login": "owner"
    }
  }
}
```

**响应**:

成功:
```json
{
  "status": "success",
  "files_reviewed": 3,
  "total_issues": 5
}
```

跳过:
```json
{
  "status": "skipped",
  "reason": "没有需要审查的文件"
}
```

错误:
```json
{
  "status": "error",
  "error": "错误信息"
}
```

**状态码**:
- `200`: 成功处理
- `400`: 请求格式错误
- `500`: 服务器内部错误

**示例**:

```bash
# 使用curl测试
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -d '{
    "action": "opened",
    "number": 1,
    "pull_request": {
      "number": 1,
      "title": "Test PR"
    },
    "repository": {
      "name": "test-repo",
      "owner": {
        "login": "test-user"
      }
    }
  }'
```

```python
# 使用Python requests
import requests

payload = {
    "action": "opened",
    "number": 1,
    "pull_request": {
        "number": 1,
        "title": "Test PR"
    },
    "repository": {
        "name": "test-repo",
        "owner": {
            "login": "test-user"
        }
    }
}

response = requests.post(
    "http://localhost:8000/webhook",
    json=payload,
    headers={"X-GitHub-Event": "pull_request"}
)

print(response.json())
```

---

## 手动审查API

### 触发PR审查

手动触发对特定PR的审查。

**Endpoint**: `POST /review/<owner>/<repo>/<pr_number>`

**URL参数**:
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| owner | string | 是 | 仓库所有者用户名 |
| repo | string | 是 | 仓库名称 |
| pr_number | integer | 是 | PR编号 |

**响应**:

成功:
```json
{
  "status": "success",
  "files_reviewed": 3,
  "total_issues": 5
}
```

**状态码**:
- `200`: 审查完成
- `400`: 参数错误
- `404`: PR不存在
- `500`: 服务器错误

**示例**:

```bash
# 审查特定PR
curl -X POST http://localhost:8000/review/facebook/react/12345
```

```python
# 使用Python
import requests

owner = "facebook"
repo = "react"
pr_number = 12345

response = requests.post(
    f"http://localhost:8000/review/{owner}/{repo}/{pr_number}"
)

result = response.json()
print(f"审查了 {result['files_reviewed']} 个文件")
print(f"发现了 {result['total_issues']} 个问题")
```

---

## 健康检查API

### 检查服务状态

用于监控和负载均衡的健康检查端点。

**Endpoint**: `GET /`

**响应**:
```json
{
  "status": "healthy",
  "service": "pr-codex-reviewer",
  "version": "1.0.0"
}
```

**状态码**:
- `200`: 服务正常

**示例**:

```bash
curl http://localhost:8000/
```

```python
import requests

response = requests.get("http://localhost:8000/")
if response.json()["status"] == "healthy":
    print("服务运行正常")
```

---

## 错误处理

### 错误响应格式

所有错误响应都遵循以下格式：

```json
{
  "status": "error",
  "error": "人类可读的错误描述",
  "code": "ERROR_CODE",
  "details": {
    "field": "额外信息"
  }
}
```

### 错误代码

| 代码 | 描述 | HTTP状态码 |
|------|------|-----------|
| `MISSING_CONFIG` | 缺少配置 | 500 |
| `GITHUB_API_ERROR` | GitHub API调用失败 | 502 |
| `OPENAI_API_ERROR` | OpenAI API调用失败 | 502 |
| `INVALID_PAYLOAD` | Webhook数据无效 | 400 |
| `RATE_LIMITED` | 超出速率限制 | 429 |

### 常见错误

**配置错误**:
```json
{
  "status": "error",
  "error": "缺少必需的环境变量: OPENAI_API_KEY",
  "code": "MISSING_CONFIG"
}
```

**GitHub API错误**:
```json
{
  "status": "error",
  "error": "GitHub API返回401: Bad credentials",
  "code": "GITHUB_API_ERROR",
  "details": {
    "status_code": 401
  }
}
```

**OpenAI API错误**:
```json
{
  "status": "error",
  "error": "Rate limit exceeded",
  "code": "OPENAI_API_ERROR",
  "details": {
    "retry_after": 20
  }
}
```

---

## Webhook事件格式

### Pull Request事件

GitHub发送的Pull Request Webhook事件格式：

#### 创建PR (opened)

```json
{
  "action": "opened",
  "number": 123,
  "pull_request": {
    "id": 1,
    "node_id": "MDExOlB1bGxSZXF1ZXN0MQ==",
    "number": 123,
    "state": "open",
    "locked": false,
    "title": "Add new feature",
    "user": {
      "login": "username",
      "id": 1,
      "avatar_url": "https://github.com/images/error/username_happy.gif"
    },
    "body": "PR描述内容",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "closed_at": null,
    "merged_at": null,
    "merge_commit_sha": "abc123",
    "assignee": null,
    "assignees": [],
    "requested_reviewers": [],
    "labels": [],
    "head": {
      "label": "username:branch-name",
      "ref": "branch-name",
      "sha": "abc123",
      "user": {
        "login": "username"
      },
      "repo": {
        "id": 1,
        "name": "repo-name",
        "full_name": "username/repo-name"
      }
    },
    "base": {
      "label": "username:main",
      "ref": "main",
      "sha": "def456",
      "user": {
        "login": "username"
      },
      "repo": {
        "id": 1,
        "name": "repo-name",
        "full_name": "username/repo-name"
      }
    }
  },
  "repository": {
    "id": 1,
    "node_id": "MDEwOlJlcG9zaXRvcnkx",
    "name": "repo-name",
    "full_name": "owner/repo-name",
    "private": false,
    "owner": {
      "login": "owner",
      "id": 1
    },
    "html_url": "https://github.com/owner/repo-name",
    "description": "Repository description",
    "fork": false,
    "url": "https://api.github.com/repos/owner/repo-name"
  },
  "sender": {
    "login": "username",
    "id": 1
  }
}
```

#### 更新PR (synchronize)

当PR有新的提交推送时：

```json
{
  "action": "synchronize",
  "number": 123,
  "pull_request": {
    "number": 123,
    "head": {
      "sha": "new-sha-123"
    }
  },
  "repository": {
    "name": "repo-name",
    "owner": {
      "login": "owner"
    }
  }
}
```

### 验证Webhook签名

为了安全，应该验证Webhook请求确实来自GitHub：

```python
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    验证GitHub Webhook签名
    
    参数:
        payload: 请求体原始字节
        signature: X-Hub-Signature-256头值
        secret: Webhook密钥
        
    返回:
        bool: 签名是否有效
    """
    # 计算期望的签名
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # 比较签名（使用constant_time_compare防止时序攻击）
    return hmac.compare_digest(
        f"sha256={expected}",
        signature
    )
```

使用示例：

```python
from flask import request

@app.route('/webhook', methods=['POST'])
def webhook():
    # 获取签名
    signature = request.headers.get('X-Hub-Signature-256')
    
    # 验证签名（如果配置了密钥）
    if Config.GITHUB_WEBHOOK_SECRET:
        if not verify_webhook_signature(
            request.data,
            signature,
            Config.GITHUB_WEBHOOK_SECRET
        ):
            return jsonify({"status": "error", "reason": "Invalid signature"}), 401
    
    # 处理Webhook
    payload = request.get_json()
    result = engine.handle_webhook(payload)
    
    return jsonify(result)
```

---

## 速率限制

### GitHub API限制

| 类型 | 限制 | 说明 |
|------|------|------|
| 认证用户 | 5000/小时 | 使用Personal Access Token |
| 未认证 | 60/小时 | 不推荐 |

**响应头**:
```
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4999
X-RateLimit-Reset: 1640995200
```

### OpenAI API限制

| 模型 | RPM | TPM |
|------|-----|-----|
| gpt-4 | 200 | 40,000 |
| gpt-3.5-turbo | 3,500 | 90,000 |

*RPM: Requests Per Minute*  
*TPM: Tokens Per Minute*

### 处理速率限制

```python
import time
from functools import wraps

def rate_limit_handler(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    if i == max_retries - 1:
                        raise
                    
                    # 等待重试
                    wait_time = e.retry_after or (2 ** i)
                    time.sleep(wait_time)
            
        return wrapper
    return decorator
```

---

## SDK示例

### Python SDK

```python
import requests

class PRCodexReviewer:
    """PR Codex Reviewer 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def health_check(self) -> dict:
        """检查服务状态"""
        response = requests.get(f"{self.base_url}/")
        response.raise_for_status()
        return response.json()
    
    def review_pr(self, owner: str, repo: str, pr_number: int) -> dict:
        """审查PR"""
        url = f"{self.base_url}/review/{owner}/{repo}/{pr_number}"
        response = requests.post(url)
        response.raise_for_status()
        return response.json()
    
    def send_webhook(self, payload: dict) -> dict:
        """发送Webhook事件"""
        response = requests.post(
            f"{self.base_url}/webhook",
            json=payload,
            headers={"X-GitHub-Event": "pull_request"}
        )
        response.raise_for_status()
        return response.json()

# 使用示例
client = PRCodexReviewer("https://api.example.com")

# 检查服务状态
health = client.health_check()
print(f"服务状态: {health['status']}")

# 审查PR
result = client.review_pr("facebook", "react", 12345)
print(f"发现问题: {result['total_issues']} 个")
```

### JavaScript/TypeScript SDK

```typescript
class PRCodexReviewer {
    private baseUrl: string;
    
    constructor(baseUrl: string = "http://localhost:8000") {
        this.baseUrl = baseUrl.replace(/\/$/, '');
    }
    
    async healthCheck(): Promise<{status: string}> {
        const response = await fetch(`${this.baseUrl}/`);
        return response.json();
    }
    
    async reviewPR(owner: string, repo: string, prNumber: number): Promise<{
        status: string;
        files_reviewed: number;
        total_issues: number;
    }> {
        const response = await fetch(
            `${this.baseUrl}/review/${owner}/${repo}/${prNumber}`,
            { method: 'POST' }
        );
        return response.json();
    }
}

// 使用示例
const client = new PRCodexReviewer("https://api.example.com");

// 检查服务状态
const health = await client.healthCheck();
console.log(`服务状态: ${health.status}`);

// 审查PR
const result = await client.reviewPR("facebook", "react", 12345);
console.log(`发现问题: ${result.total_issues} 个`);
```

---

*文档版本: 1.0*  
*最后更新: 2026-05-31*
