# ClaudeCode-Debugger

[![CI](https://github.com/888wing/ClaudeCode-Debugger/workflows/CI/badge.svg)](https://github.com/888wing/ClaudeCode-Debugger/actions)
[![Coverage](https://codecov.io/gh/888wing/ClaudeCode-Debugger/branch/main/graph/badge.svg)](https://codecov.io/gh/888wing/ClaudeCode-Debugger)
[![PyPI](https://img.shields.io/pypi/v/claudecode-debugger.svg)](https://pypi.org/project/claudecode-debugger/)
[![Python Version](https://img.shields.io/pypi/pyversions/claudecode-debugger.svg)](https://pypi.org/project/claudecode-debugger/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Smart debug prompt generator for Claude Code - Transform error messages into actionable debug prompts with AI-powered analysis.

## ✨ Features

- 🔍 **Automatic Error Detection** - Intelligently identifies error types across multiple programming languages
- 🤖 **Smart Agent Selection** - Automatically selects the optimal Claude Code agent for each error type
- 📋 **One-Click Copy** - Instantly copy generated prompts to clipboard for quick debugging
- 🎨 **Beautiful Output** - Rich, colorful terminal output for better readability
- 📊 **Error Analysis** - Provides severity assessment and estimated fix time
- 🔧 **Extensible Templates** - Customize prompts with YAML templates for your specific needs
- 📈 **Learning System** - Improves suggestions based on historical solutions

## 🚀 Quick Start

### Installation

```bash
pip install claudecode-debugger
```

### Basic Usage

```bash
# Analyze error from command line
ccdebug "TypeError: Cannot read property 'name' of undefined"

# Read error from file
ccdebug -f error.log

# Copy to clipboard automatically
ccdebug -c

# Interactive mode
ccdebug -i
```

## 📖 Examples

### TypeScript Error

```bash
$ ccdebug "TS2322: Type 'string' is not assignable to type 'number'"

🚨 TypeScript Compilation Error - HIGH Priority Debug

## Error Summary
Detected 1 error(s) affecting:
- Unknown file

## TypeScript Compilation Analysis

### Error Codes Detected:
- TS2322: Type mismatch error

### Debug Tasks
1. **Type Safety Analysis**
   - Review type definitions
   - Check for implicit any usage
   - Validate interface implementations

2. **Fix Strategy**
   - Update variable type annotation
   - Convert value to expected type
   - Add type guards if needed

[✓ Copied to clipboard!]
```

### Python Exception

```bash
$ ccdebug -f traceback.log

🚨 Python Exception - CRITICAL Priority Debug

## Error Summary
Detected Python exception in:
- app.py (line 42)

## Exception Details
ImportError: No module named 'requests'

## Debug Tasks
1. **Dependency Check**
   - Verify package installation
   - Check virtual environment
   
2. **Fix Strategy**
   - pip install requests
   - Update requirements.txt

[✓ Saved to debug-prompt.md]
```

## 🛠️ Advanced Features

### Custom Templates

Create your own debug templates in `~/.ccdebug/templates/`:

```yaml
# custom_error.yaml
name: Custom Error Template
agent: debug-specialist
template: |
  ## Custom Error Analysis
  Error: {error_type}
  Files: {affected_files}
  
  ## Your Custom Sections
  {custom_analysis}
```

### Configuration

Configure defaults in `~/.ccdebugrc.yaml`:

```yaml
preferences:
  auto_copy: true
  output_format: markdown
  default_agent: debug-specialist
  
agents:
  typescript: debug-specialist
  python: backend-system-architect
  memory: performance-specialist
```

### Plugin System

Extend functionality with plugins:

```python
from claudecode_debugger.plugins import Plugin

class GitContextPlugin(Plugin):
    def enhance_prompt(self, prompt_data):
        # Add git context to prompts
        prompt_data['git_info'] = self.get_git_context()
        return prompt_data
```

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

- 📖 [Documentation](https://claudecode-debugger.readthedocs.io)
- 🐛 [Issue Tracker](https://github.com/888wing/ClaudeCode-Debugger/issues)
- 💬 [Discussions](https://github.com/888wing/ClaudeCode-Debugger/discussions)
- 🔔 [Changelog](CHANGELOG.md)