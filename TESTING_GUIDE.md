# ClaudeCode-Debugger 測試指南

本指南將幫助您完整測試 ClaudeCode-Debugger 的所有功能。

## 🚀 快速開始

### 1. 克隆並安裝

```bash
# 克隆專案
git clone https://github.com/888wing/ClaudeCode-Debugger.git
cd ClaudeCode-Debugger

# 創建虛擬環境（推薦）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝開發版本（包含所有功能）
pip install -e ".[all,dev]"

# 或者只安裝基礎版本
pip install -e .
```

### 2. 驗證安裝

```bash
# 檢查安裝
ccdebug --version
ccdebug --help

# 測試基本功能
ccdebug "TypeError: Cannot read property 'name' of undefined"
```

## 📋 功能測試清單

### 基礎功能測試

#### 1. 命令行輸入測試
```bash
# TypeScript 錯誤
ccdebug "TS2322: Type 'string' is not assignable to type 'number'"

# JavaScript 錯誤
ccdebug "TypeError: Cannot read property 'foo' of undefined"

# Python 錯誤
ccdebug "Traceback (most recent call last): ImportError: No module named requests"

# 記憶體錯誤
ccdebug "FATAL ERROR: JavaScript heap out of memory"

# 網路錯誤
ccdebug "CORS policy: No 'Access-Control-Allow-Origin'"
```

#### 2. 文件輸入測試
```bash
# 創建測試錯誤文件
echo "TS2322: Type 'string' is not assignable to type 'number'" > test_error.log

# 從文件讀取
ccdebug -f test_error.log

# 多個文件（進階功能）
ccdebug -f "*.log"
```

#### 3. 剪貼板測試
```bash
# 複製錯誤到剪貼板
echo "TypeError: undefined is not a function" | pbcopy  # macOS
# 或 echo "TypeError: undefined is not a function" | xclip  # Linux

# 從剪貼板讀取（不帶參數）
ccdebug

# 自動複製結果到剪貼板
ccdebug "SyntaxError: Unexpected token" -c
```

#### 4. 輸出格式測試
```bash
# 輸出到文件
ccdebug "Error message" -o debug_prompt.md

# 不同格式輸出（進階功能）
ccdebug "Error" --format json -o result.json
ccdebug "Error" --format markdown -o result.md
ccdebug "Error" --format html -o result.html
```

### 進階功能測試

#### 1. 互動模式
```bash
# 啟動互動模式
ccdebug -i

# 在互動模式中：
# 1. 貼上多行錯誤
# 2. 按 Ctrl+D 結束輸入
# 3. 查看分析結果
# 4. 選擇是否複製到剪貼板
```

#### 2. 錯誤類型指定
```bash
# 強制指定錯誤類型
ccdebug "Some generic error" -t python
ccdebug "Another error" --type typescript
```

#### 3. 詳細輸出
```bash
# 顯示詳細分析信息
ccdebug "TypeError: Cannot read property" -v
ccdebug "Error" --verbose
```

#### 4. 自定義 Agent
```bash
# 使用特定的 Claude Code agent
ccdebug "Error" --agent frontend-system-builder
ccdebug "Error" --agent backend-system-architect
```

### 增強型 CLI 測試

#### 1. 批次處理
```bash
# 創建多個測試文件
echo "Error 1" > error1.log
echo "Error 2" > error2.log

# 批次分析
ccdebug batch -f "*.log" --output batch_report.json
```

#### 2. 主題設置
```bash
# 使用不同主題
ccdebug "Error" --theme dark
ccdebug "Error" --theme light

# 設置默認主題
ccdebug config set general.theme dark
```

#### 3. 歷史功能
```bash
# 查看歷史
ccdebug history show --last 10

# 搜索歷史
ccdebug history search "TypeError"

# 查看統計
ccdebug history stats
```

#### 4. 模板管理
```bash
# 列出所有模板
ccdebug template list

# 查看模板詳情
ccdebug template show typescript

# 測試模板
ccdebug template test typescript --sample "TS2322: Type error"
```

#### 5. 插件管理
```bash
# 列出插件
ccdebug plugin list

# 啟用/禁用插件
ccdebug plugin enable stack_trace_analyzer
ccdebug plugin disable git_context
```

### 機器學習功能測試（需要安裝 ML 依賴）

```bash
# 安裝 ML 支援
pip install -e ".[ml]"

# 使用 ML 分類
ccdebug "Complex error message" --ml

# 設置信心閾值
ccdebug "Error" --ml --confidence-threshold 0.8
```

## 🧪 自動化測試

### 運行單元測試
```bash
# 運行所有測試
pytest

# 運行特定測試
pytest tests/test_detector.py
pytest tests/test_cli.py

# 運行測試並顯示覆蓋率
pytest --cov=claudecode_debugger --cov-report=html

# 查看覆蓋率報告
open htmlcov/index.html  # macOS
# 或 xdg-open htmlcov/index.html  # Linux
```

### 運行整合測試
```bash
# 運行整合測試
pytest tests/integration/

# 運行效能測試
pytest tests/performance/ -v
```

### 使用 Make 命令
```bash
# 運行所有測試
make test

# 運行測試並生成覆蓋率報告
make test-coverage

# 檢查代碼品質
make lint

# 格式化代碼
make format

# 完整檢查
make check
```

## 🐛 常見問題排查

### 1. 安裝問題
```bash
# 如果遇到權限問題
pip install --user -e .

# 如果遇到依賴衝突
pip install --upgrade pip
pip install -e . --force-reinstall
```

### 2. 剪貼板問題
```bash
# Linux 需要安裝 xclip
sudo apt-get install xclip

# 測試剪貼板功能
python -c "import pyperclip; pyperclip.copy('test'); print(pyperclip.paste())"
```

### 3. ML 功能問題
```bash
# 檢查 scikit-learn 安裝
python -c "import sklearn; print(sklearn.__version__)"

# 重新安裝 ML 依賴
pip install scikit-learn joblib numpy --upgrade
```

## 📊 效能測試

### 測試大文件處理
```bash
# 創建大型日誌文件
python -c "
for i in range(10000):
    print(f'Error {i}: TypeError: Cannot read property')
" > large_error.log

# 測試處理速度
time ccdebug -f large_error.log
```

### 測試批次處理
```bash
# 創建多個錯誤文件
for i in {1..100}; do
    echo "Error in file $i" > "error_$i.log"
done

# 批次處理測試
time ccdebug batch -f "error_*.log" --parallel
```

## 🎯 完整測試腳本

創建 `test_all_features.sh`：

```bash
#!/bin/bash

echo "=== ClaudeCode-Debugger 完整功能測試 ==="

# 基礎測試
echo -e "\n1. 基礎錯誤檢測測試"
ccdebug "TypeError: Cannot read property 'name' of undefined"

echo -e "\n2. 文件輸入測試"
echo "TS2322: Type error" > test.log
ccdebug -f test.log

echo -e "\n3. 剪貼板測試"
ccdebug "Error" -c

echo -e "\n4. 輸出格式測試"
ccdebug "Error" -o test_output.md

echo -e "\n5. 批次處理測試"
echo "Error 1" > error1.log
echo "Error 2" > error2.log
ccdebug batch -f "error*.log"

echo -e "\n6. 模板測試"
ccdebug template list
ccdebug template test typescript

echo -e "\n7. 配置測試"
ccdebug config show

echo -e "\n=== 測試完成 ==="
```

## 📈 測試報告

測試完成後，請記錄：

1. ✅ 通過的測試項目
2. ❌ 失敗的測試項目
3. ⚠️ 警告或異常行為
4. 💡 改進建議

您可以在 GitHub Issues 中報告問題：
https://github.com/888wing/ClaudeCode-Debugger/issues

## 🎉 下一步

測試成功後，您可以：

1. 開始在實際專案中使用
2. 創建自定義模板
3. 開發自己的插件
4. 貢獻代碼改進

感謝您測試 ClaudeCode-Debugger！