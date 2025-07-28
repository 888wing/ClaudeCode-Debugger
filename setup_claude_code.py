#!/usr/bin/env python3
"""
Claude Code Integration Setup Script for CCDebugger
快速設置 CCDebugger 與 Claude Code 的整合
"""

import os
import json
import sys
from pathlib import Path
import subprocess

def setup_claude_code_integration():
    """設置 Claude Code 整合"""
    
    print("🚀 CCDebugger Claude Code Integration Setup")
    print("-" * 50)
    
    # 1. 檢查 CCDebugger 是否已安裝
    print("\n1. 檢查 CCDebugger 安裝...")
    try:
        import claudecode_debugger
        print("✅ CCDebugger 已安裝")
    except ImportError:
        print("❌ CCDebugger 未安裝")
        if input("是否要安裝 CCDebugger? (y/n): ").lower() == 'y':
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', '.'])
            print("✅ CCDebugger 安裝完成")
        else:
            print("請先安裝 CCDebugger: pip install claudecode-debugger")
            return
    
    # 2. 創建 Claude 配置目錄
    print("\n2. 設置配置文件...")
    claude_dir = Path.home() / '.claude'
    claude_dir.mkdir(exist_ok=True)
    
    # 3. 創建配置文件
    config_file = claude_dir / 'ccdebug.json'
    
    default_config = {
        "autoAnalyze": True,
        "defaultLanguage": "zh",
        "enableSuggestions": True,
        "saveHistory": True,
        "maxHistorySize": 20,
        "monitorMode": False,
        "contextLines": 10,
        "outputFormat": "structured",
        "templates": {
            "python": {
                "enabled": True,
                "customPrompts": []
            },
            "javascript": {
                "enabled": True,
                "customPrompts": []
            }
        }
    }
    
    if config_file.exists():
        print(f"配置文件已存在: {config_file}")
        if input("是否要覆蓋現有配置? (y/n): ").lower() != 'y':
            with open(config_file) as f:
                existing_config = json.load(f)
            # 合併配置
            for key, value in default_config.items():
                if key not in existing_config:
                    existing_config[key] = value
            default_config = existing_config
    
    # 語言選擇
    print("\n3. 選擇預設語言:")
    print("   1. 中文 (zh)")
    print("   2. English (en)")
    choice = input("請選擇 (1/2) [預設: 1]: ").strip() or '1'
    default_config['defaultLanguage'] = 'zh' if choice == '1' else 'en'
    
    # 自動分析
    print("\n4. 是否啟用自動錯誤分析?")
    auto_analyze = input("啟用自動分析? (y/n) [預設: y]: ").strip().lower()
    default_config['autoAnalyze'] = auto_analyze != 'n'
    
    # 監控模式
    print("\n5. 是否啟用監控模式?")
    print("   監控模式會持續監控所有命令輸出")
    monitor_mode = input("啟用監控模式? (y/n) [預設: n]: ").strip().lower()
    default_config['monitorMode'] = monitor_mode == 'y'
    
    # 保存配置
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 配置已保存到: {config_file}")
    
    # 4. 創建快捷命令（可選）
    print("\n6. 創建快捷命令...")
    
    # 創建 ccdebug 包裝腳本
    wrapper_script = """#!/usr/bin/env python3
# CCDebugger Claude Code Wrapper
import sys
from claude_code_ccdebug import CCDebugCommand

if __name__ == "__main__":
    command = " ".join(sys.argv)
    ccdebug = CCDebugCommand()
    result = ccdebug.execute(command)
    print(result)
"""
    
    bin_dir = Path.home() / '.local' / 'bin'
    bin_dir.mkdir(exist_ok=True, parents=True)
    
    ccdebug_script = bin_dir / 'ccdebug-claude'
    with open(ccdebug_script, 'w') as f:
        f.write(wrapper_script)
    
    ccdebug_script.chmod(0o755)
    
    # 5. 測試整合
    print("\n7. 測試整合...")
    test_code = """
from claude_code_integration import claude_code_hook

# 測試錯誤
test_output = '''
Traceback (most recent call last):
  File "test.py", line 1, in <module>
    undefined_function()
NameError: name 'undefined_function' is not defined
'''

result = claude_code_hook(test_output, "python test.py")
if result:
    print("✅ 整合測試成功!")
    print("\\n預覽:")
    print(result[:200] + "...")
else:
    print("❌ 整合測試失敗")
"""
    
    try:
        exec(test_code)
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
    
    # 6. 使用說明
    print("\n" + "="*50)
    print("🎉 設置完成！")
    print("\n使用方法:")
    print("1. 在 Claude Code 中正常執行命令")
    print("2. 遇到錯誤時，CCDebugger 會自動分析")
    print("3. 使用 'ccdebug --last' 分析最後的錯誤")
    print("4. 使用 'ccdebug --help' 查看更多選項")
    
    if default_config['monitorMode']:
        print("\n監控模式已啟用，所有錯誤都會被自動分析。")
    
    print(f"\n配置文件位置: {config_file}")
    print("修改配置後會立即生效。")
    
    # 7. 創建示例代碼
    if input("\n是否創建示例代碼? (y/n): ").lower() == 'y':
        example_file = Path.cwd() / 'claude_code_example.py'
        example_code = '''#!/usr/bin/env python3
"""
CCDebugger Claude Code Integration Example
這是一個展示 CCDebugger 如何在 Claude Code 中工作的示例
"""

# 示例 1: 基本錯誤
def test_basic_error():
    """測試基本的 NameError"""
    print("測試 1: NameError")
    undefined_variable  # 這會觸發 CCDebugger

# 示例 2: 類型錯誤
def test_type_error():
    """測試 TypeError"""
    print("測試 2: TypeError")
    "string" + 123  # 這會觸發 CCDebugger

# 示例 3: 屬性錯誤
def test_attribute_error():
    """測試 AttributeError"""
    print("測試 3: AttributeError")
    data = None
    data.process()  # 這會觸發 CCDebugger

# 示例 4: 索引錯誤
def test_index_error():
    """測試 IndexError"""
    print("測試 4: IndexError")
    items = [1, 2, 3]
    print(items[10])  # 這會觸發 CCDebugger

if __name__ == "__main__":
    print("CCDebugger Claude Code 整合示例")
    print("-" * 40)
    print("運行任何一個測試函數都會觸發 CCDebugger 自動分析")
    print("例如: test_basic_error()")
    print()
    print("提示: CCDebugger 會自動偵測錯誤並提供解決方案！")
'''
        
        with open(example_file, 'w') as f:
            f.write(example_code)
        
        print(f"\n✅ 示例代碼已創建: {example_file}")
        print("在 Claude Code 中運行示例來體驗 CCDebugger！")

if __name__ == "__main__":
    try:
        setup_claude_code_integration()
    except KeyboardInterrupt:
        print("\n\n設置已取消。")
    except Exception as e:
        print(f"\n❌ 設置過程中出錯: {e}")
        sys.exit(1)