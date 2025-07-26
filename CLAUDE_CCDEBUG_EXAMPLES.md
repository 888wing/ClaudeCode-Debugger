# /ccdebug 實際使用範例集

## 🎯 真實場景範例

### 1. Python AttributeError 調試

**場景**: Django 開發中遇到 NoneType 錯誤

```python
# 執行命令
$ python manage.py runserver

# 錯誤輸出
Traceback (most recent call last):
  File "views.py", line 25, in get_user_profile
    return user.profile.avatar_url
AttributeError: 'NoneType' object has no attribute 'profile'
```

**Claude Code 對話**:
```
User: python manage.py runserver
Claude: [顯示錯誤]

User: /ccdebug --last --zh --deep
Claude: 
🚨 Python 錯誤 - HIGH 優先級
檢測到: AttributeError - NoneType 錯誤

🎯 智能建議：
1. 添加 None 檢查：
   ```python
   if user and hasattr(user, 'profile'):
       return user.profile.avatar_url
   return None
   ```

2. 使用 Django 的 get_or_none：
   ```python
   profile = getattr(user, 'profile', None)
   if profile:
       return profile.avatar_url
   ```

3. 確保用戶已登入：
   ```python
   @login_required
   def get_user_profile(request):
       # user 保證不為 None
   ```

根本原因: user 變數為 None，可能是未登入或查詢失敗
```

### 2. React TypeError 調試

**場景**: React 組件中的 undefined 錯誤

```javascript
// 錯誤
TypeError: Cannot read property 'map' of undefined
    at TodoList (TodoList.jsx:15:19)
    at renderWithHooks (react-dom.development.js:14985:18)
```

**Claude Code 對話**:
```
User: npm start
Claude: [顯示 React 錯誤]

User: /ccdebug --last --zh --full --context TodoList.jsx
Claude:
🚨 JavaScript 錯誤 - HIGH 優先級
錯誤位置: TodoList.jsx:15

代碼上下文：
13 | function TodoList({ todos }) {
14 |   return (
15 |     <ul>{todos.map(todo => <li>{todo.text}</li>)}</ul>
     |               ^^^^^ 錯誤發生在這裡
16 |   );
17 | }

🎯 解決方案：

1. 添加預設值：
   ```jsx
   function TodoList({ todos = [] }) {
     return (
       <ul>{todos.map(todo => <li key={todo.id}>{todo.text}</li>)}</ul>
     );
   }
   ```

2. 條件渲染：
   ```jsx
   function TodoList({ todos }) {
     if (!todos || todos.length === 0) {
       return <p>No todos yet!</p>;
     }
     return (
       <ul>{todos.map(todo => <li key={todo.id}>{todo.text}</li>)}</ul>
     );
   }
   ```

3. 使用可選鏈：
   ```jsx
   <ul>{todos?.map(todo => <li key={todo.id}>{todo.text}</li>) || null}</ul>
   ```

提示: 別忘了加上 key 屬性！
```

### 3. TypeScript 類型錯誤

**場景**: TypeScript 編譯錯誤

```typescript
// 錯誤
error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
  src/utils/calculator.ts:10:15
  10   return add(userInput, 10);
                  ~~~~~~~~~
```

**Claude Code 對話**:
```
User: npm run build
Claude: [顯示 TypeScript 錯誤]

User: /ccdebug --last --zh --context calculator.ts
Claude:
🚨 TypeScript 錯誤 - MEDIUM 優先級
類型不匹配: string vs number

代碼分析：
```typescript
// calculator.ts
function add(a: number, b: number): number {
  return a + b;
}

// 問題代碼
const userInput = document.getElementById('input').value; // string
return add(userInput, 10); // ❌ 類型錯誤
```

🎯 修復方案：

1. 轉換類型：
   ```typescript
   const userInput = document.getElementById('input').value;
   return add(Number(userInput), 10);
   // 或
   return add(parseInt(userInput, 10), 10);
   ```

2. 類型守衛：
   ```typescript
   const userInput = document.getElementById('input').value;
   const num = Number(userInput);
   if (!isNaN(num)) {
     return add(num, 10);
   }
   throw new Error('Invalid number input');
   ```

3. 更新函數簽名：
   ```typescript
   function add(a: number | string, b: number): number {
     return Number(a) + b;
   }
   ```

最佳實踐: 在用戶輸入處進行驗證和轉換
```

### 4. Node.js Module 錯誤

**場景**: Node.js 依賴問題

```bash
Error: Cannot find module 'express'
Require stack:
- /Users/project/server.js
```

**Claude Code 對話**:
```
User: node server.js
Claude: [顯示模組錯誤]

User: /ccdebug --last --zh
Claude:
🚨 Node.js 錯誤 - HIGH 優先級
模組未找到: express

🎯 快速修復：

1. 安裝缺失的套件：
   ```bash
   npm install express
   # 或
   yarn add express
   ```

2. 檢查 package.json：
   ```json
   {
     "dependencies": {
       "express": "^4.18.0"
     }
   }
   ```

3. 如果已安裝但仍報錯：
   ```bash
   # 刪除 node_modules 重新安裝
   rm -rf node_modules package-lock.json
   npm install
   ```

4. 檢查導入路徑：
   ```javascript
   // ❌ 錯誤
   const express = require('Express');
   
   // ✅ 正確
   const express = require('express');
   ```

可能原因：
- 未執行 npm install
- 大小寫錯誤
- 在錯誤的目錄執行
```

### 5. 異步錯誤處理

**場景**: Promise rejection 未處理

```javascript
UnhandledPromiseRejectionWarning: TypeError: Cannot read property 'data' of undefined
    at fetchUserData (api.js:15:28)
```

**Claude Code 對話**:
```
User: /ccdebug --last --zh --deep
Claude:
🚨 JavaScript 異步錯誤 - HIGH 優先級
未處理的 Promise 拒絕

問題代碼分析：
```javascript
// 可能的問題代碼
async function fetchUserData(userId) {
  const response = await fetch(`/api/users/${userId}`);
  return response.data; // ❌ fetch 返回的是 Response 對象
}
```

🎯 修復方案：

1. 正確處理 fetch：
   ```javascript
   async function fetchUserData(userId) {
     try {
       const response = await fetch(`/api/users/${userId}`);
       if (!response.ok) {
         throw new Error(`HTTP error! status: ${response.status}`);
       }
       const data = await response.json();
       return data;
     } catch (error) {
       console.error('Failed to fetch user:', error);
       throw error;
     }
   }
   ```

2. 使用 axios（如果已安裝）：
   ```javascript
   async function fetchUserData(userId) {
     try {
       const response = await axios.get(`/api/users/${userId}`);
       return response.data; // ✅ axios 自動解析 JSON
     } catch (error) {
       if (error.response) {
         console.error('Server error:', error.response.status);
       } else {
         console.error('Network error:', error.message);
       }
       throw error;
     }
   }
   ```

3. 全局錯誤處理：
   ```javascript
   process.on('unhandledRejection', (reason, promise) => {
     console.error('Unhandled Rejection at:', promise, 'reason:', reason);
   });
   ```

關鍵點：
- fetch 需要檢查 response.ok
- 需要調用 response.json() 獲取數據
- 始終使用 try-catch 處理異步錯誤
```

## 📚 最佳實踐總結

### 1. 錯誤預防

```javascript
// ❌ 容易出錯
function processUser(user) {
  return user.profile.settings.theme;
}

// ✅ 安全的寫法
function processUser(user) {
  return user?.profile?.settings?.theme || 'default';
}
```

### 2. 錯誤處理模式

```python
# Python
try:
    result = risky_operation()
except SpecificError as e:
    # 使用 /ccdebug 分析具體錯誤
    logger.error(f"Operation failed: {e}")
    raise

# JavaScript/TypeScript
try {
  const result = await riskyOperation();
} catch (error) {
  // 記錄錯誤供 /ccdebug 分析
  console.error('Operation failed:', error);
  throw error;
}
```

### 3. 調試工作流程

1. **捕獲錯誤** → 2. **使用 /ccdebug 分析** → 3. **應用建議的修復** → 4. **測試驗證** → 5. **添加預防措施**

### 4. Claude Code 整合技巧

```
# 設定別名加速工作流程
alias ccerr='/ccdebug --last --zh --deep'
alias ccquick='/ccdebug --last --zh --quick'
alias ccfull='/ccdebug --last --zh --full --context'

# 在項目中設定 .ccdebugrc
{
  "defaultLanguage": "zh",
  "autoSuggest": true,
  "frameworks": ["django", "react"],
  "customPatterns": {
    "api_error": {
      "pattern": "API Error:",
      "suggestion": "檢查 API 端點和認證"
    }
  }
}
```

## 🎉 結語

通過這些實際範例，您可以看到 /ccdebug 如何在各種場景下提供智能的調試支援。記住：

1. **快速響應** - 錯誤發生時立即使用 /ccdebug
2. **選擇合適模式** - quick/deep/full 根據需要選擇
3. **利用上下文** - 使用 --context 獲得更準確的建議
4. **保存重要分析** - 使用 --save 記錄複雜問題

讓調試變得更簡單、更智能！ 🚀