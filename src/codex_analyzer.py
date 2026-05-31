"""
OpenAI Codex analyzer for code review
"""
import openai
from typing import Dict, List, Optional
from .config import Config


class CodexAnalyzer:
    """Analyzer using OpenAI API for code review"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        openai.api_key = self.api_key
        self.model = Config.OPENAI_MODEL
        self.max_tokens = Config.OPENAI_MAX_TOKENS
    
    def analyze_code(self, code: str, language: str, 
                    context: Optional[str] = None) -> Dict:
        """Analyze code for issues and improvements"""
        
        prompt = self._build_analysis_prompt(code, language, context)
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code reviewer. Analyze the provided code for: "
                                  "1. Bugs and potential errors, "
                                  "2. Security vulnerabilities, "
                                  "3. Code style issues, "
                                  "4. Performance improvements, "
                                  "5. Best practices violations. "
                                  "Provide specific, actionable feedback."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            return self._parse_analysis(analysis)
            
        except Exception as e:
            return {
                "error": str(e),
                "issues": [],
                "suggestions": []
            }
    
    def _build_analysis_prompt(self, code: str, language: str, 
                              context: Optional[str]) -> str:
        """Build the analysis prompt"""
        prompt = f"Please review the following {language} code:\n\n"
        prompt += f"```{language}\n{code}\n```\n\n"
        
        if context:
            prompt += f"Context: {context}\n\n"
        
        prompt += "Please provide your analysis in the following format:\n"
        prompt += "ISSUES:\n- [Issue description]\n\n"
        prompt += "SUGGESTIONS:\n- [Suggestion with code example]\n\n"
        prompt += "SECURITY:\n- [Security concern if any]\n\n"
        prompt += "PERFORMANCE:\n- [Performance improvement if any]"
        
        return prompt
    
    def _parse_analysis(self, analysis: str) -> Dict:
        """Parse the analysis response"""
        result = {
            "issues": [],
            "suggestions": [],
            "security": [],
            "performance": []
        }
        
        current_section = None
        
        for line in analysis.split("\n"):
            line = line.strip()
            
            if line.startswith("ISSUES:"):
                current_section = "issues"
            elif line.startswith("SUGGESTIONS:"):
                current_section = "suggestions"
            elif line.startswith("SECURITY:"):
                current_section = "security"
            elif line.startswith("PERFORMANCE:"):
                current_section = "performance"
            elif line.startswith("- ") and current_section:
                result[current_section].append(line[2:])
        
        return result
    
    def generate_summary(self, file_analyses: List[Dict]) -> str:
        """Generate a summary of all file analyses"""
        total_issues = sum(len(a.get("issues", [])) for a in file_analyses)
        total_security = sum(len(a.get("security", [])) for a in file_analyses)
        
        summary = f"## 🤖 AI Code Review Summary\n\n"
        summary += f"**Total Issues Found:** {total_issues}\n"
        summary += f"**Security Concerns:** {total_security}\n\n"
        
        if total_security > 0:
            summary += "⚠️ **Please address security concerns before merging**\n\n"
        
        summary += "### Detailed Analysis\n\n"
        
        for i, analysis in enumerate(file_analyses, 1):
            if analysis.get("issues") or analysis.get("security"):
                summary += f"#### File {i}\n"
                
                if analysis.get("issues"):
                    summary += "**Issues:**\n"
                    for issue in analysis["issues"]:
                        summary += f"- {issue}\n"
                    summary += "\n"
                
                if analysis.get("security"):
                    summary += "**Security:**\n"
                    for sec in analysis["security"]:
                        summary += f"- ⚠️ {sec}\n"
                    summary += "\n"
        
        return summary
