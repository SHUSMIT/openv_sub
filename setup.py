"""Setup configuration for openenv-email-triage"""

from setuptools import setup, find_packages

setup(
    name="openenv-email-triage",
    version="1.0.0",
    description="Real-world email triage environment for training AI agents",
    author="OpenEnv Community",
    author_email="openenv@huggingface.co",
    url="https://github.com/SHUSMIT/openv_sub",
    python_requires=">=3.11",
    py_modules=[
        "environment",
        "models",
        "definitions",
        "expanded_emails",
        "task_graders",
        "dynamic_grader",
        "server",
        "inference",
    ],
    install_requires=[
        "pydantic==2.5.0",
        "pydantic-core==2.14.1",
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "starlette==0.27.0",
        "openai==1.3.0",
        "anthropic==0.7.0",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "typing-extensions==4.8.0",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1",
            "httpx==0.25.1",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
