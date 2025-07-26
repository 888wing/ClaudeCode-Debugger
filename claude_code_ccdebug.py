#!/usr/bin/env python3
"""
Claude Code /ccdebug Command Implementation
實現 /ccdebug slash command 的核心功能
"""

import os
import sys
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pyperclip

class CCDebugCommand:
    """Implementation of /ccdebug slash command for Claude Code"""
    
    def __init__(self):
        self.config = self.load_config()
        self.last_error = None
        self.error_history = []
        
    def load_config(self) -> Dict:
        """Load user configuration"""
        config_paths = [
            Path.cwd() / '.ccdebugrc',
            Path.home() / '.ccdebugrc',
        ]
        
        default_config = {
            "defaultLanguage": "zh",
            "defaultMode": "deep",
            "autoSuggest": True,
            "copyToClipboard": True,
            "contextLines": 10,
            "excludePatterns": ["node_modules", ".git", "__pycache__"],
        }
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        user_config = json.load(f)
                        default_config.update(user_config)
                        break
                except:
                    pass
                    
        return default_config
    
    def parse_command(self, command: str) -> Tuple[Dict, str]:
        """Parse /ccdebug command and options"""
        # Remove /ccdebug prefix
        if command.startswith('/ccdebug'):
            command = command[8:].strip()
        elif command.startswith('/ccdb'):
            command = command[5:].strip()
            
        options = {
            'lang': self.config['defaultLanguage'],
            'mode': self.config['defaultMode'],
            'copy': self.config['copyToClipboard'],
            'context_lines': self.config['contextLines'],
        }
        
        error_content = ""
        parts = command.split()
        i = 0
        
        while i < len(parts):
            part = parts[i]
            
            # Language options
            if part in ['--zh', '--cn']:
                options['lang'] = 'zh'
            elif part == '--en':
                options['lang'] = 'en'
            elif part == '--auto-lang':
                options['auto_lang'] = True
                
            # Analysis modes
            elif part == '--quick':
                options['mode'] = 'quick'
            elif part == '--deep':
                options['mode'] = 'deep'
            elif part == '--full':
                options['mode'] = 'full'
                
            # Input sources
            elif part == '--last':
                options['use_last'] = True
            elif part == '--clipboard':
                options['use_clipboard'] = True
            elif part == '--file' and i + 1 < len(parts):
                options['file'] = parts[i + 1]
                i += 1
                
            # Output options
            elif part == '--copy':
                options['copy'] = True
            elif part == '--save' and i + 1 < len(parts):
                options['save'] = parts[i + 1]
                i += 1
                
            # Context options
            elif part == '--context' and i + 1 < len(parts):
                options['context_file'] = parts[i + 1]
                i += 1
            elif part == '--line' and i + 1 < len(parts):
                options['line_number'] = int(parts[i + 1])
                i += 1
                
            # Special modes
            elif part == '--watch' and i + 1 < len(parts):
                options['watch'] = parts[i + 1]
                i += 1
            elif part == '--batch':
                options['batch'] = True
            elif part == '--test-mode':
                options['test_mode'] = True
                
            # Help
            elif part in ['--help', '-h']:
                options['help'] = True
                
            # Error content (anything not starting with --)
            elif not part.startswith('--'):
                error_content = ' '.join(parts[i:])
                break
                
            i += 1
            
        return options, error_content
    
    def execute(self, command: str) -> str:
        """Execute /ccdebug command"""
        options, error_content = self.parse_command(command)
        
        # Handle help
        if options.get('help'):
            return self.show_help()
            
        # Get error content from various sources
        if options.get('use_last') and self.last_error:
            error_content = self.last_error
        elif options.get('use_clipboard'):
            error_content = pyperclip.paste()
        elif options.get('file'):
            try:
                error_content = Path(options['file']).read_text()
            except:
                return f"❌ 無法讀取文件: {options['file']}"
                
        if not error_content:
            return "❌ 未提供錯誤內容。請使用 /ccdebug --help 查看使用方法。"
            
        # Auto-detect language if needed
        if options.get('auto_lang'):
            options['lang'] = self.detect_language(error_content)
            
        # Run analysis based on mode
        if options['mode'] == 'quick':
            result = self.quick_analysis(error_content, options)
        elif options['mode'] == 'deep':
            result = self.deep_analysis(error_content, options)
        elif options['mode'] == 'full':
            result = self.full_analysis(error_content, options)
        else:
            result = self.deep_analysis(error_content, options)
            
        # Handle output
        if options.get('copy'):
            pyperclip.copy(result)
            result += "\n\n✅ 已複製到剪貼板"
            
        if options.get('save'):
            Path(options['save']).write_text(result)
            result += f"\n✅ 已保存到: {options['save']}"
            
        # Store in history
        self.error_history.append({
            'time': datetime.now(),
            'error': error_content[:100] + '...',
            'options': options
        })
        
        return result
    
    def quick_analysis(self, error_content: str, options: Dict) -> str:
        """Quick analysis using basic ccdebug"""
        cmd = ['python3', '-m', 'claudecode_debugger.cli_new']
        cmd.extend([error_content])
        cmd.extend(['--lang', options['lang']])
        
        return self.run_ccdebug(cmd)
    
    def deep_analysis(self, error_content: str, options: Dict) -> str:
        """Deep analysis with suggestions"""
        cmd = ['python3', '-m', 'claudecode_debugger.cli_new']
        cmd.extend([error_content])
        cmd.extend(['--lang', options['lang']])
        cmd.extend(['--suggest', '--analyze-stack'])
        
        if options.get('verbose'):
            cmd.append('--verbose')
            
        return self.run_ccdebug(cmd)
    
    def full_analysis(self, error_content: str, options: Dict) -> str:
        """Full analysis with context"""
        cmd = ['python3', '-m', 'claudecode_debugger.cli_new']
        cmd.extend([error_content])
        cmd.extend(['--lang', options['lang']])
        cmd.extend(['--suggest', '--analyze-stack', '--verbose'])
        
        if options.get('context_file'):
            cmd.extend(['--context', options['context_file']])
            
        return self.run_ccdebug(cmd)
    
    def run_ccdebug(self, cmd: List[str]) -> str:
        """Run ccdebug command and return output"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"❌ 分析失敗:\n{result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "❌ 分析超時（30秒）"
        except Exception as e:
            return f"❌ 執行錯誤: {str(e)}"
    
    def detect_language(self, error_content: str) -> str:
        """Auto-detect language from error content"""
        chinese_patterns = ['錯誤', '異常', '失敗', '找不到', '無法']
        
        for pattern in chinese_patterns:
            if pattern in error_content:
                return 'zh'
                
        return 'en'
    
    def show_help(self) -> str:
        """Show help message"""
        return """
🛠️ **CCDebug Command Help**

**基本用法:**
- `/ccdebug` - 分析上一個錯誤
- `/ccdebug "error message"` - 分析特定錯誤
- `/ccdb` - 簡短別名

**語言選項:**
- `--zh` / `--cn` - 使用中文
- `--en` - 使用英文
- `--auto-lang` - 自動檢測語言

**分析模式:**
- `--quick` - 快速分析
- `--deep` - 深度分析（預設）
- `--full` - 完整分析含代碼上下文

**輸入來源:**
- `--last` - 使用上一個錯誤
- `--clipboard` - 從剪貼板讀取
- `--file <path>` - 從文件讀取

**輸出選項:**
- `--copy` - 複製到剪貼板
- `--save <path>` - 保存到文件

**範例:**
```
/ccdebug --last --zh
/ccdebug "TypeError: undefined" --deep
/ccdb --file error.log --save report.md
```

💡 提示: 在 ~/.ccdebugrc 設定預設選項
"""
    
    def watch_errors(self, error_content: str, last_error: Optional[str] = None) -> Optional[str]:
        """Monitor for errors and suggest /ccdebug"""
        error_patterns = [
            r'Error:|Exception:|Failed:|錯誤:|異常:|失敗:',
            r'Traceback \(most recent call last\):',
            r'TypeError:|AttributeError:|ValueError:',
            r'at .+ \(.+:\d+:\d+\)',
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, error_content, re.IGNORECASE):
                self.last_error = error_content
                return self.suggest_command(error_content)
                
        return None
    
    def suggest_command(self, error_content: str) -> str:
        """Suggest appropriate /ccdebug command"""
        # Detect error type
        is_test = 'test' in error_content.lower() or 'spec' in error_content.lower()
        is_build = 'build' in error_content.lower() or 'compile' in error_content.lower()
        has_stack = 'Traceback' in error_content or ' at ' in error_content
        
        suggestions = []
        
        # Basic suggestion
        lang = '--zh' if self.detect_language(error_content) == 'zh' else '--en'
        suggestions.append(f"/ccdebug --last {lang}")
        
        # Specific suggestions
        if has_stack:
            suggestions.append(f"/ccdebug --last {lang} --deep")
            
        if is_test:
            suggestions.append(f"/ccdebug --last {lang} --test-mode")
            
        if is_build:
            suggestions.append(f"/ccdebug --last {lang} --full")
            
        return f"""
🔍 偵測到錯誤，建議使用:

{chr(10).join(f'• `{s}`' for s in suggestions)}

或使用 `/ccdebug --help` 查看更多選項
"""


# Command line interface
def main():
    """CLI interface for testing"""
    if len(sys.argv) < 2:
        print("Usage: python claude_code_ccdebug.py '<command>'")
        print("Example: python claude_code_ccdebug.py '/ccdebug --last --zh'")
        return
        
    command = ' '.join(sys.argv[1:])
    ccdebug = CCDebugCommand()
    
    # Test with sample error
    ccdebug.last_error = """
Traceback (most recent call last):
  File "app.py", line 42, in process
    result = data.process()
AttributeError: 'NoneType' object has no attribute 'process'
"""
    
    result = ccdebug.execute(command)
    print(result)


if __name__ == "__main__":
    main()