"""
OpenAI Codex Code Analysis Module

This module is responsible for calling the OpenAI API for code analysis
and is the core intelligence component of the project.

Features:
    - Analyze potential issues in code (bugs, security vulnerabilities, performance issues, etc.)
    - Generate improvement suggestions
    - Create structured review reports

Design Approach:
    Uses OpenAI's ChatCompletion API, guiding the AI to perform code
    review through carefully designed prompts. The analysis results are
    parsed into structured data for downstream processing and presentation.

API Docs:
    https://platform.openai.com/docs/api-reference/chat
"""

import openai
from typing import Dict, List, Optional
from src.config import Config


class CodexAnalyzer:
    """
    OpenAI Codex Code Analyzer

    This class encapsulates the interaction with the OpenAI API and
    provides the core functionality of code analysis.

    Usage:
        analyzer = CodexAnalyzer()

        # Analyze code
        result = analyzer.analyze_code(
            code="def hello(): print('world')",
            language="python"
        )

        # View issues
        for issue in result["issues"]:
            print(f"Issue: {issue}")

    Attributes:
        api_key: OpenAI API key
        model: AI model to use
        max_tokens: Maximum token limit
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Codex analyzer.

        Args:
            api_key: OpenAI API key. If not provided, reads from Config.OPENAI_API_KEY
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        openai.api_key = self.api_key
        self.model = Config.OPENAI_MODEL
        self.max_tokens = Config.OPENAI_MAX_TOKENS

    def analyze_code(self, code: str, language: str,
                     context: Optional[str] = None) -> Dict:
        """
        Analyze code and return structured results.

        This method:
        1. Builds the analysis prompt (including code and review requirements)
        2. Calls the OpenAI API to get the analysis result
        3. Parses the result into structured data

        Args:
            code: Code text to analyze
            language: Programming language (e.g. "python", "javascript")
            context: Optional contextual information (e.g. filename, PR description)

        Returns:
            Dict: Structured analysis result containing:
                - issues: List of issues
                - suggestions: List of improvement suggestions
                - security: List of security issues
                - performance: List of performance issues
                - error: If an error occurred, contains the error message

        Example:
            code = '''
            def divide(a, b):
                return a / b
            '''

            result = analyzer.analyze_code(code, "python")

            if result.get("security"):
                print("Security issues found:")
                for issue in result["security"]:
                    print(f"  - {issue}")
        """
        # Build the analysis prompt
        prompt = self._build_analysis_prompt(code, language, context)

        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior code review expert. Analyze the provided code, "
                            "focusing on:\n"
                            "1. Potential bugs and logic errors\n"
                            "2. Security vulnerabilities (SQL injection, XSS, sensitive info leaks, etc.)\n"
                            "3. Code style and best practices\n"
                            "4. Performance optimization opportunities\n"
                            "5. Maintainability issues\n\n"
                            "Provide specific, actionable improvement suggestions."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )

            # Extract AI response
            analysis = response.choices[0].message.content

            # Parse into structured data
            return self._parse_analysis(analysis)

        except Exception as e:
            # Error handling: return a dictionary containing the error message
            return {
                "error": str(e),
                "issues": [],
                "suggestions": [],
                "security": [],
                "performance": []
            }

    def _build_analysis_prompt(self, code: str, language: str,
                               context: Optional[str]) -> str:
        """
        Build the code analysis prompt.

        This method formats the code and context into a prompt that
        the AI can understand. Uses Markdown code block formatting
        to help the AI recognize the code.

        Args:
            code: Code text
            language: Programming language
            context: Contextual information

        Returns:
            str: Formatted prompt text
        """
        # Build the base prompt
        prompt = f"Please review the following {language} code:\n\n"

        # Add the code block (using Markdown format)
        prompt += f"```{language}\n{code}\n```\n\n"

        # Add context (if any)
        if context:
            prompt += f"Context: {context}\n\n"

        # Specify the output format for easier parsing later
        prompt += "Please provide analysis results in the following format:\n\n"
        prompt += "ISSUES:\n"
        prompt += "- [Specific issue description, with location and suggestions]\n\n"
        prompt += "SUGGESTIONS:\n"
        prompt += "- [Improvement suggestions, with code examples]\n\n"
        prompt += "SECURITY:\n"
        prompt += "- [Security issues, if any]\n\n"
        prompt += "PERFORMANCE:\n"
        prompt += "- [Performance optimization suggestions, if any]\n"

        return prompt

    def _parse_analysis(self, analysis: str) -> Dict:
        """
        Parse the AI's analysis text into a structured dictionary.

        AI returns plain text; this method parses it into a structured
        dictionary for easier downstream processing and presentation.

        Parsing logic:
            1. Iterate through the text line by line
            2. Identify section headers (ISSUES:, SUGGESTIONS:, etc.)
            3. Collect list items under each section

        Args:
            analysis: AI analysis text

        Returns:
            Dict: Structured analysis result
        """
        # Initialize result dict
        result = {
            "issues": [],       # General issues
            "suggestions": [],  # Improvement suggestions
            "security": [],     # Security issues
            "performance": []   # Performance issues
        }

        current_section = None  # Current parsing section

        # Parse line by line
        for line in analysis.split("\n"):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Identify section headers
            if line.startswith("ISSUES:"):
                current_section = "issues"
            elif line.startswith("SUGGESTIONS:"):
                current_section = "suggestions"
            elif line.startswith("SECURITY:"):
                current_section = "security"
            elif line.startswith("PERFORMANCE:"):
                current_section = "performance"

            # Collect list items (lines starting with "- ")
            elif line.startswith("- ") and current_section:
                # Remove the "- " prefix and add to the current section
                item = line[2:].strip()
                if item:  # Make sure it is not an empty string
                    result[current_section].append(item)

        return result

    def generate_summary(self, file_analyses: List[Dict]) -> str:
        """
        Generate the PR review summary.

        Aggregates the analysis results of multiple files into a complete
        PR review report.

        Args:
            file_analyses: List of file analysis results, each element is an analysis dictionary

        Returns:
            str: Review summary in Markdown format

        Example:
            analyses = [
                {
                    "filename": "main.py",
                    "issues": ["Missing error handling"],
                    "security": ["SQL injection risk"]
                }
            ]

            summary = analyzer.generate_summary(analyses)
            print(summary)
        """
        # Count total issues by category
        total_issues = sum(len(a.get("issues", [])) for a in file_analyses)
        total_security = sum(len(a.get("security", [])) for a in file_analyses)
        total_suggestions = sum(len(a.get("suggestions", [])) for a in file_analyses)

        # Build Markdown summary
        summary = "## AI Code Review Report\n\n"

        # Statistics overview
        summary += "### Statistics Overview\n\n"
        summary += f"- **Issues found:** {total_issues}\n"
        summary += f"- **Security warnings:** {total_security}\n"
        summary += f"- **Improvement suggestions:** {total_suggestions}\n"
        summary += f"- **Files reviewed:** {len(file_analyses)}\n\n"

        # If there are security issues, add a warning
        if total_security > 0:
            summary += "> **Security issues found, please address before merging**\n\n"

        # Detailed analysis
        summary += "### Detailed Analysis\n\n"

        for analysis in file_analyses:
            filename = analysis.get("filename", "Unknown file")

            # Only show files with issues
            has_issues = (
                analysis.get("issues") or
                analysis.get("security") or
                analysis.get("suggestions")
            )

            if has_issues:
                summary += f"#### {filename}\n\n"

                # Show issues
                if analysis.get("issues"):
                    summary += "**Issues:**\n"
                    for issue in analysis["issues"]:
                        summary += f"- {issue}\n"
                    summary += "\n"

                # Show security issues
                if analysis.get("security"):
                    summary += "**Security:**\n"
                    for sec in analysis["security"]:
                        summary += f"- {sec}\n"
                    summary += "\n"

                # Show suggestions
                if analysis.get("suggestions"):
                    summary += "**Suggestions:**\n"
                    for suggestion in analysis["suggestions"]:
                        summary += f"- {suggestion}\n"
                    summary += "\n"

                # Show performance issues
                if analysis.get("performance"):
                    summary += "**Performance:**\n"
                    for perf in analysis["performance"]:
                        summary += f"- {perf}\n"
                    summary += "\n"

        # Add footer
        summary += "---\n\n"
        summary += "*Generated automatically by PR Codex Reviewer*\n"

        return summary
