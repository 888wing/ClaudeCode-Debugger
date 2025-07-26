#!/usr/bin/env python3
"""Fix CI errors for ClaudeCode-Debugger project."""

import os
import re
import subprocess
from pathlib import Path

def run_command(cmd):
    """Run a command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def fix_imports():
    """Fix missing imports in all Python files."""
    fixes = {
        'claudecode_debugger/utils/formatters.py': [
            ('from typing import', 'from typing import Any, Dict, List, Optional, Union')
        ],
        'claudecode_debugger/utils/config.py': [
            ('from typing import', 'from typing import Any, Dict, List, Optional, Union')
        ],
        'claudecode_debugger/cli.py': [
            ('from rich.syntax import Syntax', '# from rich.syntax import Syntax  # Unused import')
        ],
        'claudecode_debugger/cli_enhanced.py': [
            ('import json', '# import json  # Unused import'),
            ('from typing import Any, Dict, List, Optional', 'from typing import Any, Dict, Optional'),
            ('import configparser', '# import configparser  # Unused import'),
            ('from rich.live import Live', '# from rich.live import Live  # Unused import'),
            ('from rich.columns import Columns', '# from rich.columns import Columns  # Unused import')
        ]
    }
    
    for filepath, replacements in fixes.items():
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            
            for old, new in replacements:
                content = content.replace(old, new)
            
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Fixed imports in {filepath}")

def fix_whitespace():
    """Fix whitespace issues in all Python files."""
    for root, dirs, files in os.walk('claudecode_debugger'):
        # Skip __pycache__ directories
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    lines = f.readlines()
                
                # Fix whitespace issues
                fixed_lines = []
                for line in lines:
                    # Remove trailing whitespace
                    line = line.rstrip() + '\n'
                    # Fix blank lines with whitespace
                    if line.strip() == '':
                        line = '\n'
                    fixed_lines.append(line)
                
                # Ensure file ends with newline
                if fixed_lines and not fixed_lines[-1].endswith('\n'):
                    fixed_lines[-1] += '\n'
                elif not fixed_lines:
                    fixed_lines = ['\n']
                
                with open(filepath, 'w') as f:
                    f.writelines(fixed_lines)

def fix_line_length():
    """Fix lines that are too long."""
    max_length = 88
    
    for root, dirs, files in os.walk('claudecode_debugger'):
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    lines = f.readlines()
                
                fixed_lines = []
                for line in lines:
                    if len(line.rstrip()) > max_length and not line.strip().startswith('#'):
                        # Simple fix for long lines - just add a comment
                        if 'error:' in line or 'Error' in line:
                            # Keep error messages intact
                            fixed_lines.append(line)
                        else:
                            # Try to break at logical points
                            if ',' in line and len(line) > max_length:
                                # Find a good break point
                                parts = line.split(',')
                                current_line = parts[0]
                                for i, part in enumerate(parts[1:]):
                                    if len(current_line + ',' + part) <= max_length:
                                        current_line += ',' + part
                                    else:
                                        fixed_lines.append(current_line + ',\n')
                                        current_line = '    ' + part.strip()
                                fixed_lines.append(current_line + '\n')
                            else:
                                fixed_lines.append(line)
                    else:
                        fixed_lines.append(line)
                
                with open(filepath, 'w') as f:
                    f.writelines(fixed_lines)

def add_type_annotations():
    """Add missing type annotations."""
    type_fixes = {
        'claudecode_debugger/core/detector.py': [
            ('def __init__(self):', 'def __init__(self) -> None:'),
        ],
        'claudecode_debugger/utils/history.py': [
            ('def __init__(self, db_path: Optional[Path] = None):', 
             'def __init__(self, db_path: Optional[Path] = None) -> None:'),
            ('def _init_db(self):', 'def _init_db(self) -> None:'),
            ('def close(self):', 'def close(self) -> None:'),
        ],
        'claudecode_debugger/plugins/base.py': [
            ('def __init__(self, plugin_dirs: Optional[List[Path]] = None):', 
             'def __init__(self, plugin_dirs: Optional[List[Path]] = None) -> None:'),
            ('def load_builtin_plugins(self):', 'def load_builtin_plugins(self) -> None:'),
            ('def load_user_plugins(self):', 'def load_user_plugins(self) -> None:'),
            ('def enable_plugin(self, plugin_name: str):', 
             'def enable_plugin(self, plugin_name: str) -> None:'),
        ]
    }
    
    for filepath, replacements in type_fixes.items():
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            
            for old, new in replacements:
                content = content.replace(old, new)
            
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Added type annotations to {filepath}")

def main():
    """Run all fixes."""
    print("Fixing CI errors...")
    
    # Fix imports
    fix_imports()
    
    # Fix whitespace
    fix_whitespace()
    
    # Fix line length
    fix_line_length()
    
    # Add type annotations
    add_type_annotations()
    
    # Run black to format everything properly
    print("\nRunning black formatter...")
    run_command("python3 -m black claudecode_debugger tests --line-length 88")
    
    # Run isort to sort imports
    print("\nRunning isort...")
    run_command("python3 -m isort claudecode_debugger tests --profile black")
    
    print("\nDone! CI errors should be fixed.")

if __name__ == "__main__":
    main()