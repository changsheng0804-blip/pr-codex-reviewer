"""
代码审查引擎模块

这个模块是项目的核心协调器，负责：
1. 接收PR审查请求（来自Webhook或手动调用）
2. 获取PR的代码变更
3. 调用AI分析代码
4. 生成并发布审查报告

工作流程:
    1. GitHub Webhook触发 → handle_webhook()
    2. 提取PR信息 → review_pr()
    3. 获取修改的文件 → get_pr_files()
    4. 过滤支持的文件 → _filter_supported_files()
    5. 分析每个文件 → _analyze_file()
    6. 生成总结报告 → generate_summary()
    7. 发布审查结果 → submit_review()

设计模式:
    使用组合模式，将GitHubClient和CodexAnalyzer组合在一起，
    协调它们完成完整的审查流程。
"""

from typing import Dict, List, Optional
from .github_client import GitHubClient
from .codex_analyzer import CodexAnalyzer
from .config import Config


class ReviewEngine:
    """
    PR审查引擎
    
    这是项目的主要协调类，负责管理整个代码审查流程。
    
    使用方法:
        engine = ReviewEngine()
        
        # 审查特定PR
        result = engine.review_pr("owner", "repo", 123)
        print(f"审查了 {result['files_reviewed']} 个文件")
        
        # 处理Webhook
        payload = {...}  # GitHub Webhook数据
        result = engine.handle_webhook(payload)
    
    属性:
        github: GitHub API客户端
        analyzer: AI代码分析器
    """
    
    def __init__(self):
        """
        初始化审查引擎
        
        自动创建所需的GitHubClient和CodexAnalyzer实例。
        """
        self.github = GitHubClient()
        self.analyzer = CodexAnalyzer()
    
    def review_pr(self, owner: str, repo: str, pr_number: int) -> Dict:
        """
        审查一个PR并发布结果
        
        这是主要的审查方法，执行完整的审查流程：
        1. 获取PR修改的文件列表
        2. 过滤出支持的文件
        3. 分析每个文件
        4. 生成总结报告
        5. 发布审查评论
        
        参数:
            owner: 仓库所有者用户名
            repo: 仓库名称
            pr_number: PR编号
            
        返回:
            Dict: 审查结果，包含:
                - status: 状态（success/skipped/error）
                - files_reviewed: 审查的文件数
                - total_issues: 发现的问题数
                - reason: 如果跳过或出错，说明原因
                - error: 如果出错，包含错误信息
                
        示例:
            result = engine.review_pr("facebook", "react", 12345)
            
            if result["status"] == "success":
                print(f"审查完成！发现 {result['total_issues']} 个问题")
            elif result["status"] == "skipped":
                print(f"跳过: {result['reason']}")
            else:
                print(f"错误: {result['error']}")
        """
        
        try:
            # 步骤1: 获取PR修改的文件
            print(f"正在获取 PR #{pr_number} 的文件列表...")
            files = self.github.get_pr_files(owner, repo, pr_number)
            
            # 步骤2: 过滤支持的文件
            supported_files = self._filter_supported_files(files)
            
            # 如果没有支持的文件，跳过审查
            if not supported_files:
                return {
                    "status": "skipped",
                    "reason": "没有需要审查的文件（不支持的格式或文件过大）"
                }
            
            print(f"找到 {len(supported_files)} 个需要审查的文件")
            
            # 步骤3: 分析每个文件
            analyses = []
            for i, file_info in enumerate(supported_files, 1):
                print(f"正在分析文件 {i}/{len(supported_files)}: {file_info['filename']}")
                analysis = self._analyze_file(owner, repo, file_info)
                analyses.append(analysis)
            
            # 步骤4: 生成总结报告
            print("正在生成审查报告...")
            summary = self.analyzer.generate_summary(analyses)
            
            # 步骤5: 发布审查结果
            print("正在发布审查评论...")
            self.github.submit_review(
                owner, repo, pr_number,
                body=summary,
                event="COMMENT"  # 仅评论，不阻止合并
            )
            
            # 计算统计信息
            total_issues = sum(len(a.get("issues", [])) for a in analyses)
            
            print(f"审查完成！发现 {total_issues} 个问题")
            
            return {
                "status": "success",
                "files_reviewed": len(supported_files),
                "total_issues": total_issues
            }
            
        except Exception as e:
            # 错误处理
            error_msg = str(e)
            print(f"审查失败: {error_msg}")
            
            return {
                "status": "error",
                "error": error_msg
            }
    
    def _filter_supported_files(self, files: List[Dict]) -> List[Dict]:
        """
        过滤出支持审查的文件
        
        根据以下条件过滤：
        1. 文件扩展名在支持列表中
        2. 文件大小不超过限制
        3. 数量不超过限制
        
        参数:
            files: GitHub API返回的文件列表
            
        返回:
            List[Dict]: 过滤后的文件列表
        """
        supported = []
        
        for file in files:
            filename = file.get("filename", "").lower()
            
            # 检查1: 文件扩展名是否支持
            is_supported = any(
                filename.endswith(f".{ext}")
                for ext in Config.SUPPORTED_LANGUAGES
            )
            
            if not is_supported:
                continue  # 跳过不支持的文件
            
            # 检查2: 文件大小是否超过限制
            file_size = file.get("changes", 0)
            if file_size > Config.MAX_FILE_SIZE:
                print(f"跳过过大的文件: {filename} ({file_size} 字节)")
                continue
            
            # 添加到支持列表
            supported.append(file)
            
            # 检查3: 是否达到数量限制
            if len(supported) >= Config.MAX_FILES_PER_REVIEW:
                print(f"已达到最大文件数限制 ({Config.MAX_FILES_PER_REVIEW})")
                break
        
        return supported
    
    def _analyze_file(self, owner: str, repo: str, file_info: Dict) -> Dict:
        """
        分析单个文件
        
        从GitHub获取文件的patch（代码差异），然后调用AI进行分析。
        
        参数:
            owner: 仓库所有者
            repo: 仓库名称
            file_info: 文件信息字典（来自GitHub API）
            
        返回:
            Dict: 分析结果，包含文件名和各类问题
        """
        filename = file_info["filename"]
        patch = file_info.get("patch", "")
        
        # 自动检测编程语言
        language = self._detect_language(filename)
        
        # 调用AI分析代码
        analysis = self.analyzer.analyze_code(
            code=patch,
            language=language,
            context=f"文件: {filename}"
        )
        
        # 添加文件名到分析结果
        return {
            "filename": filename,
            **analysis
        }
    
    def _detect_language(self, filename: str) -> str:
        """
        根据文件名检测编程语言
        
        使用文件扩展名映射到语言名称。
        
        参数:
            filename: 文件名（包含扩展名）
            
        返回:
            str: 语言名称，如果未知返回 "unknown"
            
        示例:
            engine._detect_language("main.py")      # 返回: "python"
            engine._detect_language("app.js")       # 返回: "javascript"
            engine._detect_language("unknown.xyz")  # 返回: "unknown"
        """
        # 扩展名到语言的映射表
        extension_map = {
            # Python
            ".py": "python",
            ".pyw": "python",
            ".pyi": "python",
            
            # JavaScript/TypeScript
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            
            # Java
            ".java": "java",
            
            # Go
            ".go": "go",
            
            # Rust
            ".rs": "rust",
            
            # C/C++
            ".cpp": "cpp",
            ".cxx": "cpp",
            ".cc": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp"
        }
        
        # 转换为小写并查找
        filename_lower = filename.lower()
        for ext, lang in extension_map.items():
            if filename_lower.endswith(ext):
                return lang
        
        return "unknown"
    
    def handle_webhook(self, payload: Dict) -> Dict:
        """
        处理GitHub Webhook请求
        
        解析Webhook的JSON数据，提取PR信息，然后调用审查流程。
        
        支持的Webhook事件:
            - pull_request.opened: PR被创建
            - pull_request.synchronize: PR被更新（推送新提交）
        
        参数:
            payload: GitHub Webhook的JSON数据
            
        返回:
            Dict: 处理结果
            
        示例:
            from flask import request
            
            @app.route('/webhook', methods=['POST'])
            def webhook():
                payload = request.get_json()
                result = engine.handle_webhook(payload)
                return jsonify(result)
        """
        
        # 检查事件类型
        action = payload.get("action")
        if action not in ["opened", "synchronize"]:
            return {
                "status": "ignored",
                "reason": f"不处理 '{action}' 事件，只处理 opened 和 synchronize"
            }
        
        # 提取PR数据
        pr_data = payload.get("pull_request", {})
        if not pr_data:
            return {
                "status": "error",
                "reason": "Webhook数据中没有找到PR信息"
            }
        
        # 提取仓库信息
        repo_data = payload.get("repository", {})
        owner = repo_data.get("owner", {}).get("login")
        repo = repo_data.get("name")
        pr_number = pr_data.get("number")
        
        # 验证必需信息
        if not all([owner, repo, pr_number]):
            return {
                "status": "error",
                "reason": "缺少必需的仓库或PR信息"
            }
        
        print(f"收到PR事件: {owner}/{repo}#{pr_number} ({action})")
        
        # 开始审查
        return self.review_pr(owner, repo, pr_number)
