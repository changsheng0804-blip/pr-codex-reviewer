"""
GitHub API Client Module

This module encapsulates all interactions with the GitHub API, including:
- Fetching PR diffs
- Getting PR file lists
- Posting PR comments
- Submitting formal PR reviews

Design:
    Uses requests library for HTTP requests.
    All methods handle GitHub API authentication and error handling.
    
    For simple text comments, use post_pr_comment
    For code-specific comments, use post_review_comment
    For formal review conclusions, use submit_review

GitHub API Docs:
    https://docs.github.com/en/rest/pulls
"""

import requests
import base64
from typing import Dict, List, Optional
from src.config import Config


class GitHubClient:
    """
    GitHub API Client
    
    Encapsulates all GitHub API interactions with easy-to-use methods
    for fetching PR info and posting comments.
    
    Usage:
        client = GitHubClient()
        
        # Get PR files
        files = client.get_pr_files("owner", "repo", 123)
        
        # Post a comment
        client.post_pr_comment("owner", "repo", 123, "Great PR!")
        
        # Submit a review
        client.submit_review("owner", "repo", 123, "LGTM", event="APPROVE")
    
    Attributes:
        token: GitHub personal access token
        headers: HTTP headers for API requests
        base_url: GitHub API base URL
    """
    
    def __init__(self):
        """
        Initialize the GitHub client.
        
        Automatically reads the GitHub token from Config.
        Raises an error if the token is not configured.
        """
        self.token = Config.GITHUB_TOKEN
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"
    
    def get_pr_files(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """
        Get the list of files modified in a PR.
        
        Args:
            owner: Repository owner username
            repo: Repository name
            pr_number: PR number
            
        Returns:
            List[Dict]: List of file information, each containing:
                - filename: File path
                - status: File status (added/modified/removed)
                - additions: Number of lines added
                - deletions: Number of lines deleted
                - changes: Total number of changes
                - patch: Code diff content
                
        Example:
            files = client.get_pr_files("facebook", "react", 12345)
            for file in files:
                print(f"{file['filename']}: +{file['additions']} -{file['deletions']}")
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching PR files: {e}")
            return []
    
    def get_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """
        Get the diff content of a PR.
        
        Args:
            owner: Repository owner username
            repo: Repository name
            pr_number: PR number
            
        Returns:
            str: PR diff content
            
        Example:
            diff = client.get_pr_diff("facebook", "react", 12345)
            print(diff[:1000])  # Print first 1000 chars
        """
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"
        
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching PR diff: {e}")
            return ""
    
    def post_pr_comment(self, owner: str, repo: str, pr_number: int, body: str) -> bool:
        """
        Post a general comment on a PR.
        
        Args:
            owner: Repository owner username
            repo: Repository name
            pr_number: PR number
            body: Comment content (supports Markdown)
            
        Returns:
            bool: True if posted successfully, False otherwise
            
        Example:
            success = client.post_pr_comment(
                "facebook", "react", 12345,
                "## Review Summary\n\nThis PR looks great!"
            )
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        data = {"body": body}
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            print(f"Comment posted successfully: {response.json().get('html_url')}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error posting comment: {e}")
            return False
    
    def post_review_comment(self, owner: str, repo: str, pr_number: int, 
                           commit_id: str, path: str, line: int, body: str) -> bool:
        """
        Post a code review comment on a specific line.
        
        This is more specific than post_pr_comment - it attaches the comment
        to a specific line of code.
        
        Args:
            owner: Repository owner username
            repo: Repository name
            pr_number: PR number
            commit_id: Commit SHA
            path: File path
            line: Line number
            body: Comment content
            
        Returns:
            bool: True if posted successfully, False otherwise
            
        Example:
            client.post_review_comment(
                "facebook", "react", 12345,
                commit_id="abc123",
                path="src/components/Button.js",
                line=42,
                body="Consider using const here instead of let."
            )
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        data = {
            "body": body,
            "commit_id": commit_id,
            "path": path,
            "line": line
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error posting review comment: {e}")
            return False
    
    def submit_review(self, owner: str, repo: str, pr_number: int,
                     body: str, event: str = "COMMENT") -> bool:
        """
        Submit a formal PR review.
        
        This is the most formal way to review a PR. You can:
        - APPROVE: Approve the PR
        - REQUEST_CHANGES: Request changes
        - COMMENT: Just comment without approving or rejecting
        
        Args:
            owner: Repository owner username
            repo: Repository name
            pr_number: PR number
            body: Review summary content
            event: Review type (APPROVE/REQUEST_CHANGES/COMMENT)
            
        Returns:
            bool: True if submitted successfully, False otherwise
            
        Example:
            client.submit_review(
                "facebook", "react", 12345,
                body="## Review Result\n\nLGTM!",
                event="APPROVE"
            )
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        data = {
            "body": body,
            "event": event
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            print(f"Review submitted successfully: {event}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error submitting review: {e}")
            return False
