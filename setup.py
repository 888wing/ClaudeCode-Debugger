from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="claudecode-debugger",
    version="0.1.0",
    author="888wing",
    author_email="",
    description="Smart debug prompt generator for Claude Code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/888wing/ClaudeCode-Debugger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
        "pyperclip>=1.8",
        "pyyaml>=6.0",
        "rich>=13.0",
        "markdown>=3.0",
        "pygments>=2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "watch": [
            "watchdog>=3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ccdebug=claudecode_debugger.cli_new:cli",
            "ccdebug-basic=claudecode_debugger.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "claudecode_debugger": ["templates/*.yaml"],
    },
)