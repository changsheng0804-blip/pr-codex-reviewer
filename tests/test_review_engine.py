"""
Tests for ReviewEngine
"""
import pytest
from unittest.mock import Mock, patch
from src.review_engine import ReviewEngine


class TestReviewEngine:
    """Test cases for ReviewEngine"""
    
    def test_init(self):
        """Test engine initialization"""
        engine = ReviewEngine()
        assert engine.github is not None
        assert engine.analyzer is not None
    
    def test_filter_supported_files(self):
        """Test filtering supported files"""
        engine = ReviewEngine()
        
        files = [
            {"filename": "test.py", "changes": 100},
            {"filename": "test.js", "changes": 200},
            {"filename": "test.txt", "changes": 50},  # Not supported
            {"filename": "test.py", "changes": 999999999},  # Too large
        ]
        
        supported = engine._filter_supported_files(files)
        
        assert len(supported) == 2
        assert supported[0]["filename"] == "test.py"
        assert supported[1]["filename"] == "test.js"
    
    def test_detect_language(self):
        """Test language detection"""
        engine = ReviewEngine()
        
        assert engine._detect_language("test.py") == "python"
        assert engine._detect_language("test.js") == "javascript"
        assert engine._detect_language("test.unknown") == "unknown"
    
    def test_handle_webhook_invalid_event(self):
        """Test webhook handling with invalid event"""
        engine = ReviewEngine()
        
        payload = {
            "action": "closed",  # Not supported
            "pull_request": {},
            "repository": {}
        }
        
        result = engine.handle_webhook(payload)
        
        assert result["status"] == "ignored"
