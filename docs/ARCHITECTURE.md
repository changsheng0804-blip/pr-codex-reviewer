# 🏗️ PR Codex Reviewer - 架构文档

## 📋 目录

1. [系统概述](#系统概述)
2. [核心组件](#核心组件)
3. [数据流](#数据流)
4. [设计决策](#设计决策)
5. [扩展指南](#扩展指南)

---

## 系统概述

PR Codex Reviewer 是一个基于AI的代码审查工具，自动分析GitHub Pull Request中的代码变更，提供质量评估和改进建议。

### 主要特性

- 🤖 **AI驱动**: 使用OpenAI GPT-4进行代码分析
- 🔗 **GitHub集成**: 通过Webhook自动触发审查
- 🌐 **多语言支持**: Python, JavaScript, TypeScript, Java, Go, Rust, C/C++
- 📝 **结构化报告**: 生成Markdown格式的审查报告
- 🐳 **易于部署**: 支持Docker和云原生部署

---

## 核心组件

### 1. Web服务器 (Flask)

```
┌─────────────────────────────────────┐
│           Flask Server               │
│                                      │
│  ┌─────────┐    ┌───────────────┐   │
│  │  Health │    │   Webhook     │   │
│  │  Check  │    │   Handler     │   │
│  │   GET / │    │   POST /webhook│  │
│  └─────────┘    └───────────────┘   │
│                                      │
│  ┌─────────────────────────────┐    │
│  │     Manual Review API       │    │
│  │  POST /review/:owner/:repo/:pr │ │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

**职责**:
- 接收GitHub Webhook请求
- 提供健康检查端点
- 支持手动触发审查

**代码位置**: `src/main.py`

---

### 2. 审查引擎 (ReviewEngine)

```
┌─────────────────────────────────────┐
│         Review Engine                │
│                                      │
│  ┌──────────────┐  ┌─────────────┐ │
│  │   GitHub     │  │    AI       │ │
│  │   Client     │  │  Analyzer   │ │
│  └──────────────┘  └─────────────┘ │
│         │                │          │
│         └────────────────┘          │
│                  │                  │
│         ┌──────────────┐           │
│         │  Review Flow │           │
│         │  Controller  │           │
│         └──────────────┘           │
└─────────────────────────────────────┘
```

**职责**:
- 协调审查流程
- 过滤和分发文件
- 生成最终报告

**代码位置**: `src/review_engine.py`

---

### 3. GitHub客户端 (GitHubClient)

```
┌─────────────────────────────────────┐
│        GitHub Client                 │
│                                      │
│  ┌─────────┐ ┌─────────┐ ┌────────┐│
│  │ Get PR  │ │ Get     │ │ Post   ││
│  │ Files   │ │ File    │ │ Comment││
│  │         │ │ Content │ │        ││
│  └─────────┘ └─────────┘ └────────┘│
│  ┌─────────┐ ┌─────────────────┐   │
│  │ Submit  │ │ Post Review     │   │
│  │ Review  │ │ Comment         │   │
│  └─────────┘ └─────────────────┘   │
└─────────────────────────────────────┘
```

**职责**:
- 与GitHub API通信
- 获取PR信息
- 发布审查结果

**代码位置**: `src/github_client.py`

---

### 4. AI分析器 (CodexAnalyzer)

```
┌─────────────────────────────────────┐
│        Codex Analyzer                │
│                                      │
│  ┌──────────────┐  ┌─────────────┐ │
│  │   Prompt     │  │   OpenAI    │ │
│  │   Builder    │  │    API      │ │
│  └──────────────┘  └─────────────┘ │
│         │                │          │
│         └────────────────┘          │
│                  │                  │
│         ┌──────────────┐           │
│         │   Result     │           │
│         │   Parser     │           │
│         └──────────────┘           │
└─────────────────────────────────────┘
```

**职责**:
- 构建分析Prompt
- 调用OpenAI API
- 解析分析结果

**代码位置**: `src/codex_analyzer.py`

---

## 数据流

### 完整审查流程

```
GitHub Webhook
      │
      ▼
┌─────────────┐
│ Flask Server │
│  /webhook   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Review    │
│   Engine    │
└──────┬──────┘
       │
       ├──► GitHub API ──► PR Files
       │                      │
       │                      ▼
       │               Filter & Select
       │                      │
       │                      ▼
       │               For Each File:
       │                      │
       ├──► AI Analyzer ──► Code Analysis
       │                      │
       │                      ▼
       │               Parse Results
       │                      │
       │                      ▼
       │               Generate Summary
       │                      │
       ▼                      │
┌─────────────┐              │
│   GitHub    │◄─────────────┘
│   API       │
│ Post Review │
└─────────────┘
```

### 详细步骤

1. **触发**: GitHub发送Webhook（PR创建或更新）
2. **接收**: Flask服务器接收并解析Webhook
3. **提取**: ReviewEngine提取PR信息（仓库、PR编号）
4. **获取**: GitHubClient获取PR修改的文件列表
5. **过滤**: ReviewEngine过滤支持的文件（语言、大小）
6. **分析**: CodexAnalyzer分析每个文件的代码
7. **汇总**: ReviewEngine汇总所有分析结果
8. **发布**: GitHubClient发布审查报告到PR

---

## 设计决策

### 1. 为什么选择Flask？

**原因**:
- 轻量级，易于部署
- 社区成熟，文档丰富
- 适合Webhook这种简单场景

**替代方案**:
- FastAPI: 更好的类型支持和性能
- Django: 过于重量级

### 2. 为什么使用类属性存储配置？

**原因**:
- 简单，无需实例化
- 全局可访问
- 适合配置这种全局状态

**替代方案**:
- Pydantic Settings: 更强大的验证
- 单例模式: 更灵活

### 3. 为什么使用OpenAI ChatCompletion？

**原因**:
- 对指令遵循更好
- 支持系统提示词
- 输出更结构化

**替代方案**:
- Completion API: 较旧，效果较差
- 其他模型: Claude, Gemini等

### 4. 为什么使用Markdown格式报告？

**原因**:
- GitHub原生支持
- 格式丰富，易于阅读
- 无需额外渲染

---

## 扩展指南

### 添加新的编程语言支持

1. **更新配置** (`src/config.py`):
```python
SUPPORTED_LANGUAGES: list = [
    # ... 现有语言
    "ruby",  # 添加新语言
]
```

2. **更新语言检测** (`src/review_engine.py`):
```python
extension_map = {
    # ... 现有映射
    ".rb": "ruby",  # 添加扩展名映射
}
```

3. **测试**: 提交一个该语言的PR测试

### 添加新的审查规则

1. **修改Prompt** (`src/codex_analyzer.py`):
```python
content = (
    "你是一位资深的代码审查专家。请分析提供的代码，"
    "重点关注以下方面:\n"
    "1. 潜在的Bug和逻辑错误\n"
    "2. 安全漏洞\n"
    "3. 代码风格和最佳实践\n"
    "4. 性能优化机会\n"
    "5. 可维护性问题\n"
    "6. 【新增】可访问性（Accessibility）\n"  # 添加新规则
    "请提供具体、可操作的改进建议。"
)
```

2. **更新解析器**:
```python
result = {
    # ... 现有字段
    "accessibility": [],  # 添加新字段
}
```

3. **更新报告生成**:
```python
if analysis.get("accessibility"):
    summary += "**♿ 可访问性:**\n"
    for item in analysis["accessibility"]:
        summary += f"- {item}\n"
```

### 集成其他AI模型

1. **创建新的分析器类**:
```python
class ClaudeAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def analyze_code(self, code: str, language: str) -> Dict:
        # 调用Claude API
        pass
```

2. **修改ReviewEngine**:
```python
class ReviewEngine:
    def __init__(self, analyzer_type: str = "openai"):
        if analyzer_type == "openai":
            self.analyzer = CodexAnalyzer()
        elif analyzer_type == "claude":
            self.analyzer = ClaudeAnalyzer()
```

---

## 部署架构

### 单机部署

```
┌─────────────────────────────────────┐
│              Server                  │
│                                      │
│  ┌─────────┐      ┌─────────────┐  │
│  │  Nginx  │─────►│    Flask    │  │
│  │ (Proxy) │      │   (App)     │  │
│  └─────────┘      └──────┬──────┘  │
│                          │          │
│                   ┌──────┴──────┐   │
│                   │   SQLite    │   │
│                   │   (Cache)   │   │
│                   └─────────────┘   │
└─────────────────────────────────────┘
```

### Docker部署

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    volumes:
      - ./logs:/app/logs
```

### 云原生部署

```
┌─────────────────────────────────────┐
│           Kubernetes                 │
│                                      │
│  ┌─────────┐      ┌─────────────┐  │
│  │ Ingress │─────►│   Service   │  │
│  │         │      │             │  │
│  └─────────┘      └──────┬──────┘  │
│                          │          │
│                   ┌──────┴──────┐   │
│                   │   Pod       │   │
│                   │ ┌─────────┐ │   │
│                   │ │  Flask  │ │   │
│                   │ └─────────┘ │   │
│                   └─────────────┘   │
└─────────────────────────────────────┘
```

---

## 性能考虑

### 瓶颈分析

| 组件 | 潜在瓶颈 | 优化方案 |
|------|---------|---------|
| OpenAI API | 调用延迟（1-5秒） | 异步处理，超时设置 |
| GitHub API | 速率限制 | 缓存，批量请求 |
| 大文件 | Token超出限制 | 文件大小限制，分块处理 |
| 并发 | 多PR同时触发 | 队列处理，限流 |

### 优化建议

1. **异步处理**: 使用Celery或RQ处理审查任务
2. **缓存**: 缓存GitHub API响应
3. **限流**: 限制并发审查数量
4. **监控**: 添加性能指标收集

---

## 安全考虑

### 威胁模型

| 威胁 | 风险 | 缓解措施 |
|------|------|---------|
| API密钥泄露 | 高 | 环境变量，密钥管理服务 |
| Webhook伪造 | 中 | 签名验证，IP白名单 |
| 代码注入 | 中 | 输入验证，沙箱执行 |
| 数据泄露 | 低 | 最小权限，日志脱敏 |

### 安全最佳实践

1. **API密钥**: 使用环境变量，定期轮换
2. **Webhook**: 验证签名，使用HTTPS
3. **代码**: 不执行用户代码，仅静态分析
4. **日志**: 脱敏敏感信息

---

*文档版本: 1.0*  
*最后更新: 2026-05-31*
