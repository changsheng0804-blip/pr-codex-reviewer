# 🛠️ PR Codex Reviewer - 开发指南

## 📋 目录

1. [环境搭建](#环境搭建)
2. [项目结构](#项目结构)
3. [开发流程](#开发流程)
4. [测试指南](#测试指南)
5. [调试技巧](#调试技巧)
6. [常见问题](#常见问题)

---

## 环境搭建

### 前置要求

- Python 3.11+
- Git
- GitHub账号
- OpenAI账号（可选，用于测试）

### 1. 克隆仓库

```bash
# 克隆项目
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

# 安装开发依赖（如果需要）
pip install -e ".[dev]"
```

### 4. 配置环境变量

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的API密钥
# Windows:
notepad .env
# macOS/Linux:
nano .env
```

**.env 文件示例**:
```env
# OpenAI 配置（必需）
OPENAI_API_KEY=sk-your-key-here

# GitHub 配置（必需）
GITHUB_TOKEN=ghp_your-token-here

# 可选配置
DEBUG=true
```

### 5. 验证安装

```bash
# 运行测试
pytest tests/ -v

# 启动开发服务器
python -m src.main
```

访问 http://localhost:8000/ 应该看到健康检查响应。

---

## 项目结构

```
pr-codex-reviewer/
│
├── src/                          # 源代码目录
│   ├── __init__.py              # 包初始化
│   ├── main.py                  # Flask应用入口
│   ├── config.py                # 配置管理
│   ├── github_client.py         # GitHub API客户端
│   ├── codex_analyzer.py        # AI代码分析器
│   ├── review_engine.py         # 审查引擎（核心协调器）
│   └── comment_generator.py     # 评论生成器（预留）
│
├── tests/                        # 测试目录
│   ├── __init__.py
│   ├── test_github_client.py    # GitHub客户端测试
│   ├── test_codex_analyzer.py   # AI分析器测试
│   └── test_review_engine.py    # 审查引擎测试
│
├── docs/                         # 文档目录
│   ├── ARCHITECTURE.md          # 架构文档
│   └── DEVELOPMENT.md           # 开发指南（本文件）
│
├── .github/                      # GitHub配置
│   └── workflows/
│       └── ci.yml               # CI/CD工作流
│
├── .env.example                  # 环境变量示例
├── .gitignore                    # Git忽略文件
├── Dockerfile                    # Docker构建文件
├── requirements.txt              # Python依赖
├── setup.py                      # 包安装配置
└── README.md                     # 项目说明
```

### 文件说明

| 文件 | 职责 | 修改频率 |
|------|------|---------|
| `main.py` | Web服务器，接收请求 | 低 |
| `config.py` | 配置管理 | 低 |
| `github_client.py` | GitHub API交互 | 中 |
| `codex_analyzer.py` | AI分析逻辑 | 高 |
| `review_engine.py` | 业务流程协调 | 中 |

---

## 开发流程

### 1. 创建功能分支

```bash
# 确保在主分支
git checkout main
git pull origin main

# 创建功能分支
git checkout -b feature/your-feature-name

# 示例：
git checkout -b feature/add-ruby-support
```

### 2. 开发代码

**编码规范**:
- 遵循 PEP 8 风格指南
- 使用类型提示
- 编写文档字符串
- 添加注释解释复杂逻辑

**示例**:
```python
def analyze_code(self, code: str, language: str) -> Dict:
    """
    分析代码并返回结构化结果
    
    参数:
        code: 要分析的代码文本
        language: 编程语言
        
    返回:
        Dict: 包含issues, suggestions, security, performance的字典
    """
    # 构建分析Prompt
    prompt = self._build_analysis_prompt(code, language)
    
    # 调用AI API
    response = self._call_api(prompt)
    
    # 解析结果
    return self._parse_response(response)
```

### 3. 编写测试

**测试要求**:
- 新功能必须有测试
- 测试覆盖率不低于80%
- 使用pytest框架

**示例**:
```python
def test_analyze_code_with_bug():
    """测试分析包含Bug的代码"""
    analyzer = CodexAnalyzer()
    
    code = """
    def divide(a, b):
        return a / b
    """
    
    result = analyzer.analyze_code(code, "python")
    
    # 验证发现了问题
    assert len(result["issues"]) > 0
    # 验证发现了安全问题
    assert len(result["security"]) > 0
```

### 4. 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_codex_analyzer.py -v

# 运行特定测试
pytest tests/test_codex_analyzer.py::test_analyze_code_with_bug -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

### 5. 代码检查

```bash
# 代码格式化
black src/ tests/

# 代码风格检查
ruff check src/ tests/

# 类型检查
mypy src/

# 运行所有检查（等同于CI）
black --check src/ tests/
ruff check src/ tests/
mypy src/
pytest tests/ -v
```

### 6. 提交代码

```bash
# 添加修改的文件
git add src/your_file.py tests/test_your_file.py

# 提交（使用清晰的提交信息）
git commit -m "Add Ruby language support

- Add Ruby to supported languages list
- Add .rb extension mapping
- Add tests for Ruby code analysis
- Update documentation"

# 推送到远程
git push origin feature/add-ruby-support
```

### 7. 创建Pull Request

1. 在GitHub上创建PR
2. 填写PR描述（参考模板）
3. 等待CI检查通过
4. 请求代码审查
5. 合并到main分支

---

## 测试指南

### 测试策略

```
┌─────────────────────────────────────┐
│           测试金字塔                 │
│                                      │
│         ┌─────────┐                 │
│         │  E2E    │  少量           │
│         │  Tests  │  关键流程       │
│        ┌┴─────────┴┐                │
│        │ Integration│  中等         │
│        │   Tests    │  API交互      │
│       ┌┴────────────┴┐               │
│       │   Unit Tests  │  大量        │
│       │              │  核心逻辑     │
│       └──────────────┘               │
└─────────────────────────────────────┘
```

### 单元测试

**测试文件命名**: `test_被测试模块名.py`

**测试类命名**: `Test被测试类名`

**测试方法命名**: `test_被测试方法名_场景`

**示例**:
```python
# test_codex_analyzer.py

class TestCodexAnalyzer:
    """测试CodexAnalyzer类"""
    
    def test_init_with_api_key(self):
        """测试使用API密钥初始化"""
        analyzer = CodexAnalyzer(api_key="test-key")
        assert analyzer.api_key == "test-key"
    
    def test_analyze_code_empty_code(self):
        """测试分析空代码"""
        analyzer = CodexAnalyzer()
        result = analyzer.analyze_code("", "python")
        
        assert "error" not in result
        assert result["issues"] == []
    
    def test_detect_language_python(self):
        """测试Python语言检测"""
        analyzer = CodexAnalyzer()
        lang = analyzer._detect_language("test.py")
        
        assert lang == "python"
```

### 集成测试

**测试GitHub API交互**:
```python
# 使用pytest-mock或unittest.mock
from unittest.mock import Mock, patch

def test_get_pr_files_success():
    """测试成功获取PR文件"""
    with patch("src.github_client.requests.get") as mock_get:
        # 设置模拟响应
        mock_response = Mock()
        mock_response.json.return_value = [
            {"filename": "test.py", "status": "modified"}
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # 执行测试
        client = GitHubClient(token="test-token")
        files = client.get_pr_files("owner", "repo", 1)
        
        # 验证结果
        assert len(files) == 1
        assert files[0]["filename"] == "test.py"
```

### 模拟外部API

**为什么需要模拟**:
- 避免消耗API额度
- 测试更快速
- 不依赖外部服务
- 可重复执行

**模拟OpenAI API**:
```python
@patch("openai.ChatCompletion.create")
def test_analyze_code_with_mock(mock_create):
    """使用模拟的OpenAI API测试"""
    # 设置模拟响应
    mock_create.return_value = {
        "choices": [{
            "message": {
                "content": "ISSUES:\n- Bug found\n\nSUGGESTIONS:\n- Fix it"
            }
        }]
    }
    
    # 执行测试
    analyzer = CodexAnalyzer()
    result = analyzer.analyze_code("code", "python")
    
    # 验证结果
    assert len(result["issues"]) == 1
    assert result["issues"][0] == "Bug found"
```

---

## 调试技巧

### 1. 本地调试Webhook

**使用ngrok暴露本地服务器**:
```bash
# 安装ngrok
# https://ngrok.com/download

# 启动ngrok
ngrok http 8000

# 获取公网URL（如 https://abc123.ngrok.io）
# 配置GitHub Webhook指向 https://abc123.ngrok.io/webhook
```

### 2. 查看日志

**启用调试日志**:
```python
# 在 .env 文件中设置
DEBUG=true

# 或者在代码中
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. 测试GitHub API

**使用GitHub CLI测试**:
```bash
# 获取PR文件
gh api repos/owner/repo/pulls/123/files

# 获取PR详情
gh api repos/owner/repo/pulls/123

# 发布评论
gh api repos/owner/repo/issues/123/comments \
  -f body="测试评论"
```

### 4. 测试OpenAI API

**使用curl测试**:
```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

### 5. 使用断点调试

**在代码中设置断点**:
```python
def review_pr(self, owner, repo, pr_number):
    import pdb; pdb.set_trace()  # 设置断点
    
    files = self.github.get_pr_files(owner, repo, pr_number)
    # ...
```

**使用VS Code调试**:
1. 安装Python扩展
2. 创建 `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "module": "src.main",
            "env": {
                "FLASK_APP": "src/main.py",
                "FLASK_DEBUG": "1"
            },
            "args": [
                "run",
                "--no-debugger",
                "--no-reload"
            ],
            "jinja": true
        }
    ]
}
```

---

## 常见问题

### Q1: 如何获取GitHub Token？

**步骤**:
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限:
   - `repo`: 访问仓库
   - `pull_requests`: 管理PR
   - `issues`: 管理Issues（用于评论）
4. 生成并复制Token

### Q2: 如何获取OpenAI API Key？

**步骤**:
1. 访问 https://platform.openai.com/api-keys
2. 点击 "Create new secret key"
3. 复制生成的Key

**注意**: 新注册的OpenAI账号可能需要绑定支付方式才能使用API。

### Q3: Webhook不触发怎么办？

**排查步骤**:
1. 检查Webhook URL是否正确
2. 检查是否选择了 "Pull requests" 事件
3. 检查服务器是否可访问（使用ngrok测试）
4. 查看GitHub Webhook投递记录（仓库设置 → Webhooks → Recent Deliveries）
5. 检查服务器日志

### Q4: OpenAI API调用失败？

**常见原因**:
- API Key无效或过期
- 超出速率限制
- 账户余额不足
- 网络问题

**解决方案**:
```python
# 添加重试逻辑
import time
from functools import wraps

def retry_on_error(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == max_retries - 1:
                        raise
                    time.sleep(delay * (i + 1))
        return wrapper
    return decorator

@retry_on_error(max_retries=3)
def analyze_code(self, code, language):
    # ...
```

### Q5: 如何降低API成本？

**策略**:
1. 使用更小的模型（gpt-3.5-turbo）
2. 减少max_tokens
3. 缓存分析结果
4. 只分析修改的部分（patch）
5. 限制文件大小和数量

### Q6: 如何添加新语言支持？

**步骤**:
1. 在 `config.py` 的 `SUPPORTED_LANGUAGES` 中添加语言名称
2. 在 `review_engine.py` 的 `extension_map` 中添加扩展名映射
3. 编写测试验证
4. 更新文档

---

## 贡献指南

### 提交Issue

**Bug报告模板**:
```markdown
**描述**
简要描述Bug

**复现步骤**
1. 步骤1
2. 步骤2
3. 步骤3

**期望行为**
描述应该发生什么

**实际行为**
描述实际发生了什么

**环境**
- Python版本:
- 操作系统:
- 项目版本:

**日志**
如果有错误日志，请粘贴
```

**功能请求模板**:
```markdown
**描述**
简要描述功能需求

**使用场景**
描述这个功能在什么场景下使用

**期望行为**
描述期望的功能行为

**替代方案**
是否有其他替代方案
```

### 提交PR

**PR检查清单**:
- [ ] 代码遵循项目风格
- [ ] 添加了测试
- [ ] 测试通过
- [ ] 更新了文档
- [ ] 添加了CHANGELOG

**PR描述模板**:
```markdown
## 描述
简要描述这个PR做了什么

## 变更类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 性能优化

## 测试
描述如何测试这些变更

## 截图
如果有UI变更，添加截图
```

---

*文档版本: 1.0*  
*最后更新: 2026-05-31*
