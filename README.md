# 🤖 PR Codex Reviewer

AI-powered PR review bot that automatically reviews GitHub pull requests for code quality, bugs, and security issues using OpenAI Codex.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ✨ Features

- 🔍 **Automatic Code Analysis** - Reviews PRs automatically when opened or updated
- 🐛 **Bug Detection** - Identifies potential bugs and logical errors
- 🔒 **Security Scanning** - Detects common security vulnerabilities
- 📊 **Code Quality** - Checks code style and best practices
- 🚀 **Multi-Language Support** - Python, JavaScript, TypeScript, Java, Go, and more
- 💬 **Smart Comments** - Posts detailed, actionable review comments

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- GitHub Personal Access Token

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/changsheng0804-blip/pr-codex-reviewer.git
cd pr-codex-reviewer
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run the application**
```bash
python -m src.main
```

### GitHub Webhook Setup

1. Go to your repository settings
2. Navigate to Webhooks → Add webhook
3. Set Payload URL to your server URL + `/webhook`
4. Set Content type to `application/json`
5. Select events: **Pull requests**
6. Add webhook

## 🔧 Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ |
| `GITHUB_TOKEN` | GitHub Personal Access Token | ✅ |
| `GITHUB_WEBHOOK_SECRET` | Webhook secret for verification | ❌ |
| `OPENAI_MODEL` | Model to use (default: gpt-4) | ❌ |
| `MAX_FILES_PER_REVIEW` | Max files to review per PR | ❌ |

## 📖 Usage

### Automatic Review

Once configured, the bot will automatically review PRs when they are:
- Opened
- Updated with new commits

### Manual Review

You can also trigger a manual review via API:

```bash
curl -X POST http://localhost:8000/review/owner/repo/123
```

## 🛠️ Development

### Running Tests

```bash
pytest tests/ -v --cov=src
```

### Code Formatting

```bash
black src/ tests/
ruff check src/ tests/
```

### Type Checking

```bash
mypy src/
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t pr-codex-reviewer .

# Run container
docker run -p 8000:8000 --env-file .env pr-codex-reviewer
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Powered by [OpenAI Codex](https://openai.com/codex)
- Built for the open source community

## 📧 Contact

- GitHub: [@changsheng0804-blip](https://github.com/changsheng0804-blip)
- Project Link: [https://github.com/changsheng0804-blip/pr-codex-reviewer](https://github.com/changsheng0804-blip/pr-codex-reviewer)

---

⭐ Star this repo if you find it helpful!
