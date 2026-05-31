"""
Tests for CodexAnalyzer
"""
import pytest
from src.codex_analyzer import CodexAnalyzer


class TestCodexAnalyzer:
    """Test cases for CodexAnalyzer"""
    
    def test_init(self):
        """Test analyzer initialization"""
        analyzer = CodexAnalyzer(api_key="test-key")
        assert analyzer.api_key == "test-key"
    
    def test_detect_language(self):
        """Test language detection"""
        analyzer = CodexAnalyzer()
        
        assert analyzer._detect_language("test.py") == "python"
        assert analyzer._detect_language("test.js") == "javascript"
        assert analyzer._detect_language("test.ts") == "typescript"
        assert analyzer._detect_language("test.java") == "java"
        assert analyzer._detect_language("test.go") == "go"
        assert analyzer._detect_language("test.unknown") == "unknown"
    
    def test_parse_analysis(self):
        """Test analysis parsing"""
        analyzer = CodexAnalyzer()
        
        analysis_text = """
        ISSUES:
        - Bug in line 10
        - Missing error handling
        
        SUGGESTIONS:
        - Use try-except
        
        SECURITY:
        - SQL injection risk
        
        PERFORMANCE:
        - Use list comprehension
        """
        
        result = analyzer._parse_analysis(analysis_text)
        
        assert len(result["issues"]) == 2
        assert len(result["suggestions"]) == 1
        assert len(result["security"]) == 1
        assert len(result["performance"]) == 1
    
    def test_generate_summary(self):
        """Test summary generation"""
        analyzer = CodexAnalyzer()
        
        analyses = [
            {
                "issues": ["Bug 1", "Bug 2"],
                "security": ["Security issue"],
                "suggestions": ["Suggestion 1"]
            },
            {
                "issues": ["Bug 3"],
                "security": [],
                "suggestions": []
            }
        ]
        
        summary = analyzer.generate_summary(analyses)
        
        assert "Total Issues Found: 3" in summary
        assert "Security Concerns: 1" in summary
        assert "⚠️" in summary
