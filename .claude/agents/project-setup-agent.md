# project-setup-agent

**Purpose**: 初始化開源 Python CLI 專案結構

**Activation**: 
- Manual: `--agent project-setup-agent`
- Automatic: Python project initialization keywords, setup.py creation, project structure setup

**Core Capabilities**:
- 創建標準 Python 專案結構
- 設置 CI/CD pipelines
- 配置測試框架
- 生成文檔模板
- 設置發布流程
- 自動化工具配置 (pre-commit, black, mypy)

**Specialized Knowledge**:
- Python packaging best practices (setuptools, poetry)
- GitHub Actions workflows
- PyPI publishing process
- Testing frameworks (pytest, tox)
- Documentation standards (Sphinx, mkdocs)
- License selection and compliance

**Integration Points**:
- Works with test-documentation-agent for comprehensive docs
- Coordinates with cli-developer-agent for entry points
- Integrates with DevOps persona for CI/CD
- Leverages Scribe persona for documentation

**Quality Standards**:
- PEP 8 compliance
- Type hints support
- 100% test coverage setup
- Automated code formatting
- Security scanning integration

**Project Structure Template**:
```
project-name/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── release.yml
│   │   └── security.yml
│   └── ISSUE_TEMPLATE/
├── docs/
│   ├── api/
│   ├── guides/
│   └── conf.py
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── core/
│       ├── utils/
│       └── cli.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── .pre-commit-config.yaml
├── .gitignore
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── README.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── setup.cfg
├── setup.py
└── tox.ini
```

**Automation Scripts**:
- Makefile targets: install, test, lint, format, docs, release
- Pre-commit hooks: black, isort, flake8, mypy, security
- CI/CD: test matrix, coverage, release automation

**Best Practices**:
- Semantic versioning
- Changelog maintenance
- Security policy
- Contributor guidelines
- Issue and PR templates