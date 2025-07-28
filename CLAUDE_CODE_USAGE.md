# CCDebugger Claude Code 使用指南

## 🚀 快速開始

### 1. 基本用法

在 Claude Code 中，當你遇到錯誤時，CCDebugger 會自動偵測並分析。你也可以手動使用以下命令：

```bash
# 分析最後一個錯誤
/ccdebug --last

# 分析特定錯誤（中文）
/ccdebug "TypeError: Cannot read property" --zh

# 深度分析
/ccdebug --last --deep
```

### 2. 常用命令

| 命令 | 說明 |
|------|------|
| `/ccdebug --help` | 顯示幫助信息 |
| `/ccdebug --last` | 分析最後的錯誤 |
| `/ccdebug --last --zh` | 使用中文分析 |
| `/ccdebug --last --deep` | 深度分析（含建議） |
| `/ccdebug --clipboard` | 從剪貼板讀取錯誤 |

### 3. 簡短別名

```bash
# 使用簡短別名
/ccdb --last --zh
```

## 📋 進階功能

### 監控模式

持續監控所有命令輸出，自動分析錯誤：

```bash
# 開始監控
ccdebug monitor start

# 停止監控
ccdebug monitor stop
```

### 查看歷史

```bash
# 查看最近 5 條錯誤
ccdebug history

# 查看最近 10 條錯誤
ccdebug history 10
```

### 配置管理

```bash
# 查看配置
ccdebug config show

# 設置預設語言為中文
ccdebug config set defaultLanguage zh

# 啟用自動建議
ccdebug config set enableSuggestions true
```

## 🎯 使用場景

### 場景 1: Python 錯誤

```python
# 當你運行有錯誤的 Python 代碼
undefined_function()  # NameError

# CCDebugger 自動顯示：
╭─────────────────────────────────────────────────────────────────╮
│ 🔍 CCDebugger 自動錯誤分析                                      │
╰─────────────────────────────────────────────────────────────────╯

⚠️ **CCDebugger 錯誤分析報告**
**錯誤類型**: NameError
**嚴重程度**: high

**AI 調試提示**:
你遇到了一個 NameError，這表示 Python 無法找到名為 'undefined_function' 的函數。

**🎯 智能建議**:
1. 檢查是否正確導入了該函數
2. 確認函數名稱拼寫是否正確
```

### 場景 2: JavaScript/TypeScript 錯誤

```javascript
// TypeError
const user = null;
console.log(user.name);  // TypeError

// 使用 CCDebugger 分析
/ccdebug --last --zh
```

### 場景 3: 編譯錯誤

```bash
# TypeScript 編譯錯誤
$ tsc
error TS2322: Type 'string' is not assignable to type 'number'.

# CCDebugger 會自動分析並提供解決方案
```

## ⚡ 快速技巧

1. **自動偵測**: CCDebugger 會自動偵測常見錯誤模式
2. **多語言支援**: 支援中文和英文分析
3. **深度分析**: 使用 `--deep` 獲得更詳細的建議
4. **歷史記錄**: 所有錯誤都會保存到 `~/.claude/ccdebug_history.json`

## 🔧 配置文件

在 `~/.claude/ccdebug.json` 中自定義設置：

```json
{
  "autoAnalyze": true,
  "defaultLanguage": "zh",
  "enableSuggestions": true,
  "saveHistory": true,
  "contextLines": 10
}
```

## 📝 注意事項

1. 如果看到模板錯誤警告，通常不影響使用
2. 監控模式會持續運行，記得在不需要時關閉
3. 歷史記錄會自動限制大小，無需手動清理

---

**讓 AI 秒懂你的 Bug！** 🎯