#!/usr/bin/env python3
"""
Claude Code Integration for CCDebugger
自動偵測錯誤並調用 ccdebugger 生成調試提示
支援無縫整合到 Claude Code 工作流程
"""

import subprocess
import re
import json
import os
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import tempfile

class ClaudeCodeDebugger:
    """整合 CCDebugger 到 Claude Code 工作流程"""
    
    # 錯誤模式檢測（更完整的列表）
    ERROR_PATTERNS = [
        # Python
        r'Traceback \(most recent call last\):',
        r'File ".*?", line \d+',
        r'\w+Error: .+',
        r'\w+Exception: .+',
        r'IndentationError:',
        r'TabError:',
        
        # JavaScript/TypeScript  
        r'TypeError: .+',
        r'ReferenceError: .+',
        r'SyntaxError: .+',
        r'at .+ \(.+:\d+:\d+\)',
        r'Cannot read prop\w+ .+ of (null|undefined)',
        r'is not a function',
        
        # Build/Compile Errors
        r'error TS\d+:',
        r'error CS\d+:',
        r'compilation failed',
        r'build failed',
        
        # Test Failures
        r'FAIL\s+\w+',
        r'AssertionError:',
        r'Expected .+ to (be|equal)',
        r'Test failed:',
        
        # General
        r'ERROR: .+',
        r'FAILED: .+',
        r'Error: .+',
        r'Exception: .+',
        r'fatal:',
        r'panic:',
    ]
    
    def __init__(self, lang: str = 'zh', auto_mode: bool = True):
        """
        初始化
        Args:
            lang: 語言設定 ('zh' 或 'en')
            auto_mode: 是否自動分析錯誤（無需手動調用）
        """
        self.lang = lang
        self.auto_mode = auto_mode
        self.error_pattern = re.compile('|'.join(self.ERROR_PATTERNS), re.MULTILINE | re.IGNORECASE)
        self.error_history = []
        self.max_history = 10
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """載入配置文件"""
        config_paths = [
            Path.cwd() / '.ccdebugrc',
            Path.home() / '.ccdebugrc',
            Path.home() / '.claude' / 'ccdebug.json',
        ]
        
        default_config = {
            "autoAnalyze": True,
            "defaultLanguage": self.lang,
            "contextLines": 10,
            "saveHistory": True,
            "maxHistorySize": 10,
            "outputFormat": "structured",
            "enableSuggestions": True,
            "monitorMode": False,
        }
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        if config_path.suffix == '.json':
                            user_config = json.load(f)
                        else:
                            user_config = json.load(f)
                        default_config.update(user_config)
                        break
                except:
                    pass
                    
        return default_config
    
    def detect_error_in_output(self, output: str) -> bool:
        """檢測輸出中是否包含錯誤"""
        return bool(self.error_pattern.search(output))
    
    def extract_error_section(self, output: str) -> Optional[str]:
        """從輸出中提取錯誤部分（改進版）"""
        lines = output.split('\n')
        error_sections = []
        current_section = []
        in_error = False
        error_start_line = -1
        
        for i, line in enumerate(lines):
            # 檢測錯誤開始
            if any(re.search(pattern, line) for pattern in self.ERROR_PATTERNS):
                if not in_error:
                    in_error = True
                    error_start_line = i
                    # 收集錯誤前的上下文（配置中的 contextLines）
                    context_start = max(0, i - self.config.get('contextLines', 5))
                    if context_start < i:
                        current_section.extend([f"[Context] {lines[j]}" for j in range(context_start, i)])
                
                current_section.append(line)
            elif in_error:
                # 繼續收集錯誤相關行
                if line.strip() and (
                    line.startswith(' ') or 
                    line.startswith('\t') or
                    'at ' in line or
                    re.match(r'^\s*\^+\s*$', line)  # Python 錯誤指示符
                ):
                    current_section.append(line)
                else:
                    # 錯誤結束，保存並重置
                    if current_section:
                        error_sections.append('\n'.join(current_section))
                        current_section = []
                    in_error = False
            
            # 防止收集過多
            if len(current_section) > 50:
                error_sections.append('\n'.join(current_section))
                current_section = []
                in_error = False
        
        # 處理最後一個錯誤
        if current_section:
            error_sections.append('\n'.join(current_section))
        
        # 合併多個錯誤部分
        if error_sections:
            return '\n\n--- Error Section ---\n\n'.join(error_sections)
        
        return None
    
    def run_ccdebugger(self, error_text: str, **options) -> Dict[str, str]:
        """調用 ccdebugger 生成調試提示（增強版）"""
        # 優先嘗試直接導入，提高性能
        try:
            from claudecode_debugger.core.detector import ErrorDetector
            from claudecode_debugger.core.generator import PromptGenerator
            from claudecode_debugger.analyzers import StackTraceAnalyzer, PatternAnalyzer
            from claudecode_debugger.suggestions import SuggestionEngine
            
            # 直接使用 Python API
            detector = ErrorDetector()
            detected_type = detector.detect(error_text)
            error_info = detector.extract_key_info(error_text, detected_type)
            severity = detector.get_severity(error_text, detected_type)
            
            # 進階分析
            suggestions = []
            if options.get('suggest', True) or self.config.get('enableSuggestions', True):
                pattern_analyzer = PatternAnalyzer()
                pattern_matches = pattern_analyzer.analyze(error_text)
                
                if pattern_matches:
                    suggestion_engine = SuggestionEngine()
                    error_patterns = [p.name for p in pattern_matches]
                    suggestions = suggestion_engine.generate_suggestions(
                        detected_type, error_patterns
                    )
            
            # 生成提示
            generator = PromptGenerator()
            prompt = generator.generate(error_text, detected_type, error_info)
            
            # 格式化輸出
            output = self._format_analysis_output(
                prompt, detected_type, severity, error_info, suggestions
            )
            
            return {
                'success': True,
                'output': output,
                'error': '',
                'metadata': {
                    'type': detected_type,
                    'severity': severity,
                    'suggestions_count': len(suggestions)
                }
            }
            
        except ImportError:
            # 降級到命令行模式
            cmd = ['python3', '-m', 'claudecode_debugger.cli_new', error_text]
            
            # 添加選項
            cmd.extend(['--lang', self.lang])
            
            if options.get('analyze_stack'):
                cmd.append('--analyze-stack')
            
            if options.get('suggest', True):
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
    
    def auto_debug(self, command_output: str, context: Optional[Dict] = None) -> Optional[str]:
        """
        自動偵測並調試錯誤（增強版）
        Args:
            command_output: 命令輸出內容
            context: 額外上下文資訊（如文件路徑、命令等）
        """
        if not self.detect_error_in_output(command_output):
            return None
        
        error_text = self.extract_error_section(command_output)
        if not error_text:
            return None
        
        # 儲存到歷史記錄
        if self.config.get('saveHistory', True):
            self._save_to_history(error_text, context)
        
        # 調用 ccdebugger
        result = self.run_ccdebugger(
            error_text,
            analyze_stack=True,
            suggest=True,
            context=context
        )
        
        if result['success']:
            # 如果有元數據，增加智能建議
            output = result['output']
            if result.get('metadata'):
                meta = result['metadata']
                if meta.get('severity') in ['critical', 'high']:
                    output = f"🚨 **嚴重錯誤** 🚨\n\n{output}"
                    
            return output
        else:
            return f"調試分析失敗: {result['error']}"
    
    def _save_to_history(self, error_text: str, context: Optional[Dict] = None):
        """保存錯誤到歷史記錄"""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_snippet': error_text[:200] + '...' if len(error_text) > 200 else error_text,
            'context': context or {},
            'full_error': error_text
        }
        
        self.error_history.append(history_entry)
        
        # 限制歷史記錄大小
        if len(self.error_history) > self.config.get('maxHistorySize', 10):
            self.error_history.pop(0)
        
        # 可選：保存到文件
        history_file = Path.home() / '.claude' / 'ccdebug_history.json'
        if history_file.parent.exists():
            try:
                with open(history_file, 'w') as f:
                    json.dump(self.error_history, f, indent=2)
            except:
                pass
    
    def _format_analysis_output(self, prompt: str, detected_type: str, 
                               severity: str, error_info: Dict, 
                               suggestions: List) -> str:
        """格式化分析輸出"""
        output_lines = []
        
        # 標題
        severity_emoji = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '📋',
            'low': 'ℹ️'
        }.get(severity, '📌')
        
        output_lines.append(f"{severity_emoji} **CCDebugger 錯誤分析報告**")
        output_lines.append("")
        
        # 錯誤類型和嚴重度
        output_lines.append(f"**錯誤類型**: {detected_type}")
        output_lines.append(f"**嚴重程度**: {severity}")
        output_lines.append("")
        
        # 主要分析結果
        output_lines.append("**AI 調試提示**:")
        output_lines.append(prompt)
        output_lines.append("")
        
        # 智能建議
        if suggestions:
            output_lines.append("**🎯 智能建議**:")
            for i, suggestion in enumerate(suggestions[:3], 1):
                output_lines.append(f"{i}. {suggestion}")
            output_lines.append("")
        
        # 快速操作
        output_lines.append("**⚡ 快速操作**:")
        output_lines.append("• 複製此分析: `ccdebug --last --copy`")
        output_lines.append("• 深度分析: `ccdebug --last --deep`")
        output_lines.append("• 查看歷史: `ccdebug --history`")
        
        return '\n'.join(output_lines)


# Claude Code 鉤子函數
def claude_code_hook(output: str, command: str = None) -> Optional[str]:
    """
    Claude Code 執行命令後的鉤子函數
    自動偵測錯誤並提供調試建議
    """
    # 檢查是否應該跳過（例如 ccdebug 自己的輸出）
    if 'CCDebugger' in output or 'ccdebug' in command if command else False:
        return None
        
    debugger = ClaudeCodeDebugger(lang='zh')
    
    # 準備上下文
    context = {
        'command': command,
        'timestamp': datetime.now().isoformat(),
        'cwd': str(Path.cwd())
    } if command else None
    
    # 檢查是否有錯誤
    debug_output = debugger.auto_debug(output, context)
    
    if debug_output:
        return f"""
╭─────────────────────────────────────────────────────────────────╮
│ 🔍 CCDebugger 自動錯誤分析                                      │
╰─────────────────────────────────────────────────────────────────╯

{debug_output}

💡 提示: 使用 `ccdebug --help` 查看更多選項
"""
    
    return None


# 監控模式：持續監控錯誤
class ClaudeCodeMonitor:
    """Claude Code 錯誤監控器"""
    
    def __init__(self, debugger: Optional[ClaudeCodeDebugger] = None):
        self.debugger = debugger or ClaudeCodeDebugger(lang='zh')
        self.monitoring = False
        self.error_count = 0
        self.start_time = None
        
    def start_monitoring(self):
        """開始監控模式"""
        self.monitoring = True
        self.start_time = datetime.now()
        self.error_count = 0
        
        return """
🔍 **CCDebugger 監控模式已啟動**

• 自動偵測所有錯誤
• 即時提供調試建議
• 錯誤歷史自動保存

停止監控: `ccdebug --monitor stop`
"""
    
    def stop_monitoring(self):
        """停止監控模式"""
        if not self.monitoring:
            return "監控模式未啟動"
            
        self.monitoring = False
        duration = datetime.now() - self.start_time
        
        return f"""
📊 **監控統計**

• 運行時間: {duration}
• 偵測錯誤: {self.error_count} 個
• 歷史保存: ~/.claude/ccdebug_history.json

感謝使用 CCDebugger！
"""
    
    def process_output(self, output: str, command: str = None) -> Optional[str]:
        """處理輸出（監控模式）"""
        if not self.monitoring:
            return None
            
        result = claude_code_hook(output, command)
        if result:
            self.error_count += 1
            
        return result


# 便捷函數：快速分析最後的錯誤
def analyze_last_error(lang: str = 'zh') -> str:
    """分析最後一個錯誤"""
    history_file = Path.home() / '.claude' / 'ccdebug_history.json'
    
    if not history_file.exists():
        return "❌ 沒有錯誤歷史記錄"
        
    try:
        with open(history_file) as f:
            history = json.load(f)
            
        if not history:
            return "❌ 錯誤歷史為空"
            
        last_error = history[-1]
        debugger = ClaudeCodeDebugger(lang=lang)
        
        result = debugger.run_ccdebugger(
            last_error['full_error'],
            analyze_stack=True,
            suggest=True
        )
        
        if result['success']:
            return result['output']
        else:
            return f"❌ 分析失敗: {result['error']}"
            
    except Exception as e:
        return f"❌ 讀取歷史失敗: {str(e)}"


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