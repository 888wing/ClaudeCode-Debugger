# ClaudeCode-Debugger 🚀

[![CI](https://github.com/888wing/ClaudeCode-Debugger/workflows/CI/badge.svg)](https://github.com/888wing/ClaudeCode-Debugger/actions)
[![Coverage](https://codecov.io/gh/888wing/ClaudeCode-Debugger/branch/main/graph/badge.svg)](https://codecov.io/gh/888wing/ClaudeCode-Debugger)
[![PyPI](https://img.shields.io/pypi/v/claudecode-debugger.svg)](https://pypi.org/project/claudecode-debugger/)
[![Python Version](https://img.shields.io/pypi/pyversions/claudecode-debugger.svg)](https://pypi.org/project/claudecode-debugger/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Intelligent debugging assistant for Claude Code - Transform error messages into actionable solutions with advanced AI-powered analysis, multi-language support, and seamless Claude Code integration.

## ✨ Features

- 🌍 **Multi-Language Support** - Full i18n with Chinese (中文) and English interface
- 🧠 **Advanced Error Analysis** - Three intelligent analyzers: Stack Trace, Pattern, and Code Context
- 🎯 **ML-Ready Suggestion Engine** - Confidence-scored solutions based on error patterns
- 🔍 **Deep Stack Trace Analysis** - Support for Python, JavaScript, TypeScript, Java, Ruby, Go
- 🤖 **Claude Code Integration** - Native `/ccdebug` slash command for seamless workflow
- 📋 **Smart Clipboard Integration** - Auto-detect and analyze errors from clipboard
- 🎨 **Beautiful Terminal UI** - Rich, colorful output with progress indicators
- 📊 **Intelligent Error Patterns** - Pre-configured patterns for common errors
- 🔧 **Extensible Architecture** - Plugin system for custom analyzers and patterns
- 📈 **Learning System** - Improves suggestions based on successful resolutions

## 🚀 Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/888wing/ClaudeCode-Debugger.git
cd ClaudeCode-Debugger
pip install -e .

# Install Claude Code integration
./install_claude_integration.sh
source ~/.zshrc  # or ~/.bashrc
```

### Basic Usage

```bash
# Analyze error with Chinese interface
ccdebug "TypeError: Cannot read property 'name' of undefined" --lang zh

# Deep analysis with suggestions
ccdebug "AttributeError: 'NoneType' object" --analyze-stack --suggest

# Read from clipboard
ccdebug -c --lang zh

# Interactive mode
ccdebug -i

# Claude Code integration
# In Claude Code, when you encounter an error:
/ccdebug --last --zh --deep
```

### Language Support

```bash
# Chinese interface (中文界面)
cczh "錯誤信息"  # Quick Chinese analysis
ccfull           # Full analysis in Chinese

# English interface
ccen "error message"  # Quick English analysis
ccdebug --lang en    # Explicit English
```

## 📖 Examples

### Python AttributeError (Chinese)

```bash
$ ccdebug "AttributeError: 'NoneType' object has no attribute 'profile'" --lang zh --suggest

🚨 Python 錯誤 - HIGH 優先級
檢測到: AttributeError - NoneType 錯誤

📊 堆疊追蹤分析:
- 根本原因: 嘗試訪問 None 對象的屬性
- 影響範圍: 1 個文件受影響

🎯 智能建議 (信心度: 85%):
1. 添加 None 檢查:
   ```python
   if user and hasattr(user, 'profile'):
       return user.profile.avatar_url
   return None
   ```

2. 使用 getattr 安全訪問:
   ```python
   profile = getattr(user, 'profile', None)
   if profile:
       return profile.avatar_url
   ```

3. 使用 try-except 處理:
   ```python
   try:
       return user.profile.avatar_url
   except AttributeError:
       return None
   ```

✅ 已複製到剪貼板
```

### JavaScript TypeError with Code Context

```bash
$ ccdebug --last --lang en --analyze-stack --suggest

🚨 JavaScript Error - HIGH Priority
TypeError: Cannot read property 'map' of undefined

🔍 Stack Trace Analysis:
┌─────────────────────────────────────────┐
│ at TodoList (TodoList.jsx:15:19)       │
│ at renderWithHooks (react-dom.js:14985)│
│ at mountComponent (react-dom.js:17441) │
└─────────────────────────────────────────┘

📊 Pattern Analysis:
- Error Pattern: undefined_property_access
- Common in: React component props
- Severity: HIGH

🎯 Suggestions (Confidence: 92%):
1. Add default props:
   ```javascript
   function TodoList({ todos = [] }) {
     return <ul>{todos.map(todo => <li>{todo.text}</li>)}</ul>
   }
   ```

2. Add conditional rendering:
   ```javascript
   function TodoList({ todos }) {
     if (!todos || !Array.isArray(todos)) {
       return <div>No todos available</div>
     }
     return <ul>{todos.map(todo => <li>{todo.text}</li>)}</ul>
   }
   ```

3. Use optional chaining:
   ```javascript
   return <ul>{todos?.map(todo => <li>{todo.text}</li>) || null}</ul>
   ```

[✓ Analysis complete]
```

### Claude Code Integration

```bash
# In Claude Code, when you encounter an error:
User: python manage.py runserver
Claude: [Shows Django error]

User: /ccdebug --last --zh --deep
Claude: 
🚨 Django 錯誤分析
檢測到: ImproperlyConfigured

🔍 深度分析:
- 錯誤位置: settings.py:89
- 根本原因: DATABASES 配置缺失
- 影響: 應用程序無法啟動

🎯 解決方案:
1. 檢查 settings.py 中的 DATABASES 配置
2. 確保環境變數正確設置
3. 驗證數據庫連接參數

[詳細步驟和代碼示例...]
```

## 🛠️ Advanced Features

### Intelligent Analyzers

CCDebugger includes three advanced analyzers:

```python
# Stack Trace Analyzer - Multi-language support
from claudecode_debugger.analyzers import StackTraceAnalyzer

analyzer = StackTraceAnalyzer()
result = analyzer.analyze(error_text)
# Returns: language, frames, root_cause, error_type

# Pattern Analyzer - Detects common error patterns
from claudecode_debugger.analyzers import PatternAnalyzer

analyzer = PatternAnalyzer()
patterns = analyzer.analyze(error_text)
# Returns: matched patterns with solutions

# Code Context Analyzer - Extracts code context
from claudecode_debugger.analyzers import CodeContextAnalyzer

analyzer = CodeContextAnalyzer()
context = analyzer.extract_context("app.py", line_number=42)
# Returns: code snippet with surrounding lines
```

### ML-Ready Suggestion Engine

```python
from claudecode_debugger.suggestions import SuggestionEngine

engine = SuggestionEngine()
suggestions = engine.generate_suggestions(
    error_type="AttributeError",
    error_patterns=["null_reference"],
    stack_trace_info=stack_info
)
# Returns: Ranked suggestions with confidence scores
```

### Configuration

Create `~/.ccdebugrc` for personal preferences:

```json
{
  "defaultLanguage": "zh",
  "defaultMode": "deep",
  "autoSuggest": true,
  "copyToClipboard": true,
  "contextLines": 10,
  "favoriteFrameworks": ["django", "react", "vue"],
  "customPatterns": {
    "myapp": {
      "errorPattern": "MyAppError:",
      "suggestion": "Check MyApp configuration"
    }
  }
}
```

### Claude Code Integration

The `/ccdebug` command seamlessly integrates with Claude Code:

```bash
# Auto-detection and analysis
/ccdebug --last --zh

# Different analysis modes
/ccdebug --quick   # Fast analysis
/ccdebug --deep    # Detailed analysis with suggestions
/ccdebug --full    # Complete analysis with code context

# Batch processing
/ccdebug --batch --dir logs/

# Watch mode
/ccdebug --watch server.log
```

### Custom Error Patterns

Add your own error patterns:

```python
from claudecode_debugger.analyzers.pattern import ErrorPattern

custom_pattern = ErrorPattern(
    name="custom_api_error",
    pattern=r"API Error: (\d+)",
    description="Custom API error",
    category="api",
    severity="high",
    common_causes=["Invalid API key", "Rate limit exceeded"],
    solutions=["Check API credentials", "Implement retry logic"]
)
```

## 🏗️ Architecture

CCDebugger is built with a modular, extensible architecture:

```
claudecode_debugger/
├── analyzers/           # Intelligent error analyzers
│   ├── stack_trace.py   # Multi-language stack trace analysis
│   ├── pattern.py       # Error pattern detection
│   └── code_context.py  # Code context extraction
├── suggestions/         # ML-ready suggestion engine
│   └── engine.py        # Confidence-scored solutions
├── i18n/               # Internationalization
│   ├── translator.py    # Translation engine
│   └── messages/        # Language files (en, zh)
├── formatters/         # Output formatters
│   ├── console.py      # Rich terminal output
│   └── markdown.py     # Markdown formatting
└── cli_new.py          # Enhanced CLI with full features
```

### Key Components

1. **I18n System**: Full internationalization with automatic language detection
2. **Analyzer Framework**: Pluggable analyzers for different error types
3. **Suggestion Engine**: Knowledge base with confidence scoring
4. **Claude Code Integration**: Native slash command support
5. **Rich UI**: Beautiful terminal output with progress indicators

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/888wing/ClaudeCode-Debugger.git
cd ClaudeCode-Debugger

# Install in development mode
make dev

# Run tests
make test

# Format code
make format
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the Claude Code community
- Inspired by the need for better debugging workflows
- Special thanks to all contributors

## 📬 Support

- 📖 [Claude Code Integration Guide](CLAUDE_CODE_GUIDE.md)
- 🎯 [/ccdebug Command Reference](CLAUDE_CCDEBUG_COMMAND.md)
- 📚 [Real-World Examples](CLAUDE_CCDEBUG_EXAMPLES.md)
- 🐛 [Issue Tracker](https://github.com/888wing/ClaudeCode-Debugger/issues)
- 💬 [Discussions](https://github.com/888wing/ClaudeCode-Debugger/discussions)
- 🔔 [Changelog](CHANGELOG.md)

## 🌟 What's New

### v2.0.0 - Major Update
- 🌍 Full internationalization (i18n) with Chinese and English support
- 🧠 Three new intelligent analyzers for deep error analysis
- 🎯 ML-ready suggestion engine with confidence scoring
- 🤖 Native Claude Code integration with `/ccdebug` command
- 📊 Advanced error pattern detection
- 🔍 Multi-language stack trace analysis (Python, JS, TS, Java, Ruby, Go)
- ✨ Complete architectural overhaul for extensibility