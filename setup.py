from setuptools import setup, find_packages

setup(
    name="pr-codex-reviewer",
    version="1.0.0",
    description="AI-powered PR review bot using OpenAI Codex",
    author="changsheng0804-blip",
    author_email="your.email@example.com",
    url="https://github.com/changsheng0804-blip/pr-codex-reviewer",
    packages=find_packages(),
    install_requires=[
        "flask>=2.3.0",
        "requests>=2.31.0",
        "openai>=0.27.0",
        "gunicorn>=21.2.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
)
