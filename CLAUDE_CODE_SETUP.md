# Claude Code 整合 CCDebugger 設定指南

## 快速設定

### 1. 在 Claude Code 設定中加入別名

在您的 shell 設定檔 (`~/.zshrc` 或 `~/.bashrc`) 中加入：

```bash
# CCDebugger 快捷命令
alias ccdebug="python3 -m claudecode_debugger.cli_new"
alias cchelp="ccdebug --help"
alias cczh="ccdebug --lang zh --suggest"
alias ccen="ccdebug --lang en --suggest"

# 自動調試函數
ccdebug_auto() {
    # 執行命令並捕獲輸出
    output=$("$@" 2>&1)
    exit_code=$?
    
    # 顯示原始輸出
    echo "$output"
    
    # 如果命令失敗，自動調用 ccdebugger
    if [ $exit_code -ne 0 ]; then
        echo -e "\n🔍 自動調試分析中..."
        echo "$output" | ccdebug --lang zh --suggest --analyze-stack
    fi
    
    return $exit_code
}

# 使用範例: ccdebug_auto python script.py
```

### 2. Claude Code 工作流程整合

在 Claude Code 中，您可以這樣使用：

#### 方法 1: 直接管道輸入
```bash
# 執行命令並將錯誤傳給 ccdebugger
python script.py 2>&1 | ccdebug --lang zh --suggest

# 或從檔案讀取錯誤
ccdebug -f error.log --analyze-stack --suggest
```

#### 方法 2: 剪貼板整合
```bash
# 複製錯誤到剪貼板後
ccdebug -c --lang zh  # 自動從剪貼板讀取並複製結果
```

#### 方法 3: 互動模式
```bash
# 啟動互動模式，貼上錯誤
ccdebug -i --lang zh --suggest
```

## 進階整合

### 1. VS Code 任務整合

創建 `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Debug with CCDebugger",
            "type": "shell",
            "command": "ccdebug",
            "args": [
                "${file}",
                "--lang", "zh",
                "--suggest",
                "--analyze-stack"
            ],
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "Debug Last Error",
            "type": "shell", 
            "command": "ccdebug -c --lang zh --suggest",
            "presentation": {
                "reveal": "always",
                "panel": "dedicated"
            }
        }
    ]
}
```

### 2. Git Hook 整合

創建 `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# 執行測試並自動調試失敗
if ! npm test; then
    echo "測試失敗，啟動 CCDebugger 分析..."
    npm test 2>&1 | ccdebug --lang zh --suggest
    exit 1
fi
```

### 3. CI/CD 整合

在 GitHub Actions 中使用：

```yaml
- name: Run Tests with Auto Debug
  run: |
    if ! npm test; then
      npm test 2>&1 | python -m claudecode_debugger.cli_new --lang en --suggest > debug_report.md
      cat debug_report.md >> $GITHUB_STEP_SUMMARY
      exit 1
    fi
```

## Claude Code 專用功能

### 1. 錯誤監控模式

```bash
# 監控日誌文件並自動分析新錯誤
watch_errors() {
    tail -f "$1" | while read line; do
        if echo "$line" | grep -E "(Error|Exception|Failed)" > /dev/null; then
            echo "$line" | ccdebug --lang zh --suggest
        fi
    done
}

# 使用: watch_errors /var/log/app.log
```

### 2. 批量錯誤分析

```bash
# 分析多個錯誤日誌
for log in *.log; do
    echo "分析 $log..."
    ccdebug -f "$log" -o "${log%.log}_debug.md" --lang zh
done
```

### 3. 智能錯誤分類

```bash
# 根據錯誤類型選擇不同的分析策略
smart_debug() {
    error_text="$1"
    
    if echo "$error_text" | grep -q "TypeError\|AttributeError"; then
        echo "$error_text" | ccdebug --lang zh --suggest --analyze-stack
    elif echo "$error_text" | grep -q "ImportError\|ModuleNotFoundError"; then
        echo "$error_text" | ccdebug --lang zh --verbose
    else
        echo "$error_text" | ccdebug --lang zh
    fi
}
```

## 最佳實踐

1. **設定預設語言**：
   ```bash
   export CCDEBUG_LANG=zh  # 或 en
   ```

2. **建立專案特定配置**：
   ```bash
   # .ccdebugrc
   {
     "lang": "zh",
     "default_options": ["--suggest", "--analyze-stack"],
     "auto_copy": true
   }
   ```

3. **整合到開發工作流程**：
   - 測試失敗時自動分析
   - 部署前的錯誤檢查
   - Code Review 時的錯誤文檔

## 範例場景

### 場景 1: Python 開發
```bash
# 開發時遇到錯誤
python app.py
# AttributeError: 'NoneType' object...

# 立即分析
!! | ccdebug --lang zh --suggest --context app.py
```

### 場景 2: JavaScript/TypeScript
```bash
# npm 構建失敗
npm run build 2>&1 | ccdebug --lang zh --analyze-stack
```

### 場景 3: 調試 CI 錯誤
```bash
# 從 CI 日誌複製錯誤
ccdebug -c --lang en --suggest -o ci_debug_report.md
```

## 結論

CCDebugger 可以完美整合到 Claude Code 的工作流程中，提供：
- 🚀 即時錯誤分析
- 🌍 多語言支援
- 💡 智能建議
- 📋 自動化工作流程

讓調試變得更簡單、更智能！