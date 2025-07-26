#!/usr/bin/env python3
"""Test script for enhanced ClaudeCode-Debugger features."""

import os
import subprocess
import sys
from pathlib import Path

# Test error messages
TEST_ERRORS = {
    'python_null': '''
Traceback (most recent call last):
  File "/Users/test/app.py", line 42, in process_data
    result = data.get_value()
AttributeError: 'NoneType' object has no attribute 'get_value'
''',
    
    'javascript_undefined': '''
TypeError: Cannot read property 'name' of undefined
    at UserProfile (/Users/test/components/UserProfile.js:15:23)
    at renderWithHooks (/Users/test/node_modules/react-dom/cjs/react-dom.development.js:14985:18)
    at mountIndeterminateComponent (/Users/test/node_modules/react-dom/cjs/react-dom.development.js:17811:13)
''',
    
    'typescript_type': '''
error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
  src/utils/calculator.ts:25:15
    25   return add(userInput, 10);
                    ~~~~~~~~~
'''
}

# Test commands
TEST_COMMANDS = [
    # Basic test - Chinese
    ('Basic Chinese', [
        'python3', '-m', 'claudecode_debugger.cli_enhanced',
        TEST_ERRORS['python_null'],
        '--lang', 'zh'
    ]),
    
    # Basic test - English
    ('Basic English', [
        'python3', '-m', 'claudecode_debugger.cli_enhanced',
        TEST_ERRORS['python_null'],
        '--lang', 'en'
    ]),
    
    # Stack trace analysis
    ('Stack Analysis', [
        'python3', '-m', 'claudecode_debugger.cli_enhanced',
        TEST_ERRORS['javascript_undefined'],
        '--analyze-stack',
        '--lang', 'en'
    ]),
    
    # With suggestions
    ('With Suggestions', [
        'python3', '-m', 'claudecode_debugger.cli_enhanced',
        TEST_ERRORS['python_null'],
        '--suggest',
        '--lang', 'zh'
    ]),
    
    # Verbose mode
    ('Verbose Mode', [
        'python3', '-m', 'claudecode_debugger.cli_enhanced',
        TEST_ERRORS['typescript_type'],
        '--verbose',
        '--lang', 'en'
    ]),
]

def run_test(name: str, command: list):
    """Run a single test command."""
    print(f"\n{'=' * 60}")
    print(f"Test: {name}")
    print(f"{'=' * 60}")
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("✅ Success")
            print("\nOutput:")
            print(result.stdout)
        else:
            print("❌ Failed")
            print(f"Return code: {result.returncode}")
            print("\nStderr:")
            print(result.stderr)
            print("\nStdout:")
            print(result.stdout)
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_import():
    """Test if modules can be imported."""
    print("Testing imports...")
    try:
        from claudecode_debugger.i18n import get_translator
        print("✅ i18n module imported successfully")
        
        from claudecode_debugger.analyzers import StackTraceAnalyzer, PatternAnalyzer
        print("✅ Analyzer modules imported successfully")
        
        from claudecode_debugger.suggestions import SuggestionEngine
        print("✅ Suggestion engine imported successfully")
        
        # Test translator
        translator = get_translator('zh')
        test_msg = translator('cli.analyzing')
        print(f"✅ Translator test (zh): {test_msg}")
        
        translator_en = get_translator('en')
        test_msg_en = translator_en('cli.analyzing')
        print(f"✅ Translator test (en): {test_msg_en}")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run all tests."""
    print("ClaudeCode-Debugger Enhanced Features Test")
    print("=" * 60)
    
    # First test imports
    if not test_import():
        print("\n❌ Import tests failed. Please check installation.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Running CLI tests...")
    
    # Run each test
    for name, command in TEST_COMMANDS:
        run_test(name, command)
    
    print("\n" + "=" * 60)
    print("All tests completed!")

if __name__ == "__main__":
    main()