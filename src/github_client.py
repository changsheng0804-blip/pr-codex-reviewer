"""
GitHub API client for PR Codex Reviewer
"""
import requests
from typing import Dict, List, Optional, Any
from .config import Config


class GitHubClient:
    """Client for interacting with GitHub API"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or Config.GITHUB_TOKEN
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Get the diff of a pull request"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = {**self.headers, "Accept": "application/vnd.github.v3.diff"}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    
    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Get list of files changed in a PR"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def post_review_comment(self, owner: str, repo: str, pr_number: int, 
                           body: str, commit_id: str, path: str, 
                           line: int) -> Dict:
        """Post a review comment on a specific line"""
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
        """Post a general comment on the PR"""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        
        data = {"body": body}
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def submit_review(self, owner: str, repo: str, pr_number: int,
                     body: str, event: str = "COMMENT") -> Dict:
        """Submit a PR review"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        
        data = {
            "body": body,
            "event": event  # APPROVE, REQUEST_CHANGES, or COMMENT
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def get_file_content(self, owner: str, repo: str, path: str, 
                        ref: str) -> str:
        """Get content of a file"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        
        response = requests.get(url, headers=self.headers, params={"ref": ref})
        response.raise_for_status()
        
        import base64
        content = response.json()["content"]
        return base64.b64decode(content).decode("utf-8")
