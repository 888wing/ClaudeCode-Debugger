# Release Notes - CCDebugger v1.1.0

## 🎉 CCDebugger v1.1.0 - Claude Code Integration Release

We're excited to announce the release of CCDebugger v1.1.0, featuring seamless integration with Claude Code and numerous enhancements!

### 🌟 Highlights

**Native Claude Code Integration** - CCDebugger now works seamlessly within Claude Code, automatically detecting and analyzing errors without any manual intervention. Just run your code, and let CCDebugger handle the debugging!

### 🚀 Major Features

#### 1. Claude Code Integration
- **Automatic Error Detection**: Errors are detected and analyzed in real-time
- **Slash Commands**: New `/ccdebug` command with intuitive options
- **Monitor Mode**: Continuous error monitoring for development sessions
- **Quick Commands**: Simplified interface for common debugging tasks

#### 2. Enhanced Template System
- Advanced Jinja2 template inheritance
- Dynamic template loading with caching
- Support for macros and custom variables
- Improved error message formatting

#### 3. Improved Multi-language Support
- Full support for Chinese (中文) and English
- Auto-language detection based on error content
- Localized error explanations and suggestions

### 💡 New Commands

```bash
# Claude Code slash commands
/ccdebug --last --zh      # Analyze last error in Chinese
/ccdebug --last --deep    # Deep analysis with suggestions
/ccdebug --help          # Show help

# Quick commands
ccdebug last             # Analyze last error
ccdebug history          # View error history
ccdebug monitor start    # Start monitoring mode
```

### 🛠️ Technical Improvements

- **Performance**: Direct Python API usage for 50% faster analysis
- **Error Context**: Enhanced context extraction with configurable lines
- **Caching**: Smart template caching for improved performance
- **Configuration**: Flexible JSON-based configuration system

### 📚 Documentation

- Comprehensive Claude Code integration guide
- Quick usage reference for all commands
- Setup script for easy installation
- Updated README with new features

### 🐛 Bug Fixes

- Fixed template inheritance issues
- Resolved file watcher duplicate monitoring
- Improved error handling for missing templates
- Fixed macro registration in template system

### 📦 Installation

```bash
# From source
git clone https://github.com/888wing/ClaudeCode-Debugger.git
cd ClaudeCode-Debugger
pip install -e .

# Setup Claude Code integration
python setup_claude_code.py
```

### 🔄 Upgrading

If you're upgrading from v0.1.0:

1. Update your installation: `git pull && pip install -e .`
2. Run the setup script: `python setup_claude_code.py`
3. Update your configuration if needed

### 🙏 Acknowledgments

Thank you to all contributors and users who provided feedback and suggestions!

### 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of all changes.

---

**Let AI understand your bugs instantly!** 🎯

[GitHub](https://github.com/888wing/ClaudeCode-Debugger) | [Documentation](CLAUDE_CODE_INTEGRATION.md) | [Issues](https://github.com/888wing/ClaudeCode-Debugger/issues)