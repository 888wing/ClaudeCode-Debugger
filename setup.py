from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="claudecode-debugger",
    version="1.5.0",
    author="888wing",
    author_email="",
    description="AI-powered debugging assistant with seamless Claude Code integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/888wing/ClaudeCode-Debugger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
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
        "jinja2>=3.0",
        "watchdog>=3.0",
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
        "claudecode_debugger": [
            "templates/*.yaml",
            "templates/advanced/*.yaml",
            "templates/bilingual/*.yaml",
            "i18n/*.json",
        ],
    },
)