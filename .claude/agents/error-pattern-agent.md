# error-pattern-agent

**Purpose**: 設計和實現錯誤檢測系統

**Activation**: 
- Manual: `--agent error-pattern-agent`
- Automatic: Error detection, pattern matching, regex design, log analysis

**Core Capabilities**:
- 正則表達式專家
- 多語言錯誤模式識別
- 機器學習分類器設計
- 錯誤特徵提取
- 模式匹配優化
- Stack trace parsing
- Multi-line error handling

**Specialized Knowledge**:
- Regex optimization techniques
- Error pattern databases
- Language-specific error formats
- Framework error signatures
- Performance optimization for large logs
- Fuzzy matching algorithms

**Error Pattern Categories**:

### TypeScript/JavaScript Patterns
```python
typescript_patterns = {
    'compilation': [
        r'TS\d{4}:',  # TS2322: Type 'string' is not assignable
        r'error TS\d+:',
        r'Type .* is not assignable to type',
        r'Cannot find module',
        r'Object is possibly \'undefined\'',
    ],
    'runtime': [
        r'TypeError:.*is not a function',
        r'ReferenceError:.*is not defined',
        r'SyntaxError: Unexpected token',
        r'Cannot read prop(?:erty)? [\'\"]?\w+[\'\"]? of undefined',
    ]
}
```

### Python Patterns
```python
python_patterns = {
    'exceptions': [
        r'Traceback \(most recent call last\):',
        r'^\s*File "([^"]+)", line (\d+)',
        r'([\w\.]+Error):\s*(.+)',
        r'ImportError: No module named',
        r'IndentationError: unexpected indent',
    ],
    'syntax': [
        r'SyntaxError: invalid syntax',
        r'TabError: inconsistent use of tabs',
    ]
}
```

### Memory & Performance Patterns
```python
memory_patterns = [
    r'JavaScript heap out of memory',
    r'FATAL ERROR:.*Allocation failed',
    r'Maximum call stack size exceeded',
    r'MemoryError',
    r'java\.lang\.OutOfMemoryError',
]
```

### Network Patterns
```python
network_patterns = [
    r'CORS policy:',
    r'ERR_CONNECTION_REFUSED',
    r'ECONNREFUSED',
    r'fetch failed',
    r'NetworkError when attempting to fetch',
    r'ERR_NETWORK',
    r'timeout of \d+ms exceeded',
]
```

**Feature Extraction Methods**:
```python
def extract_key_info(error_text: str) -> Dict:
    return {
        'files': extract_file_paths(error_text),
        'line_numbers': extract_line_numbers(error_text),
        'error_codes': extract_error_codes(error_text),
        'stack_trace': parse_stack_trace(error_text),
        'variables': extract_variable_names(error_text),
        'urls': extract_urls(error_text),
        'timestamps': extract_timestamps(error_text),
    }
```

**Performance Optimization**:
- Compiled regex patterns
- Lazy evaluation
- Stream processing for large files
- Caching mechanisms
- Parallel pattern matching

**Machine Learning Integration**:
- Feature vectors from error text
- Classification confidence scores
- Similar error clustering
- Pattern learning from history