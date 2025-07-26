# Claude Code + CCDebugger 使用指南

## 🚀 快速開始

### 1. 安裝
```bash
# 執行安裝腳本
./install_claude_integration.sh

# 重新載入 shell
source ~/.zshrc  # 或 ~/.bashrc
```

### 2. 基本使用

在 Claude Code 中，當遇到錯誤時：

```
# 方式 1: 直接分析
User: python app.py
Claude: [顯示錯誤]
User: /ccdebug --last --zh

# 方式 2: 複製錯誤後
User: /ccdebug --clipboard --zh

# 方式 3: 指定錯誤
User: /ccdebug "TypeError: 'NoneType' object" --zh
```

## 📖 詳細功能指南

### /ccdebug 指令選項

#### 基本指令
- `/ccdebug` - 分析上一個錯誤
- `/ccdb` - 簡短別名
- `/ccdebug --help` - 顯示幫助

#### 語言設定
- `/ccdebug --zh` - 中文輸出
- `/ccdebug --en` - 英文輸出
- `/ccdebug --auto-lang` - 自動偵測語言

#### 分析模式
- `/ccdebug --quick` - 快速分析（基本模式）
- `/ccdebug --deep` - 深度分析（預設）
- `/ccdebug --full` - 完整分析（含代碼上下文）

#### 輸入來源
- `/ccdebug --last` - 使用上一個錯誤
- `/ccdebug --clipboard` - 從剪貼板讀取
- `/ccdebug --file error.log` - 從檔案讀取

#### 輸出選項
- `/ccdebug --copy` - 複製結果到剪貼板
- `/ccdebug --save report.md` - 保存到檔案

## 🎯 使用場景範例

### 場景 1: Python 開發調試

```python
# 當您執行 Python 程式碼出錯時
User: python manage.py runserver
Claude: [顯示 Django 錯誤]

User: /ccdebug --last --zh --deep
Claude: 
🚨 Python 錯誤 - HIGH 優先級
檢測到: ImportError

🎯 智能建議：
1. 安裝缺失的套件: pip install django
2. 檢查虛擬環境是否啟動
3. 驗證 PYTHONPATH 設定

[詳細分析...]
```

### 場景 2: JavaScript/TypeScript 調試

```javascript
// React 開發中遇到錯誤
User: npm start
Claude: [顯示 TypeError]

User: /ccdebug --last --zh --full --context App.tsx
Claude:
🚨 TypeScript 錯誤 - HIGH 優先級
錯誤位置: App.tsx:42

代碼上下文:
>>> 42 | const user = data.user.name

🎯 建議：
1. 添加可選鏈: data?.user?.name
2. 添加類型檢查
3. 設定預設值

[完整建議...]
```

### 場景 3: 測試失敗分析

```bash
# 測試失敗時
User: npm test
Claude: [顯示測試失敗]

User: /ccdebug --last --zh --test-mode
Claude:
🧪 測試失敗分析
失敗測試: 3/50

主要問題:
1. UserService.test.js - Mock 設定錯誤
2. API.test.js - 非同步處理問題

[詳細解決方案...]
```

### 場景 4: CI/CD 錯誤調試

```yaml
# GitHub Actions 失敗
User: 查看 CI 日誌發現構建失敗
User: /ccdebug --clipboard --zh --ci-mode

Claude:
🔧 CI/CD 錯誤分析
環境: GitHub Actions / Ubuntu

錯誤類型: 依賴安裝失敗

解決步驟:
1. 更新 package-lock.json
2. 清除 npm cache
3. 指定 Node 版本

[詳細步驟...]
```

## 💡 進階技巧

### 1. 自動錯誤監控

```bash
# 在開發時自動監控錯誤
User: 請監控 server.log 的錯誤

Claude: 我會使用 ccdebug_watch 功能：
ccdebug_watch server.log

# 當日誌中出現錯誤時，會自動分析
```

### 2. 批量錯誤分析

```bash
# 分析多個錯誤日誌
User: /ccdebug --batch --dir logs/ --save analysis.md

Claude: 正在分析 logs/ 目錄下的所有錯誤...
找到 5 個錯誤文件，生成綜合報告...
```

### 3. 自訂配置

創建 `~/.ccdebugrc`:
```json
{
  "defaultLanguage": "zh",
  "defaultMode": "deep",
  "autoSuggest": true,
  "copyToClipboard": true,
  "contextLines": 15,
  "favoriteFrameworks": ["django", "react", "vue"],
  "customPatterns": {
    "myapp": {
      "errorPattern": "MyAppError:",
      "suggestion": "檢查 MyApp 配置文件"
    }
  }
}
```

### 4. VS Code 整合

使用 VS Code 任務：
- `Cmd+Shift+P` → `Tasks: Run Task`
- 選擇 `CCDebug: Analyze Current File`

或設定快捷鍵：
```json
{
  "key": "cmd+shift+d",
  "command": "workbench.action.tasks.runTask",
  "args": "CCDebug: Analyze Clipboard"
}
```

## 🛠️ Shell 函數使用

### ccdebug_auto - 自動調試

```bash
# 自動分析命令錯誤
ccdebug_auto python script.py
ccdebug_auto npm run build
ccdebug_auto docker compose up
```

### ccdebug_watch - 監控日誌

```bash
# 監控日誌文件
ccdebug_watch /var/log/app.log
ccdebug_watch ./debug.log
```

## 📝 最佳實踐

### 1. 設定個人偏好
```bash
# 在 ~/.zshrc 或 ~/.bashrc 添加
export CCDEBUG_LANG=zh
export CCDEBUG_MODE=deep
```

### 2. 項目專屬配置
在項目根目錄創建 `.ccdebugrc`:
```json
{
  "language": "zh",
  "frameworks": ["django", "celery"],
  "ignorePatterns": ["*.test.js", "migrations/*"]
}
```

### 3. 團隊協作
```bash
# 分享調試報告
/ccdebug --last --save debug-report.md
# 提交到 Git 或分享給團隊
```

### 4. 持續改進
```bash
# 查看歷史分析
/ccdebug --history

# 分析成功率
/ccdebug --stats
```

## 🤝 Claude Code 工作流程整合

### 智能提示
Claude Code 會在適當時機建議使用 /ccdebug：

```
Claude: 我注意到執行命令時出現了錯誤。需要我幫您分析嗎？
       建議使用: /ccdebug --last --zh --deep
```

### 上下文感知
Claude Code 會記住：
- 您的語言偏好
- 常用的分析模式
- 項目類型和框架
- 歷史錯誤模式

### 學習和改進
- Claude 會學習您的調試習慣
- 根據解決成功率調整建議
- 記住特定錯誤的解決方案

## ❓ 常見問題

### Q: /ccdebug 命令找不到？
A: 請確保已執行安裝腳本並重載 shell：
```bash
source ~/.zshrc
```

### Q: 如何更改預設語言？
A: 編輯 `~/.ccdebugrc` 或設定環境變數：
```bash
export CCDEBUG_LANG=en
```

### Q: 分析結果太長？
A: 使用 `--quick` 模式或 `--save` 保存到文件

### Q: 可以分析其他語言嗎？
A: 支援 Python, JavaScript, TypeScript, Java, Ruby, Go 等主流語言

## 🎉 總結

通過 /ccdebug 整合，您可以：

1. **即時調試** - 錯誤發生時立即獲得幫助
2. **智能分析** - 深度理解錯誤原因
3. **快速修復** - 獲得具體的解決方案
4. **持續學習** - 從錯誤中學習和改進

讓 Claude Code + CCDebugger 成為您的智能調試助手！ 🚀