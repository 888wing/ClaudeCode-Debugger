# ClaudeCode-Debugger Enhanced CLI Guide

## Overview

The enhanced CLI for ClaudeCode-Debugger provides advanced features for error analysis, batch processing, and intelligent debugging prompt generation. Built with Click and Rich, it offers a powerful and beautiful command-line experience.

## Installation

```bash
pip install -e .
```

After installation, you'll have access to two commands:
- `ccdebug` - Original CLI (maintained for compatibility)
- `ccdebug-enhanced` - Enhanced CLI with all new features

## Features

### 1. Advanced File Input

#### Multiple Files
```bash
# Analyze multiple specific files
ccdebug-enhanced -f error1.log -f error2.log -f error3.log

# Use wildcards
ccdebug-enhanced -f "logs/*.log"
ccdebug-enhanced -f "**/*.error"
```

#### Batch Processing
```bash
# Process all matching files and generate a report
ccdebug-enhanced -f "logs/*.log" --batch -o report.json --format json

# Batch process with specific error type
ccdebug-enhanced -f "typescript/*.ts.log" --batch -t typescript -o ts_report.md --format markdown
```

### 2. Error Type Detection

#### Auto-completion
The CLI provides auto-completion for error types:
```bash
ccdebug-enhanced -t typ<TAB>  # Completes to "typescript"
```

#### Supported Types
- `typescript` - TypeScript compilation errors
- `javascript` - JavaScript runtime errors
- `python` - Python exceptions and tracebacks
- `rust` - Rust compiler errors
- `go` - Go compilation and runtime errors
- `java` - Java exceptions
- `memory` - Memory-related errors
- `network` - Network and API errors
- `permission` - Permission and access errors
- `syntax` - Syntax errors across languages
- `runtime` - General runtime errors
- `build` - Build system errors
- `test` - Test framework errors
- `deployment` - Deployment and CI/CD errors
- `database` - Database query errors
- `api` - API and HTTP errors

### 3. Enhanced Clipboard Support

#### Format Options
```bash
# Copy as plain text
ccdebug-enhanced "error message" -c plain

# Copy as Markdown (default)
ccdebug-enhanced "error message" -c markdown

# Copy as code block with syntax highlighting
ccdebug-enhanced "error message" -c code

# Copy as JSON with metadata
ccdebug-enhanced "error message" -c json
```

### 4. Multiple Output Formats

```bash
# Save as Markdown
ccdebug-enhanced -f error.log -o debug_prompt.md --format markdown

# Save as JSON
ccdebug-enhanced -f error.log -o debug_data.json --format json

# Save as HTML with syntax highlighting
ccdebug-enhanced -f error.log -o report.html --format html

# Save as YAML
ccdebug-enhanced -f error.log -o debug.yaml --format yaml
```

### 5. Interactive Mode

```bash
ccdebug-enhanced --interactive
# or
ccdebug-enhanced -i
```

Features:
- Multi-line error input with Ctrl+D to analyze
- Real-time analysis with progress indicators
- Post-analysis options:
  - Copy to clipboard with format selection
  - Save to file with format selection
  - Re-analyze with different settings
  - Analyze new error

Commands in interactive mode:
- `help` - Show help
- `clear` - Clear screen
- `exit` - Exit interactive mode

### 6. History Management

#### View History
```bash
# Show last 10 entries (default)
ccdebug-enhanced history show

# Show last 20 entries
ccdebug-enhanced history show --limit 20

# Filter by error type
ccdebug-enhanced history show --filter typescript
```

#### Clear History
```bash
ccdebug-enhanced history clear
```

### 7. Configuration Management

#### View Configuration
```bash
# Show all settings
ccdebug-enhanced config show

# Get specific value
ccdebug-enhanced config get general.theme
```

#### Set Configuration
```bash
# Set theme
ccdebug-enhanced config set general.theme dark

# Enable auto-copy
ccdebug-enhanced config set general.auto_copy true

# Set default format
ccdebug-enhanced config set general.default_format json
```

#### Configuration File
Create `~/.ccdebug/config.ini`:
```ini
[general]
theme = dark
verbose = false
auto_copy = true
default_format = markdown

[output]
max_width = 120
syntax_theme = monokai

[clipboard]
default_format = markdown
include_timestamp = true

[plugins]
auto_enable = ["stack_trace_analyzer"]
```

### 8. Plugin System

#### List Plugins
```bash
ccdebug-enhanced plugin list
```

#### Enable/Disable Plugins
```bash
# Enable a plugin
ccdebug-enhanced plugin enable stack_trace_analyzer

# Disable a plugin
ccdebug-enhanced plugin disable security_analyzer
```

#### Available Plugins
- `stack_trace_analyzer` - Deep analysis of stack traces
- `dependency_analyzer` - Identify problematic dependencies
- `performance_analyzer` - Performance-related insights
- `security_analyzer` - Security vulnerability detection
- `pattern_matcher` - Common error pattern matching
- `ai_suggestions` - AI-powered fix suggestions

### 9. Visual Enhancements

#### Beautiful Output
- Syntax highlighting for code snippets
- Color-coded severity levels
- Progress bars and spinners
- Formatted tables and trees
- Rich panels and layouts

#### Themes
```bash
# Use dark theme
ccdebug-enhanced --theme dark "error message"

# Use light theme
ccdebug-enhanced --theme light "error message"

# Use custom theme (defined in config)
ccdebug-enhanced --theme custom "error message"
```

### 10. Advanced Features

#### Watch Mode
```bash
# Monitor files for changes
ccdebug-enhanced --watch -f "logs/*.log"
```

#### Statistics
```bash
# Show usage statistics
ccdebug-enhanced --stats
```

#### Custom Agent Override
```bash
# Use specific AI agent
ccdebug-enhanced "error" --agent specialized-debugger
```

#### Verbose Mode
```bash
# Show detailed analysis
ccdebug-enhanced "error" -v
# or
ccdebug-enhanced "error" --verbose
```

## Examples

### Example 1: TypeScript Error Analysis
```bash
ccdebug-enhanced -f src/errors.log -t typescript -c markdown -v
```

### Example 2: Batch Process Python Errors
```bash
ccdebug-enhanced -f "tests/**/*.error" --batch -t python -o test_report.html --format html
```

### Example 3: Interactive Debugging Session
```bash
ccdebug-enhanced -i --theme dark
```

### Example 4: Quick Copy from Clipboard
```bash
# Copy error from clipboard, analyze, and copy result back
ccdebug-enhanced -c markdown
```

### Example 5: Historical Analysis
```bash
# Review past errors
ccdebug-enhanced history show --limit 50 --filter critical
```

## Tips and Tricks

1. **Shell Aliases**: Create aliases for common operations
   ```bash
   alias ccd="ccdebug-enhanced"
   alias ccd-ts="ccdebug-enhanced -t typescript"
   alias ccd-py="ccdebug-enhanced -t python"
   ```

2. **Default Configuration**: Set your preferences in `~/.ccdebug/config.ini`

3. **Plugin Development**: Create custom plugins in `~/.ccdebug/plugins/`

4. **Batch Reports**: Use JSON output format for programmatic processing

5. **CI/CD Integration**: Use the CLI in CI pipelines for automatic error analysis

## Troubleshooting

### Issue: Clipboard not working
- **Solution**: Install `pbcopy` (macOS), `xclip` (Linux), or ensure Windows clipboard access

### Issue: Encoding errors
- **Solution**: Ensure files are UTF-8 encoded or specify encoding in config

### Issue: Plugin not loading
- **Solution**: Check plugin requirements and Python path

### Issue: Performance with large files
- **Solution**: Adjust `max_file_size` in configuration

## Contributing

To add new features or plugins:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## Support

For issues, questions, or suggestions:
- GitHub Issues: https://github.com/888wing/ClaudeCode-Debugger
- Documentation: https://claudecode-debugger.readthedocs.io