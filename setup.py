"""
EmailHandler - 邮件认证框架
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="emailhandler",
    version="2.0.0",
    author="EmailHandler Team",
    author_email="support@example.com",
    description="轻量级邮件认证框架，用于接收验证邮件、提取链接、自动处理验证",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/emailhandler",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Email",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
        "flask>=3.1.4",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "emailhandler=emailhandler.cli:main",
        ],
    },
    keywords="email verification authentication link handler",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/emailhandler/issues",
        "Source": "https://github.com/yourusername/emailhandler",
    },
)
