# /ccdebug - Claude Code Debug Command Specification

## Overview

`/ccdebug` is a specialized slash command for Claude Code that integrates the ClaudeCode-Debugger for intelligent error analysis and debugging assistance.

## Command Syntax

```
/ccdebug [options] [error_content]
```

## Core Options

### Basic Usage
- `/ccdebug` - Analyze the last error from previous command
- `/ccdebug "error message"` - Analyze specific error text
- `/ccdebug --help` - Show command help

### Language Options
- `/ccdebug --zh` - Use Chinese (中文)
- `/ccdebug --en` - Use English (default)
- `/ccdebug --auto-lang` - Auto-detect based on error content

### Analysis Options
- `/ccdebug --quick` - Quick analysis (basic pattern matching)
- `/ccdebug --deep` - Deep analysis (stack trace + patterns + suggestions)
- `/ccdebug --full` - Full analysis with code context

### Input Sources
- `/ccdebug --last` - Analyze last command error
- `/ccdebug --clipboard` - Read from clipboard
- `/ccdebug --file <path>` - Read from file
- `/ccdebug --selection` - Analyze selected text

### Output Options
- `/ccdebug --copy` - Copy result to clipboard
- `/ccdebug --save <path>` - Save to file
- `/ccdebug --share` - Generate shareable link

### Context Options
- `/ccdebug --context <file>` - Include code context
- `/ccdebug --line <number>` - Specify error line
- `/ccdebug --project` - Include project structure

## Advanced Features

### Batch Processing
```
/ccdebug --batch --dir logs/     # Analyze all error logs
/ccdebug --watch file.log        # Monitor and analyze new errors
```

### Integration Modes
```
/ccdebug --git-hook              # Git commit hook mode
/ccdebug --ci-mode               # CI/CD integration mode
/ccdebug --test-mode             # Test failure analysis
```

### Filtering
```
/ccdebug --type python           # Only Python errors
/ccdebug --severity high         # High severity only
/ccdebug --recent 1h             # Errors from last hour
```

## Command Aliases

For convenience, these shortcuts are available:

- `/ccdb` - Short alias for `/ccdebug`
- `/cchelp` - Alias for `/ccdebug --help`
- `/cczh` - Alias for `/ccdebug --zh --deep`
- `/ccen` - Alias for `/ccdebug --en --deep`
- `/ccquick` - Alias for `/ccdebug --quick`
- `/ccfull` - Alias for `/ccdebug --full`

## Interactive Features

### Smart Detection
Claude Code automatically detects when to suggest `/ccdebug`:

1. **Auto-Suggest**: When error patterns detected
2. **Context Aware**: Understands current file type
3. **History**: Remembers user preferences
4. **Learning**: Improves suggestions over time

### Conversation Flow
```
User: npm test
Claude: [Test fails with TypeError]
       
       I noticed a test failure. Would you like me to analyze it?
       You can use: /ccdebug --last --zh

User: /ccdebug --last --zh
Claude: [Performs analysis and shows results]
```

## Examples

### Basic Examples
```bash
# Analyze last error in Chinese
/ccdebug --last --zh

# Quick analysis of specific error
/ccdebug --quick "TypeError: undefined is not a function"

# Full analysis with context
/ccdebug --full --context app.js --line 42
```

### Advanced Examples
```bash
# Analyze all test failures
/ccdebug --test-mode --batch

# Monitor log file
/ccdebug --watch server.log --zh

# CI integration
/ccdebug --ci-mode --save report.md
```

### Workflow Examples
```bash
# Development workflow
/ccdebug --last --deep --copy

# Debugging session
/ccdebug --full --project --zh

# Code review
/ccdebug --file pr-errors.log --save review.md
```

## Configuration

### User Preferences
Claude Code remembers your preferences:

```json
{
  "ccdebug": {
    "defaultLanguage": "zh",
    "defaultMode": "deep",
    "autoSuggest": true,
    "copyToClipboard": true,
    "contextLines": 10
  }
}
```

### Project Configuration
Create `.ccdebugrc` in project root:

```json
{
  "language": "zh",
  "severity": "medium",
  "exclude": ["node_modules", ".git"],
  "autoAnalyze": {
    "testFailures": true,
    "buildErrors": true,
    "runtimeErrors": true
  }
}
```

## Integration Points

### 1. Command Execution Hook
```python
# Claude Code automatically offers /ccdebug after errors
on_command_error = lambda err: suggest("/ccdebug --last")
```

### 2. File Watching
```python
# Auto-analyze when error files change
watch_patterns = ["*.log", "error-*.txt", "test-results.xml"]
```

### 3. Context Enhancement
```python
# Claude Code provides additional context
enhance_context = {
    "recent_commands": last_5_commands,
    "open_files": current_files,
    "project_type": detect_project_type()
}
```

## Best Practices

1. **Use Language Flag**: Always specify `--zh` or `--en` for consistent output
2. **Include Context**: Use `--context` for better analysis
3. **Save Important Analysis**: Use `--save` for future reference
4. **Batch Similar Errors**: Use `--batch` for multiple errors
5. **Set Preferences**: Configure defaults to save time

## Error Handling

### Common Issues
- **No Error Found**: `/ccdebug` will prompt for error input
- **Invalid Options**: Shows help with valid options
- **Timeout**: Large analysis may take time, use `--quick` for faster results
- **Language Detection Failed**: Defaults to English, use explicit flag

### Fallback Behavior
```
/ccdebug [invalid] → Shows help
/ccdebug (no error) → Prompts for input
/ccdebug --file (not found) → Checks clipboard
```

## Future Enhancements

- **AI Learning**: Improve suggestions based on resolution success
- **Team Sharing**: Share debugging sessions with team
- **Plugin System**: Custom analyzers for specific frameworks
- **Voice Input**: Describe errors verbally
- **Visual Mode**: Graphical error visualization

## Summary

`/ccdebug` seamlessly integrates advanced debugging capabilities into Claude Code, providing:

- 🎯 **Precise Analysis**: Intelligent error pattern recognition
- 🌍 **Multi-language**: Full Chinese and English support
- 🚀 **Quick Access**: Simple slash command interface
- 🧠 **Smart Suggestions**: Context-aware debugging advice
- 🔄 **Workflow Integration**: Fits naturally into development process

Making debugging in Claude Code smarter, faster, and more efficient!