"""
GitHub API 客户端模块

这个模块封装了与GitHub API的所有交互，包括：
- 获取PR的代码差异（diff）
- 获取PR修改的文件列表
- 在PR上发布评论
- 提交正式的PR审查

设计思路:
    这个客户端使用 requests 库进行HTTP请求，
    所有方法都会处理GitHub API的认证和错误处理。
    
    对于简单的文本评论，使用 post_pr_comment
    对于带有代码定位的评论，使用 post_review_comment
    对于正式的审查结论，使用 submit_review

GitHub API 文档:
    https://docs.github.com/en/rest/pulls
"""

import requests
import base64
from typing import Dict, List, Optional
from .config import Config


class GitHubClient:
    """
    GitHub API 客户端
    
    这个类封装了所有与GitHub API的交互，提供了简单易用的方法
    来获取PR信息和发布评论。
    
    使用方法:
        client = GitHubClient()
        
        # 获取PR修改的文件
        files = client.get_pr_files("owner", "repo", 123)
        
        # 发布评论
        client.post_pr_comment("owner", "repo", 123, "代码看起来不错！")
    
    属性:
        token: GitHub Personal Access Token
        base_url: GitHub API基础URL
        headers: 请求头，包含认证信息
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        初始化GitHub客户端
        
        参数:
            token: GitHub Personal Access Token，
                   如果不提供，会从 Config.GITHUB_TOKEN 读取
        """
        self.token = token or Config.GITHUB_TOKEN
        self.base_url = "https://api.github.com"
        
        # 设置请求头，包含认证信息
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """
        获取PR的代码差异（diff格式）
        
        diff格式显示了文件的修改内容，包括添加和删除的行。
        这是代码审查的基础数据。
        
        参数:
            owner: 仓库所有者用户名
            repo: 仓库名称
            pr_number: PR编号
            
        返回:
            str: diff格式的文本内容
            
        示例:
            diff = client.get_pr_diff("facebook", "react", 12345)
            print(diff[:500])  # 打印前500字符
        """
        # 构建API URL
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        
        # 使用特殊的Accept头来获取diff格式
        headers = {**self.headers, "Accept": "application/vnd.github.v3.diff"}
        
        # 发送请求
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果出错会抛出异常
        
        return response.text
    
    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """
        获取PR修改的文件列表
        
        返回每个文件的详细信息，包括文件名、状态（新增/修改/删除）、
        修改行数、patch（代码差异）等。
        
        参数:
            owner: 仓库所有者用户名
            repo: 仓库名称
            pr_number: PR编号
            
        返回:
            List[Dict]: 文件信息列表，每个字典包含:
                - filename: 文件路径
                - status: 文件状态（added/modified/removed）
                - additions: 添加的行数
                - deletions: 删除的行数
                - changes: 总修改行数
                - patch: 代码差异文本
                
        示例:
            files = client.get_pr_files("owner", "repo", 123)
            for file in files:
                print(f"{file['filename']}: +{file['additions']}/-{file['deletions']}")
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def post_review_comment(self, owner: str, repo: str, pr_number: int,
                           body: str, commit_id: str, path: str,
                           line: int) -> Dict:
        """
        在PR的特定代码行上发布评论
        
        这种评论会显示在代码差异视图中，直接关联到具体代码行。
        适合指出具体代码问题。
        
        参数:
            owner: 仓库所有者用户名
            repo: 仓库名称
            pr_number: PR编号
            body: 评论内容（支持Markdown）
            commit_id: 提交SHA，用于定位代码版本
            path: 文件路径
            line: 代码行号
            
        返回:
            Dict: 创建的评论信息
            
        示例:
            client.post_review_comment(
                "owner", "repo", 123,
                body="这里可能有空指针风险",
                commit_id="abc123...",
                path="src/main.py",
                line=42
            )
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        
        data = {
            "body": body,
            "commit_id": commit_id,
            "path": path,
            "line": line
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        
        return response.json()
    
    def post_pr_comment(self, owner: str, repo: str, pr_number: int,
                       body: str) -> Dict:
        """
        在PR上发布一般性评论
        
        这种评论显示在PR的讨论区域，不关联特定代码行。
        适合发布总结性意见或一般性建议。
        
        参数:
            owner: 仓库所有者用户名
            repo: 仓库名称
            pr_number: PR编号
            body: 评论内容（支持Markdown）
            
        返回:
            Dict: 创建的评论信息
            
        示例:
            client.post_pr_comment(
                "owner", "repo", 123,
                body="## 审查总结\\n\\n整体代码质量良好..."
            )
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        
        data = {"body": body}
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        
        return response.json()
    
    def submit_review(self, owner: str, repo: str, pr_number: int,
                     body: str, event: str = "COMMENT") -> Dict:
        """
        提交正式的PR审查结论
        
        GitHub有三种审查结论：
        - COMMENT: 仅评论，不影响合并
        - APPROVE: 批准PR，允许合并
        - REQUEST_CHANGES: 请求修改，阻止合并
        
        参数:
            owner: 仓库所有者用户名
            repo: 仓库名称
            pr_number: PR编号
            body: 审查总结内容
            event: 审查结论类型，默认COMMENT
            
        返回:
            Dict: 审查信息
            
        示例:
            # 批准PR
            client.submit_review(
                "owner", "repo", 123,
                body="代码审查通过，可以合并",
                event="APPROVE"
            )
            
            # 请求修改
            client.submit_review(
                "owner", "repo", 123,
                body="请修复安全问题后再合并",
                event="REQUEST_CHANGES"
            )
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        
        data = {
            "body": body,
            "event": event
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        
        return response.json()
    
    def get_file_content(self, owner: str, repo: str, path: str,
                        ref: str) -> str:
        """
        获取文件的完整内容
        
        用于获取PR中修改文件的完整内容，以便进行更全面的分析。
        
        参数:
            owner: 仓库所有者用户名
            repo: 仓库名称
            path: 文件路径
            ref: 分支名或提交SHA
            
        返回:
            str: 文件内容（解码后的文本）
            
        示例:
            content = client.get_file_content(
                "owner", "repo",
                path="src/main.py",
                ref="main"
            )
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        
        response = requests.get(url, headers=self.headers, params={"ref": ref})
        response.raise_for_status()
        
        # GitHub API返回的内容是Base64编码的
        content = response.json()["content"]
        return base64.b64decode(content).decode("utf-8")
