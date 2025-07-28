# Changelog

All notable changes to ClaudeCode-Debugger will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-01-28

### 🚀 Major Features

#### Claude Code Integration
- **Seamless Integration**: CCDebugger now works natively within Claude Code
- **Auto-Detection**: Automatically detects and analyzes errors without manual intervention
- **Slash Commands**: New `/ccdebug` command with intuitive options
- **Real-time Monitoring**: Monitor mode for continuous error detection

### ✨ New Features

- **Enhanced Template System**: Advanced template inheritance with Jinja2
- **Multi-language Support**: Full support for Chinese (中文) and English interfaces
- **Smart Error Detection**: Improved error pattern recognition for multiple languages
- **History Management**: Automatic error history tracking with JSON storage
- **Configuration System**: Flexible configuration via `~/.claude/ccdebug.json`
- **Quick Commands**: Simplified command interface for common operations

### 🛠️ Improvements

- **Performance**: Direct Python API usage for faster analysis
- **Error Context**: Enhanced error context extraction with configurable context lines
- **Template Loading**: Improved template loading system with caching
- **Suggestions Engine**: AI-powered suggestions with confidence scores
- **Documentation**: Comprehensive Claude Code integration guide

### 🐛 Bug Fixes

- Fixed template inheritance issues (`base_base` not found error)
- Resolved file watcher duplicate monitoring problems
- Fixed macro and variable registration in template system
- Improved error handling for missing templates

### 📚 Documentation

- Added `CLAUDE_CODE_INTEGRATION.md` - Complete integration guide
- Added `CLAUDE_CODE_USAGE.md` - Quick usage reference
- Updated README with Claude Code integration section
- Added setup script for easy installation

### 🔧 Technical Changes

- Upgraded to Beta status (Development Status :: 4)
- Added Jinja2 and watchdog to core dependencies
- Implemented DictLoader for dynamic template registration
- Enhanced template system with macro support
- Improved error pattern matching algorithms

## [0.1.0] - 2024-01-20

### Initial Release

- Basic error detection and analysis
- Template-based prompt generation
- Multi-language support (Chinese/English)
- Clipboard integration
- Rich terminal UI
- Basic CLI interface

---

[1.1.0]: https://github.com/888wing/ClaudeCode-Debugger/compare/v0.1.0...v1.1.0
[0.1.0]: https://github.com/888wing/ClaudeCode-Debugger/releases/tag/v0.1.0