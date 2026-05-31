"""
Main review engine that orchestrates the PR review process
"""
from typing import Dict, List, Optional
from .github_client import GitHubClient
from .codex_analyzer import CodexAnalyzer
from .config import Config


class ReviewEngine:
    """Main engine for reviewing pull requests"""
    
    def __init__(self):
        self.github = GitHubClient()
        self.analyzer = CodexAnalyzer()
    
    def review_pr(self, owner: str, repo: str, pr_number: int) -> Dict:
        """Review a pull request and post comments"""
        
        try:
            # Get PR files
            files = self.github.get_pr_files(owner, repo, pr_number)
            
            # Filter supported files
            supported_files = self._filter_supported_files(files)
            
            if not supported_files:
                return {
                    "status": "skipped",
                    "reason": "No supported files found in PR"
                }
            
            # Analyze each file
            analyses = []
            for file_info in supported_files:
                analysis = self._analyze_file(owner, repo, file_info)
                analyses.append(analysis)
            
            # Generate summary
            summary = self.analyzer.generate_summary(analyses)
            
            # Post review
            self.github.submit_review(
                owner, repo, pr_number,
                body=summary,
                event="COMMENT"
            )
            
            return {
                "status": "success",
                "files_reviewed": len(supported_files),
                "total_issues": sum(len(a.get("issues", [])) for a in analyses)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _filter_supported_files(self, files: List[Dict]) -> List[Dict]:
        """Filter files that we can analyze"""
        supported = []
        
        for file in files:
            filename = file.get("filename", "").lower()
            
            # Check file extension
            if any(filename.endswith(f".{ext}") for ext in Config.SUPPORTED_LANGUAGES):
                # Check file size
                if file.get("changes", 0) < Config.MAX_FILE_SIZE:
                    supported.append(file)
            
            # Limit number of files
            if len(supported) >= Config.MAX_FILES_PER_REVIEW:
                break
        
        return supported
    
    def _analyze_file(self, owner: str, repo: str, file_info: Dict) -> Dict:
        """Analyze a single file"""
        filename = file_info["filename"]
        patch = file_info.get("patch", "")
        
        # Determine language
        language = self._detect_language(filename)
        
        # Analyze the code
        analysis = self.analyzer.analyze_code(
            code=patch,
            language=language,
            context=f"File: {filename}"
        )
        
        return {
            "filename": filename,
            **analysis
        }
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename"""
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp"
        }
        
        for ext, lang in extension_map.items():
            if filename.endswith(ext):
                return lang
        
        return "unknown"
    
    def handle_webhook(self, payload: Dict) -> Dict:
        """Handle GitHub webhook payload"""
        
        # Check if it's a PR event
        if payload.get("action") not in ["opened", "synchronize"]:
            return {"status": "ignored", "reason": "Not a relevant PR event"}
        
        pr_data = payload.get("pull_request", {})
        if not pr_data:
            return {"status": "error", "reason": "No PR data found"}
        
        # Extract repository info
        repo_data = payload.get("repository", {})
        owner = repo_data.get("owner", {}).get("login")
        repo = repo_data.get("name")
        pr_number = pr_data.get("number")
        
        if not all([owner, repo, pr_number]):
            return {"status": "error", "reason": "Missing required information"}
        
        # Start review
        return self.review_pr(owner, repo, pr_number)
