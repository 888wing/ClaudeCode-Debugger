#!/bin/bash
# Claude Code Integration Setup Script for CCDebugger
# 自動設置 /ccdebug 指令整合

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Header
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║     CCDebugger Claude Code Integration Setup         ║"
echo "║              /ccdebug Command Installation           ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running from correct directory
if [ ! -f "setup.py" ] || [ ! -d "claudecode_debugger" ]; then
    print_error "Please run this script from the ClaudeCode_Debugger directory"
    exit 1
fi

# Step 1: Install CCDebugger
print_info "Step 1: Installing CCDebugger..."
if pip3 install -e . > /dev/null 2>&1; then
    print_success "CCDebugger installed successfully"
else
    print_error "Failed to install CCDebugger"
    exit 1
fi

# Step 2: Detect shell
print_info "Step 2: Detecting shell configuration..."
SHELL_RC=""
SHELL_NAME=""

if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
    SHELL_NAME="zsh"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
    SHELL_NAME="bash"
else
    print_warning "Unknown shell. Please manually add aliases to your shell configuration."
    SHELL_RC="$HOME/.bashrc"
    SHELL_NAME="bash"
fi

print_success "Detected $SHELL_NAME shell, using $SHELL_RC"

# Step 3: Create ccdebug wrapper script
print_info "Step 3: Creating ccdebug wrapper script..."

WRAPPER_SCRIPT="$HOME/.local/bin/ccdebug-wrapper"
mkdir -p "$HOME/.local/bin"

cat > "$WRAPPER_SCRIPT" << 'EOF'
#!/usr/bin/env python3
"""CCDebug wrapper for Claude Code integration"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claude_code_ccdebug import CCDebugCommand

if __name__ == "__main__":
    command = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    ccdebug = CCDebugCommand()
    
    # For testing, you can set last_error here
    result = ccdebug.execute(command)
    print(result)
EOF

chmod +x "$WRAPPER_SCRIPT"
print_success "Wrapper script created"

# Step 4: Copy integration module
print_info "Step 4: Installing integration module..."
cp claude_code_ccdebug.py "$HOME/.local/bin/"
print_success "Integration module installed"

# Step 5: Add aliases to shell configuration
print_info "Step 5: Adding aliases to $SHELL_RC..."

# Check if aliases already exist
if grep -q "CCDebugger Aliases" "$SHELL_RC" 2>/dev/null; then
    print_warning "CCDebugger aliases already exist in $SHELL_RC"
else
    cat >> "$SHELL_RC" << 'EOF'

# CCDebugger Aliases for Claude Code
alias ccdebug="python3 -m claudecode_debugger.cli_new"
alias ccdb="ccdebug"
alias ccdebug-wrapper="$HOME/.local/bin/ccdebug-wrapper"

# Quick access aliases
alias cczh="ccdebug --lang zh --suggest"
alias ccen="ccdebug --lang en --suggest"
alias ccquick="ccdebug --lang zh"
alias ccfull="ccdebug --lang zh --analyze-stack --suggest --verbose"
alias cchelp="ccdebug --help"

# Function for auto-debugging
ccdebug_auto() {
    # Run command and capture output
    output=$("$@" 2>&1)
    exit_code=$?
    
    # Display output
    echo "$output"
    
    # If command failed, auto-analyze
    if [ $exit_code -ne 0 ]; then
        echo -e "\n🔍 Auto-analyzing error with CCDebugger..."
        echo "$output" | ccdebug --lang zh --suggest
    fi
    
    return $exit_code
}

# Watch log files for errors
ccdebug_watch() {
    if [ -z "$1" ]; then
        echo "Usage: ccdebug_watch <logfile>"
        return 1
    fi
    
    tail -f "$1" | while read line; do
        if echo "$line" | grep -E "(Error|Exception|Failed|錯誤|異常|失敗)" > /dev/null; then
            echo -e "\n🚨 Error detected, analyzing..."
            echo "$line" | ccdebug --lang zh --suggest
        fi
    done
}

# Export for use in scripts
export -f ccdebug_auto
export -f ccdebug_watch
EOF
    print_success "Aliases added to $SHELL_RC"
fi

# Step 6: Create default configuration
print_info "Step 6: Creating default configuration..."

CONFIG_FILE="$HOME/.ccdebugrc"
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << 'EOF'
{
  "defaultLanguage": "zh",
  "defaultMode": "deep",
  "autoSuggest": true,
  "copyToClipboard": true,
  "contextLines": 10,
  "excludePatterns": ["node_modules", ".git", "__pycache__", "*.pyc"],
  "autoAnalyze": {
    "testFailures": true,
    "buildErrors": true,
    "runtimeErrors": true
  }
}
EOF
    print_success "Configuration file created at $CONFIG_FILE"
else
    print_warning "Configuration file already exists at $CONFIG_FILE"
fi

# Step 7: Create VS Code integration (optional)
if command -v code &> /dev/null; then
    print_info "Step 7: VS Code detected, creating tasks..."
    
    VSCODE_DIR=".vscode"
    if [ -d "$VSCODE_DIR" ]; then
        TASKS_FILE="$VSCODE_DIR/tasks.json"
        
        if [ ! -f "$TASKS_FILE" ]; then
            cat > "$TASKS_FILE" << 'EOF'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "CCDebug: Analyze Current File",
            "type": "shell",
            "command": "ccdebug",
            "args": [
                "-f", "${file}",
                "--lang", "zh",
                "--suggest"
            ],
            "presentation": {
                "reveal": "always",
                "panel": "dedicated"
            },
            "problemMatcher": []
        },
        {
            "label": "CCDebug: Analyze Clipboard",
            "type": "shell",
            "command": "ccdebug",
            "args": [
                "--lang", "zh",
                "--suggest",
                "-c"
            ],
            "presentation": {
                "reveal": "always",
                "panel": "dedicated"
            }
        },
        {
            "label": "CCDebug: Interactive Mode",
            "type": "shell",
            "command": "ccdebug",
            "args": [
                "-i",
                "--lang", "zh"
            ],
            "presentation": {
                "reveal": "always",
                "panel": "dedicated",
                "focus": true
            }
        }
    ]
}
EOF
            print_success "VS Code tasks created"
        else
            print_warning "VS Code tasks already exist"
        fi
    fi
else
    print_info "VS Code not detected, skipping VS Code integration"
fi

# Step 8: Test installation
print_info "Step 8: Testing installation..."

# Test basic command
if python3 -m claudecode_debugger.cli_new --help > /dev/null 2>&1; then
    print_success "Basic command test passed"
else
    print_error "Basic command test failed"
fi

# Test wrapper if possible
if [ -f "$WRAPPER_SCRIPT" ]; then
    if python3 "$WRAPPER_SCRIPT" "/ccdebug --help" > /dev/null 2>&1; then
        print_success "Wrapper test passed"
    else
        print_warning "Wrapper test failed, but this might be expected"
    fi
fi

# Final summary
echo -e "\n${GREEN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║         Installation Complete! 🎉                    ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "\n${BLUE}Available Commands:${NC}"
echo "  • ccdebug        - Basic CCDebugger command"
echo "  • ccdb           - Short alias"
echo "  • cczh           - Chinese mode with suggestions"
echo "  • ccen           - English mode with suggestions"
echo "  • ccquick        - Quick analysis"
echo "  • ccfull         - Full analysis with all features"
echo "  • ccdebug_auto   - Auto-analyze command errors"
echo "  • ccdebug_watch  - Watch log files for errors"

echo -e "\n${BLUE}Claude Code Integration:${NC}"
echo "  Use /ccdebug in Claude Code for intelligent debugging"
echo "  Example: /ccdebug --last --zh"

echo -e "\n${YELLOW}Important:${NC}"
echo "  1. Reload your shell: source $SHELL_RC"
echo "  2. Or start a new terminal session"
echo "  3. Test with: ccdebug --help"

echo -e "\n${GREEN}Happy Debugging! 🚀${NC}\n"