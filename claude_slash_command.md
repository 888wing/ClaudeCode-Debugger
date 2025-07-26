# Claude Code Slash Command: /debug

## 概念

在 Claude Code 中創建一個 `/debug` slash command，自動調用 ccdebugger：

```markdown
/debug [error_message] [options]
```

## 實現方式

### 1. 基本用法

當您在 Claude Code 中遇到錯誤時，只需：

```
/debug "TypeError: Cannot read property 'x' of undefined"
```

Claude 會自動：
1. 識別錯誤類型
2. 調用 ccdebugger 進行分析
3. 提供智能建議
4. 生成調試步驟

### 2. 進階選項

```
/debug --last           # 分析最後一個錯誤
/debug --file error.log # 從文件讀取
/debug --context app.js # 包含代碼上下文
/debug --lang zh        # 使用中文
```

### 3. 工作流程整合

#### 自動錯誤捕獲
Claude Code 可以：
1. 監控執行的命令輸出
2. 自動偵測錯誤模式
3. 提示是否要執行 `/debug`

#### 範例對話
```
User: python app.py
Claude: 執行命令...
[輸出顯示 AttributeError]

Claude: 偵測到錯誤。要我幫您分析嗎？您可以使用：
/debug --last --lang zh

User: /debug --last --lang zh
Claude: [調用 ccdebugger 並顯示分析結果]

🚨 Python 錯誤 - HIGH 優先級
檢測到: AttributeError

🎯 智能建議：
1. 添加 None 檢查
2. 初始化變數
3. 使用 Optional chaining

[詳細的調試步驟...]
```

### 4. 自定義整合

Claude Code 可以記住您的偏好：

```python
# Claude 記住的設定
user_debug_preferences = {
    "language": "zh",
    "auto_suggest": True,
    "analyze_stack": True,
    "context_lines": 10
}

# 之後只需簡單使用
/debug
# Claude 會自動應用您的偏好設定
```

## 優勢

1. **無縫整合**: 不需要離開 Claude Code 環境
2. **智能化**: Claude 可以理解上下文，提供更準確的分析
3. **個性化**: 記住用戶偏好，自動應用設定
4. **工作流程優化**: 減少複製貼上，提高效率

## 實際應用場景

### 場景 1: 即時調試
```
User: 執行測試
Claude: [執行 npm test]
[測試失敗，顯示錯誤]

User: /debug
Claude: 根據剛才的錯誤，我分析如下：
[自動調用 ccdebugger 並解釋結果]
```

### 場景 2: 批量分析
```
User: /debug --all-errors-in logs/
Claude: 找到 3 個錯誤日誌，逐一分析：
[對每個錯誤調用 ccdebugger]
```

### 場景 3: 學習模式
```
User: /debug --explain
Claude: 不僅提供解決方案，還會解釋：
- 為什麼會發生這個錯誤
- 如何避免類似錯誤
- 最佳實踐建議
```

## 總結

透過 `/debug` slash command，CCDebugger 可以完美整合到 Claude Code 中，提供：

- 🎯 **即時分析**: 錯誤發生時立即獲得幫助
- 🧠 **智能建議**: 基於上下文的個性化建議  
- 🔄 **工作流程整合**: 無縫融入開發流程
- 🌍 **多語言支援**: 根據需要切換語言
- 📚 **學習提升**: 不只解決問題，還幫助理解

這樣的整合讓 Claude Code 不只是一個編碼助手，更是一個智能調試夥伴！