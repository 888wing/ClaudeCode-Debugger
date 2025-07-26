#!/usr/bin/env python3
"""Fix remaining type annotation issues."""

import os
import re

def fix_remaining_issues():
    """Fix remaining type issues."""
    
    # Fix plugins/base.py - missing logger import
    base_path = 'claudecode_debugger/plugins/base.py'
    if os.path.exists(base_path):
        with open(base_path, 'r') as f:
            lines = f.readlines()
        
        # Add logger import
        import_added = False
        for i, line in enumerate(lines):
            if 'import logging' in line:
                import_added = True
                break
            elif line.startswith('import') and not import_added:
                lines.insert(i + 1, 'import logging\n')
                import_added = True
                break
        
        # Add logger initialization
        logger_added = False
        for i, line in enumerate(lines):
            if 'from typing import' in line:
                lines.insert(i + 2, '\nlogger = logging.getLogger(__name__)\n')
                logger_added = True
                break
        
        with open(base_path, 'w') as f:
            f.writelines(lines)
        print("Fixed logger in plugins/base.py")
    
    # Fix detector.py issues
    detector_path = 'claudecode_debugger/core/detector.py'
    if os.path.exists(detector_path):
        with open(detector_path, 'r') as f:
            content = f.read()
        
        # Fix the max() issue - already fixed in previous script
        # Fix dict.fromkeys issue - already fixed
        
        with open(detector_path, 'w') as f:
            f.write(content)
    
    # Fix history.py issues
    history_path = 'claudecode_debugger/utils/history.py'
    if os.path.exists(history_path):
        with open(history_path, 'r') as f:
            lines = f.readlines()
        
        # Add return type annotations
        for i, line in enumerate(lines):
            if 'def get_recent_errors(self, limit: int = 10):' in line:
                lines[i] = line.replace('):', ') -> List[Dict[str, Any]]:')
            elif 'def export_history(self, format: str = "json"):' in line:
                lines[i] = line.replace('):', ') -> str:')
            elif 'def import_history(self, data: str, format: str = "json"):' in line:
                lines[i] = line.replace('):', ') -> None:')
        
        with open(history_path, 'w') as f:
            f.writelines(lines)
        print("Fixed return types in history.py")
    
    # Fix plugins/base.py return types
    if os.path.exists(base_path):
        with open(base_path, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            if 'def _load_builtin_plugins(self):' in line:
                lines[i] = line.replace('):', ') -> None:')
            elif 'def _load_plugins_from_dir(self, plugin_dir: Path):' in line:
                lines[i] = line.replace('):', ') -> None:')
            elif 'def _import_plugin(self, plugin_file: Path):' in line:
                lines[i] = line.replace('):', ') -> Optional[Type[Plugin]]:')
            elif 'def disable_plugin(self, plugin_name: str):' in line:
                lines[i] = line.replace('):', ') -> None:')
            elif 'def get_plugin_info(self, plugin_name: str):' in line:
                lines[i] = line.replace('):', ') -> Optional[Dict[str, Any]]:')
        
        with open(base_path, 'w') as f:
            f.writelines(lines)
        print("Fixed return types in plugins/base.py")
    
    # Fix advanced_detector.py issues
    adv_detector_path = 'claudecode_debugger/core/advanced_detector.py'
    if os.path.exists(adv_detector_path):
        with open(adv_detector_path, 'r') as f:
            lines = f.readlines()
        
        # Fix _cache initialization
        for i, line in enumerate(lines):
            if 'self._cache = {}' in line:
                lines[i] = line.replace('self._cache = {}', 'self._cache: Dict[str, List[ErrorMatch]] = {}')
        
        # Fix __post_init__ return type
        for i, line in enumerate(lines):
            if 'def __post_init__(self):' in line:
                lines[i] = line.replace('):', ') -> None:')
        
        # Fix type annotation for category_scores
        for i, line in enumerate(lines):
            if 'category_scores = defaultdict(lambda:' in line:
                lines[i] = '        category_scores: Dict[ErrorCategory, Dict[str, Any]] = defaultdict(lambda: {"score": 0, "matches": [], "info": {}})\n'
        
        with open(adv_detector_path, 'w') as f:
            f.writelines(lines)
        print("Fixed type annotations in advanced_detector.py")

    # Add missing imports
    # Fix advanced_detector.py imports
    if os.path.exists(adv_detector_path):
        with open(adv_detector_path, 'r') as f:
            content = f.read()
        
        # Ensure Dict is imported
        if 'from typing import' in content and 'Dict' not in content.split('from typing import')[1].split('\n')[0]:
            content = content.replace(
                'from typing import Any, List, Optional, Set, Tuple, Union',
                'from typing import Any, Dict, List, Optional, Set, Tuple, Union'
            )
        
        with open(adv_detector_path, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    fix_remaining_issues()
    print("\nRemaining type issues fixed!")