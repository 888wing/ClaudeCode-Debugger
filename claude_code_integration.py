#!/usr/bin/env python3
"""
Claude Code Integration for CCDebugger
自動偵測錯誤並調用 ccdebugger 生成調試提示
"""

import subprocess
import re
from pathlib import Path
from typing import Optional, Dict, List

class ClaudeCodeDebugger:
    """整合 CCDebugger 到 Claude Code 工作流程"""
    
    # 錯誤模式檢測
    ERROR_PATTERNS = [
        # Python
        r'Traceback \(most recent call last\):',
        r'File ".*?", line \d+',
        r'\w+Error: .+',
        r'\w+Exception: .+',
        
        # JavaScript/TypeScript
        r'TypeError: .+',
        r'ReferenceError: .+',
        r'SyntaxError: .+',
        r'at .+ \(.+:\d+:\d+\)',
        
        # General
        r'ERROR: .+',
        r'FAILED: .+',
        r'Error: .+',
        r'Exception: .+',
    ]
    
    def __init__(self, lang: str = 'zh'):
        """初始化，預設使用中文"""
        self.lang = lang
        self.error_pattern = re.compile('|'.join(self.ERROR_PATTERNS), re.MULTILINE | re.IGNORECASE)
    
    def detect_error_in_output(self, output: str) -> bool:
        """檢測輸出中是否包含錯誤"""
        return bool(self.error_pattern.search(output))
    
    def extract_error_section(self, output: str) -> Optional[str]:
        """從輸出中提取錯誤部分"""
        lines = output.split('\n')
        error_lines = []
        in_error = False
        
        for line in lines:
            if any(re.search(pattern, line) for pattern in self.ERROR_PATTERNS[:4]):
                in_error = True
            
            if in_error:
                error_lines.append(line)
                # 收集完整的錯誤堆疊
                if len(error_lines) > 20:  # 防止收集過多
                    break
        
        return '\n'.join(error_lines) if error_lines else None
    
    def run_ccdebugger(self, error_text: str, **options) -> Dict[str, str]:
        """調用 ccdebugger 生成調試提示"""
        cmd = ['python3', '-m', 'claudecode_debugger.cli_new', error_text]
        
        # 添加選項
        cmd.extend(['--lang', self.lang])
        
        if options.get('analyze_stack'):
            cmd.append('--analyze-stack')
        
        if options.get('suggest', True):  # 預設啟用建議
            cmd.append('--suggest')
            
        if options.get('verbose'):
            cmd.append('--verbose')
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
    
    def auto_debug(self, command_output: str) -> Optional[str]:
        """自動偵測並調試錯誤"""
        if not self.detect_error_in_output(command_output):
            return None
        
        error_text = self.extract_error_section(command_output)
        if not error_text:
            return None
        
        # 調用 ccdebugger
        result = self.run_ccdebugger(
            error_text,
            analyze_stack=True,
            suggest=True
        )
        
        if result['success']:
            return result['output']
        else:
            return f"調試分析失敗: {result['error']}"


# Claude Code 鉤子函數
def claude_code_hook(output: str, command: str = None) -> Optional[str]:
    """
    Claude Code 執行命令後的鉤子函數
    自動偵測錯誤並提供調試建議
    """
    debugger = ClaudeCodeDebugger(lang='zh')
    
    # 檢查是否有錯誤
    debug_output = debugger.auto_debug(output)
    
    if debug_output:
        return f"""
╭─────────────────────────────────────────────────────────────────╮
│ 🔍 CCDebugger 自動錯誤分析                                      │
╰─────────────────────────────────────────────────────────────────╯

{debug_output}

💡 提示: 使用 `ccdebug --help` 查看更多選項
"""
    
    return None


# 範例使用
if __name__ == "__main__":
    # 模擬錯誤輸出
    test_output = """
    Running tests...
    
    Traceback (most recent call last):
      File "test.py", line 42, in test_function
        result = data.process()
    AttributeError: 'NoneType' object has no attribute 'process'
    
    Tests failed!
    """
    
    debugger = ClaudeCodeDebugger()
    
    # 測試錯誤偵測
    print("偵測到錯誤:", debugger.detect_error_in_output(test_output))
    
    # 測試自動調試
    debug_result = debugger.auto_debug(test_output)
    if debug_result:
        print("\n自動調試結果:")
        print(debug_result)