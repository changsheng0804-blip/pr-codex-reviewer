"""
配置模块 - PR Codex Reviewer

这个模块负责管理应用的所有配置项，包括：
- OpenAI API 配置（模型选择、Token限制等）
- GitHub API 配置（认证、Webhook密钥等）
- 代码审查配置（支持的语言、文件大小限制等）
- 服务器配置（端口、主机、调试模式等）

使用方法:
    from src.config import Config
    
    # 验证配置是否完整
    Config.validate()
    
    # 访问配置项
    print(Config.OPENAI_MODEL)  # 输出: gpt-4

环境变量:
    所有配置都可以通过环境变量设置，详见 .env.example 文件
"""

import os
from typing import Optional


class Config:
    """
    应用配置类
    
    这个类使用类属性存储所有配置，方便全局访问。
    所有配置项都有默认值，但建议通过环境变量覆盖。
    
    属性:
        OPENAI_API_KEY: OpenAI API 密钥，用于调用 GPT-4/Codex
        OPENAI_MODEL: 使用的AI模型，默认 gpt-4
        OPENAI_MAX_TOKENS: 每次请求的最大Token数，默认2000
        GITHUB_TOKEN: GitHub Personal Access Token
        GITHUB_WEBHOOK_SECRET: GitHub Webhook 密钥（可选，用于验证请求）
        MAX_FILES_PER_REVIEW: 每次审查的最大文件数，防止超出Token限制
        MAX_FILE_SIZE: 最大文件大小（字节），过滤过大的文件
        SUPPORTED_LANGUAGES: 支持的编程语言列表
        PORT: 服务器端口，默认8000
        HOST: 服务器主机，默认0.0.0.0（监听所有接口）
        DEBUG: 调试模式，默认False
    """
    
    # ==================== OpenAI 配置 ====================
    # 这些配置控制AI代码分析的行为
    
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    """OpenAI API 密钥 - 必须设置，用于调用AI模型"""
    
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    """使用的AI模型 - 可选，默认gpt-4，也可使用gpt-3.5-turbo降低成本"""
    
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    """每次请求的最大Token数 - 控制响应长度和成本"""
    
    # ==================== GitHub 配置 ====================
    # 这些配置控制与GitHub API的交互
    
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    """GitHub Personal Access Token - 必须设置，用于访问仓库和发布评论"""
    
    GITHUB_WEBHOOK_SECRET: Optional[str] = os.getenv("GITHUB_WEBHOOK_SECRET")
    """GitHub Webhook 密钥 - 可选，用于验证Webhook请求的真实性"""
    
    # ==================== 审查配置 ====================
    # 这些配置控制代码审查的行为和限制
    
    MAX_FILES_PER_REVIEW: int = int(os.getenv("MAX_FILES_PER_REVIEW", "10"))
    """每次审查的最大文件数 - 防止PR过大导致超时或超出Token限制"""
    
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "100000"))
    """最大文件大小（字节，约100KB）- 过滤过大的文件，如生成的代码、数据文件等"""
    
    SUPPORTED_LANGUAGES: list = [
        "python",      # Python - 主要支持语言
        "javascript",  # JavaScript - Web开发
        "typescript",  # TypeScript - 带类型的JavaScript
        "java",        # Java - 企业级开发
        "go",          # Go - 云原生开发
        "rust",        # Rust - 系统编程
        "cpp",         # C++ - 系统/游戏开发
        "c"            # C - 底层开发
    ]
    """支持的编程语言列表 - 只有这些语言的文件会被分析"""
    
    # ==================== 服务器配置 ====================
    # 这些配置控制Flask服务器的运行参数
    
    PORT: int = int(os.getenv("PORT", "8000"))
    """服务器端口 - 默认8000，部署时可能被云平台覆盖"""
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    """服务器主机 - 默认0.0.0.0表示监听所有网络接口"""
    
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    """调试模式 - 开启后会显示详细的错误信息，生产环境应关闭"""
    
    @classmethod
    def validate(cls) -> bool:
        """
        验证必需配置是否已设置
        
        这个方法检查所有必需的配置项（API密钥等）是否已设置。
        如果缺少必需配置，会抛出 ValueError 异常。
        
        返回:
            bool: 验证成功返回True
            
        抛出:
            ValueError: 当缺少必需的环境变量时
            
        示例:
            try:
                Config.validate()
                print("配置验证通过")
            except ValueError as e:
                print(f"配置错误: {e}")
        """
        # 定义必需的环境变量
        required_vars = ["OPENAI_API_KEY", "GITHUB_TOKEN"]
        
        # 检查每个必需变量
        missing = []
        for var in required_vars:
            value = getattr(cls, var)
            if not value or value.strip() == "":
                missing.append(var)
        
        # 如果有缺失的变量，抛出异常
        if missing:
            raise ValueError(
                f"缺少必需的环境变量: {', '.join(missing)}\n"
                f"请复制 .env.example 为 .env 并填写相应的值"
            )
        
        return True
    
    @classmethod
    def get_openai_config(cls) -> dict:
        """
        获取OpenAI相关的配置字典
        
        方便传递给OpenAI客户端使用
        
        返回:
            dict: 包含api_key, model, max_tokens的字典
        """
        return {
            "api_key": cls.OPENAI_API_KEY,
            "model": cls.OPENAI_MODEL,
            "max_tokens": cls.OPENAI_MAX_TOKENS
        }
    
    @classmethod
    def get_github_config(cls) -> dict:
        """
        获取GitHub相关的配置字典
        
        方便传递给GitHub客户端使用
        
        返回:
            dict: 包含token, webhook_secret的字典
        """
        return {
            "token": cls.GITHUB_TOKEN,
            "webhook_secret": cls.GITHUB_WEBHOOK_SECRET
        }
