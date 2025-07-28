# Claude Code Integration Guide for CCDebugger

## 🚀 快速開始

CCDebugger 現已完全支援 Claude Code！無需手動輸入指令，自動偵測並分析錯誤。

### 安裝與設置

1. **安裝 CCDebugger**
```bash
pip install claudecode-debugger
```

2. **配置 Claude Code**
在 `~/.claude/ccdebug.json` 創建配置文件：
```json
{
  "autoAnalyze": true,
  "defaultLanguage": "zh",
  "enableSuggestions": true,
  "saveHistory": true,
  "monitorMode": false,
  "contextLines": 10
}
```

3. **啟用整合**
```python
# 在你的 Python 專案中
from claude_code_integration import claude_code_hook

# Claude Code 會自動使用這個 hook
```

## 🎯 核心功能

### 1. 自動錯誤偵測

Claude Code 執行命令時，CCDebugger 會自動：
- 偵測錯誤模式
- 提取錯誤上下文
- 生成 AI 調試提示
- 提供智能建議

**支援的錯誤類型：**
- Python: Traceback, SyntaxError, TypeError, etc.
- JavaScript/TypeScript: 運行時錯誤、編譯錯誤
- 測試失敗: pytest, jest, mocha
- 構建錯誤: webpack, tsc, etc.

### 2. 無縫整合體驗

```python
# 當你在 Claude Code 中執行有錯誤的代碼
result = undefined_function()  # NameError

# CCDebugger 自動顯示：
╭─────────────────────────────────────────────────────────────────╮
│ 🔍 CCDebugger 自動錯誤分析                                      │
╰─────────────────────────────────────────────────────────────────╯

⚠️ **CCDebugger 錯誤分析報告**

**錯誤類型**: NameError
**嚴重程度**: high

**AI 調試提示**:
你遇到了一個 NameError，這表示 Python 無法找到名為 'undefined_function' 的函數或變量。

**🎯 智能建議**:
1. 檢查是否正確導入了該函數
2. 確認函數名稱拼寫是否正確
3. 檢查函數是否在當前作用域內定義

**⚡ 快速操作**:
• 複製此分析: `ccdebug --last --copy`
• 深度分析: `ccdebug --last --deep`
• 查看歷史: `ccdebug --history`
```

### 3. 監控模式

持續監控所有命令輸出，自動分析錯誤：

```python
from claude_code_integration import ClaudeCodeMonitor

# 啟動監控
monitor = ClaudeCodeMonitor()
print(monitor.start_monitoring())

# 所有後續錯誤都會自動分析
# ...

# 停止監控並查看統計
print(monitor.stop_monitoring())
```

### 4. 快速指令

雖然 CCDebugger 會自動工作，你仍可使用這些指令：

- `ccdebug --last` - 分析最後一個錯誤
- `ccdebug --last --zh` - 使用中文分析
- `ccdebug --last --deep` - 深度分析含建議
- `ccdebug --history` - 查看錯誤歷史
- `ccdebug --monitor start` - 開始監控模式
- `ccdebug --clipboard` - 從剪貼板讀取錯誤

## 📋 進階配置

### 自定義錯誤模式

```python
from claude_code_integration import ClaudeCodeDebugger

# 添加自定義錯誤模式
debugger = ClaudeCodeDebugger()
debugger.ERROR_PATTERNS.extend([
    r'CustomError: .+',
    r'CRITICAL: .+',
])
```

### 整合到 CI/CD

```yaml
# .github/workflows/test.yml
- name: Run tests with CCDebugger
  run: |
    pytest --tb=short | python -c "
    from claude_code_integration import claude_code_hook
    import sys
    output = sys.stdin.read()
    result = claude_code_hook(output, 'pytest')
    if result:
        print(result)
        sys.exit(1)
    "
```

### 歷史記錄管理

錯誤歷史保存在 `~/.claude/ccdebug_history.json`：

```python
# 查看歷史
from claude_code_integration import analyze_last_error

# 分析最後一個錯誤
print(analyze_last_error())

# 使用英文分析
print(analyze_last_error(lang='en'))
```

## 🔧 API 參考

### ClaudeCodeDebugger

主要的調試器類：

```python
debugger = ClaudeCodeDebugger(
    lang='zh',  # 語言: 'zh' 或 'en'
    auto_mode=True  # 自動模式
)

# 手動分析
result = debugger.auto_debug(error_output, context={
    'command': 'pytest',
    'file': 'test_app.py'
})
```

### claude_code_hook

自動鉤子函數：

```python
result = claude_code_hook(
    output=command_output,
    command='python app.py'
)
```

### ClaudeCodeMonitor

監控器類：

```python
monitor = ClaudeCodeMonitor()
monitor.start_monitoring()
# ... 執行命令 ...
stats = monitor.stop_monitoring()
```

## 💡 最佳實踐

1. **配置文件位置**
   - 專案級: `.ccdebugrc`
   - 用戶級: `~/.ccdebugrc`
   - Claude 專用: `~/.claude/ccdebug.json`

2. **性能優化**
   - CCDebugger 優先使用 Python API（更快）
   - 自動降級到 CLI 模式（相容性更好）
   - 智能緩存減少重複分析

3. **團隊協作**
   - 共享 `.ccdebugrc` 配置
   - 統一錯誤分析語言
   - 使用自定義模板

## 🐛 問題排除

### CCDebugger 沒有自動運行？

1. 確認安裝正確：
```bash
pip show claudecode-debugger
```

2. 檢查配置文件：
```bash
cat ~/.claude/ccdebug.json
```

3. 手動測試：
```python
from claude_code_integration import claude_code_hook
print(claude_code_hook("Error: test", "test"))
```

### 分析結果不準確？

1. 使用深度分析模式：
```bash
ccdebug --last --deep --analyze-stack
```

2. 提供更多上下文：
```bash
ccdebug --last --context app.py --line 42
```

## 🎯 使用場景

### 場景 1: 開發時自動調試
```python
# 開發時遇到錯誤，CCDebugger 自動分析
# 無需離開 Claude Code，立即獲得解決方案
```

### 場景 2: 代碼審查輔助
```python
# PR 中的錯誤自動標記並提供修復建議
# 提高代碼審查效率
```

### 場景 3: 學習與教學
```python
# 初學者遇到錯誤時，自動獲得詳細解釋
# 包含錯誤原因、解決方案和最佳實踐
```

## 🚀 即將推出

- VS Code 擴展整合
- 更多 IDE 支援
- 團隊協作功能
- AI 模型自定義

---

**讓 AI 秒懂你的 Bug！** 🎯

GitHub: [CCDebugger](https://github.com/888wing/ClaudeCode-Debugger)