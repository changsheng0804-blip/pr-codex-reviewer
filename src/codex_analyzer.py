"""
OpenAI Codex 代码分析模块

这个模块负责调用OpenAI API进行代码分析，是项目的核心智能组件。

功能:
    - 分析代码中的潜在问题（Bug、安全漏洞、性能问题）
    - 生成改进建议
    - 创建结构化的审查报告

设计思路:
    使用OpenAI的ChatCompletion API，通过精心设计的Prompt引导AI进行代码审查。
    分析结果会被解析为结构化数据，便于后续处理和展示。

API文档:
    https://platform.openai.com/docs/api-reference/chat
"""

import openai
from typing import Dict, List, Optional
from .config import Config


class CodexAnalyzer:
    """
    OpenAI Codex 代码分析器
    
    这个类封装了与OpenAI API的交互，提供了代码分析的核心功能。
    
    使用方法:
        analyzer = CodexAnalyzer()
        
        # 分析代码
        result = analyzer.analyze_code(
            code="def hello(): print('world')",
            language="python"
        )
        
        # 查看问题
        for issue in result["issues"]:
            print(f"问题: {issue}")
    
    属性:
        api_key: OpenAI API密钥
        model: 使用的AI模型
        max_tokens: 最大Token数限制
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Codex分析器
        
        参数:
            api_key: OpenAI API密钥，
                    如果不提供，会从 Config.OPENAI_API_KEY 读取
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        openai.api_key = self.api_key
        self.model = Config.OPENAI_MODEL
        self.max_tokens = Config.OPENAI_MAX_TOKENS
    
    def analyze_code(self, code: str, language: str,
                    context: Optional[str] = None) -> Dict:
        """
        分析代码并返回结构化结果
        
        这个方法会:
        1. 构建分析Prompt（包含代码和审查要求）
        2. 调用OpenAI API获取分析结果
        3. 解析结果为结构化数据
        
        参数:
            code: 要分析的代码文本
            language: 编程语言（如 "python", "javascript"）
            context: 可选的上下文信息（如文件名、PR描述等）
            
        返回:
            Dict: 结构化分析结果，包含:
                - issues: 问题列表
                - suggestions: 建议列表
                - security: 安全问题列表
                - performance: 性能问题列表
                - error: 如果出错，包含错误信息
                
        示例:
            code = '''
            def divide(a, b):
                return a / b
            '''
            
            result = analyzer.analyze_code(code, "python")
            
            if result.get("security"):
                print("发现安全问题！")
                for issue in result["security"]:
                    print(f"  - {issue}")
        """
        
        # 构建分析Prompt
        prompt = self._build_analysis_prompt(code, language, context)
        
        try:
            # 调用OpenAI API
            # 使用ChatCompletion API，因为它对指令遵循更好
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是一位资深的代码审查专家。请分析提供的代码，"
                            "重点关注以下方面:\n"
                            "1. 潜在的Bug和逻辑错误\n"
                            "2. 安全漏洞（如SQL注入、XSS、敏感信息泄露等）\n"
                            "3. 代码风格和最佳实践\n"
                            "4. 性能优化机会\n"
                            "5. 可维护性问题\n\n"
                            "请提供具体、可操作的改进建议。"
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.3  # 较低的温度使输出更稳定、更确定
            )
            
            # 提取AI的回复文本
            analysis = response.choices[0].message.content
            
            # 解析为结构化数据
            return self._parse_analysis(analysis)
            
        except Exception as e:
            # 错误处理：返回包含错误信息的字典
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
        构建代码分析Prompt
        
        这个方法将代码和上下文信息格式化为AI可以理解的Prompt。
        使用Markdown代码块格式，帮助AI识别代码。
        
        参数:
            code: 代码文本
            language: 编程语言
            context: 上下文信息
            
        返回:
            str: 格式化的Prompt文本
        """
        # 构建基础Prompt
        prompt = f"请审查以下{language}代码:\n\n"
        
        # 添加代码块（使用Markdown格式）
        prompt += f"```{language}\n{code}\n```\n\n"
        
        # 添加上下文（如果有）
        if context:
            prompt += f"上下文信息: {context}\n\n"
        
        # 指定输出格式，便于后续解析
        prompt += "请按以下格式提供分析结果:\n\n"
        prompt += "ISSUES:\n"
        prompt += "- [具体问题描述，包含位置和建议]\n\n"
        prompt += "SUGGESTIONS:\n"
        prompt += "- [改进建议，包含代码示例]\n\n"
        prompt += "SECURITY:\n"
        prompt += "- [安全问题，如果有]\n\n"
        prompt += "PERFORMANCE:\n"
        prompt += "- [性能优化建议，如果有]\n"
        
        return prompt
    
    def _parse_analysis(self, analysis: str) -> Dict:
        """
        解析AI的分析文本为结构化数据
        
        AI返回的是纯文本，这个方法将其解析为结构化的字典，
        方便后续处理和展示。
        
        解析逻辑:
            1. 按行遍历文本
            2. 识别章节标题（ISSUES:, SUGGESTIONS:等）
            3. 收集每个章节下的列表项
        
        参数:
            analysis: AI返回的分析文本
            
        返回:
            Dict: 结构化分析结果
        """
        # 初始化结果字典
        result = {
            "issues": [],       # 一般性问题
            "suggestions": [],  # 改进建议
            "security": [],     # 安全问题
            "performance": []   # 性能问题
        }
        
        current_section = None  # 当前正在解析的章节
        
        # 逐行解析
        for line in analysis.split("\n"):
            line = line.strip()
            
            # 跳过空行
            if not line:
                continue
            
            # 识别章节标题
            if line.startswith("ISSUES:"):
                current_section = "issues"
            elif line.startswith("SUGGESTIONS:"):
                current_section = "suggestions"
            elif line.startswith("SECURITY:"):
                current_section = "security"
            elif line.startswith("PERFORMANCE:"):
                current_section = "performance"
            
            # 收集列表项（以"- "开头的行）
            elif line.startswith("- ") and current_section:
                # 去掉"- "前缀，添加到当前章节
                item = line[2:].strip()
                if item:  # 确保不是空字符串
                    result[current_section].append(item)
        
        return result
    
    def generate_summary(self, file_analyses: List[Dict]) -> str:
        """
        生成PR审查总结
        
        将多个文件的分析结果汇总为一份完整的PR审查报告。
        
        参数:
            file_analyses: 文件分析结果列表，每个元素是一个分析字典
            
        返回:
            str: Markdown格式的审查总结
            
        示例:
            analyses = [
                {
                    "filename": "main.py",
                    "issues": ["缺少错误处理"],
                    "security": ["SQL注入风险"]
                }
            ]
            
            summary = analyzer.generate_summary(analyses)
            print(summary)
        """
        # 统计各类问题的总数
        total_issues = sum(len(a.get("issues", [])) for a in file_analyses)
        total_security = sum(len(a.get("security", [])) for a in file_analyses)
        total_suggestions = sum(len(a.get("suggestions", [])) for a in file_analyses)
        
        # 构建Markdown总结
        summary = "## 🤖 AI 代码审查报告\n\n"
        
        # 统计概览
        summary += "### 📊 统计概览\n\n"
        summary += f"- **发现问题:** {total_issues} 个\n"
        summary += f"- **安全警告:** {total_security} 个\n"
        summary += f"- **改进建议:** {total_suggestions} 个\n"
        summary += f"- **审查文件:** {len(file_analyses)} 个\n\n"
        
        # 如果有安全问题，添加警告
        if total_security > 0:
            summary += "⚠️ **发现安全问题，请在合并前处理**\n\n"
        
        # 详细分析
        summary += "### 🔍 详细分析\n\n"
        
        for analysis in file_analyses:
            filename = analysis.get("filename", "未知文件")
            
            # 只显示有问题的文件
            has_issues = (
                analysis.get("issues") or
                analysis.get("security") or
                analysis.get("suggestions")
            )
            
            if has_issues:
                summary += f"#### 📄 {filename}\n\n"
                
                # 显示问题
                if analysis.get("issues"):
                    summary += "**❌ 问题:**\n"
                    for issue in analysis["issues"]:
                        summary += f"- {issue}\n"
                    summary += "\n"
                
                # 显示安全问题
                if analysis.get("security"):
                    summary += "**🔒 安全:**\n"
                    for sec in analysis["security"]:
                        summary += f"- ⚠️ {sec}\n"
                    summary += "\n"
                
                # 显示建议
                if analysis.get("suggestions"):
                    summary += "**💡 建议:**\n"
                    for suggestion in analysis["suggestions"]:
                        summary += f"- {suggestion}\n"
                    summary += "\n"
                
                # 显示性能问题
                if analysis.get("performance"):
                    summary += "**⚡ 性能:**\n"
                    for perf in analysis["performance"]:
                        summary += f"- {perf}\n"
                    summary += "\n"
        
        # 添加页脚
        summary += "---\n\n"
        summary += "*由 PR Codex Reviewer 自动生成*\n"
        
        return summary
