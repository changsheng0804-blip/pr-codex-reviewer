"""
Tests for GitHubClient
"""
import pytest
from unittest.mock import Mock, patch
from src.github_client import GitHubClient


class TestGitHubClient:
    """Test cases for GitHubClient"""
    
    @patch("src.github_client.Config")
    def test_init(self, mock_config):
        """Test client initialization"""
        mock_config.GITHUB_TOKEN = "test-token"
        client = GitHubClient()
        assert client.token == "test-token"
        assert client.headers["Authorization"] == "token test-token"
    
    @patch("src.github_client.Config")
    @patch("src.github_client.requests.get")
    def test_get_pr_files(self, mock_get, mock_config):
        """Test getting PR files"""
        mock_config.GITHUB_TOKEN = "test-token"
        mock_response = Mock()
        mock_response.json.return_value = [
            {"filename": "test.py", "status": "modified"}
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        client = GitHubClient()
        files = client.get_pr_files("owner", "repo", 1)
        
        assert len(files) == 1
        assert files[0]["filename"] == "test.py"
    
    @patch("src.github_client.Config")
    @patch("src.github_client.requests.post")
    def test_post_pr_comment(self, mock_post, mock_config):
        """Test posting PR comment"""
        mock_config.GITHUB_TOKEN = "test-token"
        mock_response = Mock()
        mock_response.json.return_value = {"id": 123}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = GitHubClient()
        result = client.post_pr_comment("owner", "repo", 1, "Test comment")
        
        # post_pr_comment returns bool: True on success, False on failure
        assert result is True
