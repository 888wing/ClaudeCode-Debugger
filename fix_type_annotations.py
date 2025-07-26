#!/usr/bin/env python3
"""Fix type annotation issues for ClaudeCode-Debugger project."""

import os
import re

def fix_type_annotations():
    """Fix common type annotation issues."""
    
    # Fix missing return type annotations
    fixes = {
        'claudecode_debugger/utils/history.py': [
            ('def clear_history(self):', 'def clear_history(self) -> None:'),
            ('def __del__(self):', 'def __del__(self) -> None:'),
        ],
        'claudecode_debugger/plugins/base.py': [
            ('def __init__(self):', 'def __init__(self) -> None:'),
            ('def initialize(self):', 'def initialize(self) -> None:'),
            ('def register(self, plugin: Type[Plugin]):', 'def register(self, plugin: Type[Plugin]) -> None:'),
            ('def load_plugins(self):', 'def load_plugins(self) -> None:'),
            ('def unload_plugin(self, plugin_name: str):', 'def unload_plugin(self, plugin_name: str) -> None:'),
        ],
        'claudecode_debugger/core/advanced_detector.py': [
            ('def _initialize_categories(self):', 'def _initialize_categories(self) -> None:'),
        ],
        'claudecode_debugger/core/detector.py': [
            # Fix set type annotations
            ('line_numbers = set()', 'line_numbers: set[int] = set()'),
            ('codes = set()', 'codes: set[str] = set()'),
            ('messages = set()', 'messages: set[str] = set()'),
        ],
    }
    
    for filepath, replacements in fixes.items():
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            
            for old, new in replacements:
                content = content.replace(old, new)
            
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Fixed type annotations in {filepath}")
    
    # Fix specific issues
    # Fix clipboard.py return type
    clipboard_path = 'claudecode_debugger/utils/clipboard.py'
    if os.path.exists(clipboard_path):
        with open(clipboard_path, 'r') as f:
            content = f.read()
        
        # Fix the return statement
        content = re.sub(
            r'return pyperclip\.paste\(\)',
            'return str(pyperclip.paste())',
            content
        )
        
        with open(clipboard_path, 'w') as f:
            f.write(content)
        print(f"Fixed return type in {clipboard_path}")
    
    # Fix history.py type issue
    history_path = 'claudecode_debugger/utils/history.py'
    if os.path.exists(history_path):
        with open(history_path, 'r') as f:
            lines = f.readlines()
        
        # Fix line 120 - convert int to str
        for i, line in enumerate(lines):
            if 'sessions.append(row[0])' in line and 'row[0]' in line:
                lines[i] = line.replace('sessions.append(row[0])', 'sessions.append(str(row[0]))')
        
        with open(history_path, 'w') as f:
            f.writelines(lines)
        print(f"Fixed type conversion in {history_path}")
    
    # Fix detector.py max() issue
    detector_path = 'claudecode_debugger/core/detector.py'
    if os.path.exists(detector_path):
        with open(detector_path, 'r') as f:
            content = f.read()
        
        # Fix the max() call issue
        content = re.sub(
            r'max\(confidences, key=confidences\.get\)',
            'max(confidences.keys(), key=lambda k: confidences[k])',
            content
        )
        
        # Fix dict.fromkeys() issue
        content = re.sub(
            r'dict\.fromkeys\(self\.patterns\.keys\(\)\)',
            'dict.fromkeys(list(self.patterns.keys()))',
            content
        )
        
        with open(detector_path, 'w') as f:
            f.write(content)
        print(f"Fixed max() and fromkeys() issues in {detector_path}")
    
    # Fix plugins/base.py module loading
    base_path = 'claudecode_debugger/plugins/base.py'
    if os.path.exists(base_path):
        with open(base_path, 'r') as f:
            content = f.read()
        
        # Add type checking for module_from_spec
        content = re.sub(
            r'module = importlib\.util\.module_from_spec\(spec\)',
            '''if spec is None:
                logger.error(f"Could not load spec for {plugin_file}")
                continue
            module = importlib.util.module_from_spec(spec)''',
            content
        )
        
        # Add type checking for spec.loader
        content = re.sub(
            r'spec\.loader\.exec_module\(module\)',
            '''if spec.loader is None:
                logger.error(f"No loader found for {plugin_file}")
                continue
            spec.loader.exec_module(module)''',
            content
        )
        
        with open(base_path, 'w') as f:
            f.write(content)
        print(f"Fixed module loading issues in {base_path}")
    
    # Fix advanced_detector.py return type
    adv_detector_path = 'claudecode_debugger/core/advanced_detector.py'
    if os.path.exists(adv_detector_path):
        with open(adv_detector_path, 'r') as f:
            content = f.read()
        
        # Fix the return type issue
        content = re.sub(
            r'return pattern\.search\(text\)',
            'match = pattern.search(text)\n        return match',
            content
        )
        
        with open(adv_detector_path, 'w') as f:
            f.write(content)
        print(f"Fixed return type in {adv_detector_path}")

if __name__ == "__main__":
    fix_type_annotations()
    print("\nType annotation fixes complete!")