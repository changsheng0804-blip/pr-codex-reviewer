"""
Main application entry point for PR Codex Reviewer
"""
import os
import sys
from flask import Flask, request, jsonify
from .review_engine import ReviewEngine
from .config import Config

app = Flask(__name__)
engine = ReviewEngine()


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "pr-codex-reviewer",
        "version": "1.0.0"
    })


@app.route("/webhook", methods=["POST"])
def webhook():
    """GitHub webhook endpoint"""
    try:
        payload = request.get_json()
        
        if not payload:
            return jsonify({"status": "error", "reason": "No payload"}), 400
        
        # Handle the webhook
        result = engine.handle_webhook(payload)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500


@app.route("/review/<owner>/<repo>/<int:pr_number>", methods=["POST"])
def manual_review(owner: str, repo: str, pr_number: int):
    """Manual review endpoint"""
    try:
        result = engine.review_pr(owner, repo, pr_number)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 500


def main():
    """Main entry point"""
    try:
        Config.validate()
        app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
