"""
Code Review Engine Module

This module is the core coordinator of the project, responsible for:
1. Receiving PR review requests (from Webhook or manual invocation)
2. Fetching PR code changes
3. Calling AI for code analysis
4. Generating and posting review reports

Workflow:
    1. GitHub Webhook trigger -> handle_webhook()
    2. Extract PR information -> review_pr()
    3. Get modified files -> get_pr_files()
    4. Filter supported files -> _filter_supported_files()
    5. Analyze each file -> _analyze_file()
    6. Generate summary report -> generate_summary()
    7. Post review result -> submit_review()

Design Pattern:
    Uses a composite pattern, combining GitHubClient and CodexAnalyzer
    to coordinate them in completing the full review workflow.
"""

from typing import Dict, List, Optional
from src.github_client import GitHubClient
from src.codex_analyzer import CodexAnalyzer
from src.config import Config


class ReviewEngine:
    """
    PR Review Engine

    This is the main coordinator class of the project, responsible for
    managing the entire code review workflow.

    Usage:
        engine = ReviewEngine()

        # Review a specific PR
        result = engine.review_pr("owner", "repo", 123)
        print(f"Reviewed {result['files_reviewed']} files")

        # Process a Webhook
        payload = {...}  # GitHub Webhook data
        result = engine.handle_webhook(payload)

    Attributes:
        github: GitHub API client
        analyzer: AI code analyzer
    """

    def __init__(self):
        """
        Initialize the review engine.

        Automatically creates the required GitHubClient and CodexAnalyzer instances.
        """
        self.github = GitHubClient()
        self.analyzer = CodexAnalyzer()

    def review_pr(self, owner: str, repo: str, pr_number: int) -> Dict:
        """
        Review a PR and post the result.

        This is the main review method, executing the full review workflow:
        1. Get list of files modified in the PR
        2. Filter supported files
        3. Analyze each file
        4. Generate summary report
        5. Post review comment

        Args:
            owner: Repository owner username
            repo: Repository name
            pr_number: PR number

        Returns:
            Dict: Review result containing:
                - status: Status (success/skipped/error)
                - files_reviewed: Number of files reviewed
                - total_issues: Number of issues found
                - reason: If skipped or errored, explains the reason
                - error: If errored, contains the error message

        Example:
            result = engine.review_pr("facebook", "react", 12345)

            if result["status"] == "success":
                print(f"Review complete! Found {result['total_issues']} issues")
            elif result["status"] == "skipped":
                print(f"Skipped: {result['reason']}")
            else:
                print(f"Error: {result['error']}")
        """
        try:
            # Step 1: Get PR files
            print(f"Getting PR #{pr_number} files...")
            files = self.github.get_pr_files(owner, repo, pr_number)

            # Step 2: Filter supported files
            supported_files = self._filter_supported_files(files)

            # Skip if no supported files
            if not supported_files:
                return {
                    "status": "skipped",
                    "reason": "No supported files to review (unsupported format or file too large)"
                }

            print(f"Found {len(supported_files)} files to review")

            # Step 3: Analyze each file
            analyses = []
            for i, file_info in enumerate(supported_files, 1):
                print(f"Analyzing file {i}/{len(supported_files)}: {file_info['filename']}")
                analysis = self._analyze_file(owner, repo, file_info)
                analyses.append(analysis)

            # Step 4: Generate summary report
            print("Generating review report...")
            summary = self.analyzer.generate_summary(analyses)

            # Step 5: Submit review
            print("Submitting review comment...")
            self.github.submit_review(
                owner, repo, pr_number,
                body=summary,
                event="COMMENT"
            )

            # Calculate statistics
            total_issues = sum(len(a.get("issues", [])) for a in analyses)

            print(f"Review complete! Found {total_issues} issues")

            return {
                "status": "success",
                "files_reviewed": len(supported_files),
                "total_issues": total_issues
            }

        except Exception as e:
            # Error handling
            error_msg = str(e)
            print(f"Review failed: {error_msg}")

            return {
                "status": "error",
                "error": error_msg
            }

    def _filter_supported_files(self, files: List[Dict]) -> List[Dict]:
        """
        Filter files supported for review.

        Filter based on the following conditions:
        1. File extension is in the supported list
        2. File size does not exceed the limit
        3. Quantity does not exceed the limit

        Args:
            files: List of files returned by the GitHub API

        Returns:
            List[Dict]: List of files after filtering
        """
        supported = []

        for file in files:
            filename = file.get("filename", "").lower()

            # Check: is the file extension supported?
            is_supported = any(
                filename.endswith(f".{ext}")
                for ext in Config.SUPPORTED_LANGUAGES
            )

            if not is_supported:
                continue  # Skip unsupported files

            # Check: does the file size exceed the limit?
            file_size = file.get("changes", 0)
            if file_size > Config.MAX_FILE_SIZE:
                print(f"Skipping oversized file: {filename} ({file_size} bytes)")
                continue

            # Add to supported list
            supported.append(file)

            # Check: max file count
            if len(supported) >= Config.MAX_FILES_PER_REVIEW:
                print(f"Max file limit reached ({Config.MAX_FILES_PER_REVIEW})")
                break

        return supported

    def _analyze_file(self, owner: str, repo: str, file_info: Dict) -> Dict:
        """
        Analyze a single file.

        Fetch the file's patch (code diff) from GitHub, then call AI for analysis.

        Args:
            owner: Repository owner
            repo: Repository name
            file_info: File info dictionary (from GitHub API)

        Returns:
            Dict: Analysis result containing filename and various types of issues
        """
        filename = file_info["filename"]
        patch = file_info.get("patch", "")

        # Auto-detect programming language
        language = self._detect_language(filename)

        # Call AI to analyze code
        analysis = self.analyzer.analyze_code(
            code=patch,
            language=language,
            context=f"File: {filename}"
        )

        # Add filename to analysis result
        return {
            "filename": filename,
            **analysis
        }

    def _detect_language(self, filename: str) -> str:
        """
        Detect programming language based on filename.

        Uses a mapping from file extension to language name.

        Args:
            filename: Filename (including extension)

        Returns:
            str: Language name, returns "unknown" if not recognized

        Example:
            engine._detect_language("main.py")      # Returns: "python"
            engine._detect_language("app.js")       # Returns: "javascript"
            engine._detect_language("unknown.xyz")  # Returns: "unknown"
        """
        # Extension to language mapping
        extension_map = {
            # Python
            ".py": "python",
            ".pyw": "python",
            ".pyi": "python",

            # JavaScript/TypeScript
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",

            # Java
            ".java": "java",

            # Go
            ".go": "go",

            # Rust
            ".rs": "rust",

            # C/C++
            ".cpp": "cpp",
            ".cxx": "cpp",
            ".cc": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp"
        }

        # Convert to lowercase and look up
        filename_lower = filename.lower()
        for ext, lang in extension_map.items():
            if filename_lower.endswith(ext):
                return lang

        return "unknown"

    def handle_webhook(self, payload: Dict) -> Dict:
        """
        Handle a GitHub Webhook request.

        Parse the JSON data from the Webhook, extract PR information,
        and then call the review workflow.

        Supported Webhook events:
            - pull_request.opened: PR was created
            - pull_request.synchronize: PR was updated (pushed new commits)

        Args:
            payload: JSON data from GitHub Webhook

        Returns:
            Dict: Processing result

        Example:
            from flask import request

            @app.route('/webhook', methods=['POST'])
            def webhook():
                payload = request.get_json()
                result = engine.handle_webhook(payload)
                return jsonify(result)
        """
        # Check event type
        action = payload.get("action")
        if action not in ["opened", "synchronize"]:
            return {
                "status": "ignored",
                "reason": f"Ignoring '{action}' event, only handling opened and synchronize"
            }

        # Extract PR data
        pr_data = payload.get("pull_request", {})
        if not pr_data:
            return {
                "status": "error",
                "reason": "No PR info found in webhook data"
            }

        # Extract repository info
        repo_data = payload.get("repository", {})
        owner = repo_data.get("owner", {}).get("login")
        repo = repo_data.get("name")
        pr_number = pr_data.get("number")

        # Validate required info
        if not all([owner, repo, pr_number]):
            return {
                "status": "error",
                "reason": "Missing required repository or PR info"
            }

        print(f"Received PR event: {owner}/{repo}#{pr_number} ({action})")

        # Start review
        return self.review_pr(owner, repo, pr_number)
