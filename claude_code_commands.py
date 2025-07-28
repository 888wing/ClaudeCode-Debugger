#!/usr/bin/env python3
"""
Claude Code Commands for CCDebugger
提供簡單的命令介面給 Claude Code 使用
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, List

# 支援的命令列表
COMMANDS = {
    'analyze': '分析錯誤',
    'last': '分析最後的錯誤', 
    'history': '查看錯誤歷史',
    'monitor': '監控模式',
    'config': '查看/修改配置',
    'clear': '清除錯誤歷史',
    'help': '顯示幫助'
}

class CCDebugCommands:
    """CCDebugger 命令處理器"""
    
    def __init__(self):
        self.config_file = Path.home() / '.claude' / 'ccdebug.json'
        self.history_file = Path.home() / '.claude' / 'ccdebug_history.json'
        
    def execute(self, command: str, *args) -> str:
        """執行命令"""
        if command not in COMMANDS:
            return f"❌ 未知命令: {command}\n使用 'help' 查看可用命令"
            
        method = getattr(self, f'cmd_{command}', None)
        if method:
            return method(*args)
        else:
            return f"❌ 命令 '{command}' 尚未實現"
    
    def cmd_analyze(self, error_text: Optional[str] = None) -> str:
        """分析錯誤"""
        if not error_text:
            return "❌ 請提供錯誤文本"
            
        from claude_code_integration import ClaudeCodeDebugger
        
        debugger = ClaudeCodeDebugger()
        result = debugger.run_ccdebugger(error_text, analyze_stack=True, suggest=True)
        
        if result['success']:
            return result['output']
        else:
            return f"❌ 分析失敗: {result['error']}"
    
    def cmd_last(self) -> str:
        """分析最後的錯誤"""
        from claude_code_integration import analyze_last_error
        return analyze_last_error()
    
    def cmd_history(self, count: int = 5) -> str:
        """查看錯誤歷史"""
        if not self.history_file.exists():
            return "📋 沒有錯誤歷史記錄"
            
        try:
            with open(self.history_file) as f:
                history = json.load(f)
                
            if not history:
                return "📋 錯誤歷史為空"
                
            output = ["📋 **錯誤歷史** (最近 {} 條)".format(min(count, len(history)))]
            output.append("")
            
            for i, entry in enumerate(history[-count:], 1):
                output.append(f"{i}. **{entry['timestamp']}**")
                output.append(f"   {entry['error_snippet']}")
                if entry.get('context', {}).get('command'):
                    output.append(f"   命令: `{entry['context']['command']}`")
                output.append("")
            
            output.append(f"💡 使用 `ccdebug analyze <編號>` 重新分析特定錯誤")
            
            return '\n'.join(output)
            
        except Exception as e:
            return f"❌ 讀取歷史失敗: {str(e)}"
    
    def cmd_monitor(self, action: str = 'status') -> str:
        """監控模式控制"""
        from claude_code_integration import ClaudeCodeMonitor
        
        monitor = ClaudeCodeMonitor()
        
        if action == 'start':
            return monitor.start_monitoring()
        elif action == 'stop':
            return monitor.stop_monitoring()
        elif action == 'status':
            if monitor.monitoring:
                return "🔍 監控模式運行中"
            else:
                return "⏸️ 監控模式未啟動"
        else:
            return f"❌ 未知的監控動作: {action}\n可用: start, stop, status"
    
    def cmd_config(self, action: str = 'show', key: Optional[str] = None, value: Optional[str] = None) -> str:
        """配置管理"""
        if action == 'show':
            if not self.config_file.exists():
                return "❌ 配置文件不存在"
                
            try:
                with open(self.config_file) as f:
                    config = json.load(f)
                    
                if key:
                    if key in config:
                        return f"**{key}**: {json.dumps(config[key], ensure_ascii=False, indent=2)}"
                    else:
                        return f"❌ 配置項 '{key}' 不存在"
                else:
                    return f"**當前配置**:\n```json\n{json.dumps(config, ensure_ascii=False, indent=2)}\n```"
                    
            except Exception as e:
                return f"❌ 讀取配置失敗: {str(e)}"
                
        elif action == 'set':
            if not key or value is None:
                return "❌ 請提供配置項和值\n例如: config set defaultLanguage zh"
                
            try:
                # 讀取現有配置
                config = {}
                if self.config_file.exists():
                    with open(self.config_file) as f:
                        config = json.load(f)
                
                # 解析值
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                
                # 設置值
                config[key] = value
                
                # 保存配置
                self.config_file.parent.mkdir(exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                    
                return f"✅ 已設置 {key} = {value}"
                
            except Exception as e:
                return f"❌ 設置配置失敗: {str(e)}"
                
        else:
            return f"❌ 未知的配置動作: {action}\n可用: show, set"
    
    def cmd_clear(self, confirm: bool = False) -> str:
        """清除錯誤歷史"""
        if not confirm:
            return "⚠️ 這將清除所有錯誤歷史記錄\n確認清除請使用: clear --confirm"
            
        try:
            if self.history_file.exists():
                self.history_file.unlink()
            return "✅ 錯誤歷史已清除"
        except Exception as e:
            return f"❌ 清除失敗: {str(e)}"
    
    def cmd_help(self) -> str:
        """顯示幫助"""
        output = ["🛠️ **CCDebugger Claude Code 命令**", ""]
        
        # 基本命令
        output.append("**基本命令:**")
        for cmd, desc in COMMANDS.items():
            output.append(f"• `{cmd}` - {desc}")
        output.append("")
        
        # 使用示例
        output.append("**使用示例:**")
        output.append("```")
        output.append("ccdebug last              # 分析最後的錯誤")
        output.append("ccdebug history           # 查看最近 5 條錯誤")
        output.append("ccdebug history 10        # 查看最近 10 條錯誤")
        output.append("ccdebug monitor start     # 開始監控模式")
        output.append("ccdebug monitor stop      # 停止監控模式")
        output.append("ccdebug config show       # 查看所有配置")
        output.append("ccdebug config set defaultLanguage en  # 設置預設語言")
        output.append("ccdebug clear --confirm   # 清除錯誤歷史")
        output.append("```")
        output.append("")
        
        # 快捷方式
        output.append("**快捷方式:**")
        output.append("• 在 Claude Code 中執行命令時自動偵測錯誤")
        output.append("• 使用 `/ccdebug` 或 `/ccdb` slash command")
        output.append("")
        
        output.append("💡 更多資訊: https://github.com/888wing/ClaudeCode-Debugger")
        
        return '\n'.join(output)


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        commands = CCDebugCommands()
        print(commands.cmd_help())
        return
        
    command = sys.argv[1]
    args = sys.argv[2:]
    
    commands = CCDebugCommands()
    result = commands.execute(command, *args)
    print(result)


# 便捷函數供 Claude Code 直接調用
def ccdebug(command_str: str) -> str:
    """
    Claude Code 可以直接調用的函數
    例如: ccdebug("last")
    """
    parts = command_str.split()
    if not parts:
        return CCDebugCommands().cmd_help()
        
    command = parts[0]
    args = parts[1:]
    
    commands = CCDebugCommands()
    return commands.execute(command, *args)


if __name__ == "__main__":
    main()