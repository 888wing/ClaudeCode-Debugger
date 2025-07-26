"""Stack trace analyzer plugin for ClaudeCode-Debugger."""

import re
from typing import Dict, Any, List, Tuple, Optional
from .base import Plugin


class StackTraceAnalyzer(Plugin):
    """Analyzes stack traces to extract key information."""
    
    def __init__(self):
        """Initialize stack trace analyzer."""
        super().__init__()
        
        # Common stack trace patterns
        self.patterns = {
            'python': {
                'frame': r'File "([^"]+)", line (\d+), in (.+)',
                'error': r'^(\w+(?:Error|Exception|Warning)): (.+)$',
                'module': r'File "([^"]+[/\\]site-packages[/\\][^"]+)"',
            },
            'javascript': {
                'frame': r'at\s+(?:(.+?)\s+\()?([^:]+):(\d+):(\d+)\)?',
                'error': r'^(\w+(?:Error|Exception)): (.+)$',
                'module': r'node_modules[/\\]([^/\\]+)',
            },
            'java': {
                'frame': r'at\s+([\w.$]+)\(([^:]+):(\d+)\)',
                'error': r'^([\w.]+(?:Exception|Error)): (.+)$',
                'package': r'^([\w.]+)\.[\w$]+$',
            },
            'typescript': {
                'frame': r'at\s+(?:(.+?)\s+\()?([^:]+):(\d+):(\d+)\)?',
                'error': r'^(\w+(?:Error|Exception)): (.+)$|error TS\d+: (.+)',
                'module': r'node_modules[/\\]([^/\\]+)',
            }
        }
        
    def get_description(self) -> str:
        """Return plugin description."""
        return "Analyzes stack traces to identify error flow, problematic modules, and root causes"
        
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze stack trace in error content."""
        error_content = data.get('error_content', '')
        error_type = data.get('error_type', 'unknown')
        
        results = {
            'has_stack_trace': False,
            'frames': [],
            'error_origin': None,
            'external_dependencies': [],
            'call_sequence': [],
            'deepest_user_code': None,
            'error_propagation': [],
        }
        
        # Detect language-specific patterns
        patterns = self.patterns.get(error_type, self.patterns.get('python'))
        
        # Extract frames
        frames = self._extract_frames(error_content, patterns)
        if frames:
            results['has_stack_trace'] = True
            results['frames'] = frames
            results['call_sequence'] = self._build_call_sequence(frames)
            results['error_origin'] = self._find_error_origin(frames)
            results['external_dependencies'] = self._find_external_deps(frames, patterns)
            results['deepest_user_code'] = self._find_deepest_user_code(frames)
            results['error_propagation'] = self._analyze_propagation(frames)
            
        # Extract error message
        error_info = self._extract_error_info(error_content, patterns)
        if error_info:
            results['error_class'] = error_info[0]
            results['error_message'] = error_info[1]
            
        # Analyze patterns
        results['patterns'] = self._analyze_patterns(frames)
        
        return results
        
    def _extract_frames(self, content: str, patterns: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract stack trace frames."""
        frames = []
        frame_pattern = patterns.get('frame')
        
        if not frame_pattern:
            return frames
            
        for match in re.finditer(frame_pattern, content, re.MULTILINE):
            frame_data = {
                'file': match.group(1) if match.lastindex >= 1 else match.group(2),
                'line': int(match.group(2) if match.lastindex >= 2 else match.group(3)),
                'function': match.group(3) if match.lastindex >= 3 else 'unknown',
                'raw': match.group(0)
            }
            
            # Add column for JS/TS
            if match.lastindex >= 4:
                frame_data['column'] = int(match.group(4))
                
            frames.append(frame_data)
            
        return frames
        
    def _extract_error_info(self, content: str, patterns: Dict[str, str]) -> Optional[Tuple[str, str]]:
        """Extract error class and message."""
        error_pattern = patterns.get('error')
        
        if not error_pattern:
            return None
            
        # Look for error at the end of content (usually where it appears)
        lines = content.strip().split('\n')
        for line in reversed(lines[-10:]):  # Check last 10 lines
            match = re.match(error_pattern, line.strip())
            if match:
                error_class = match.group(1)
                error_message = match.group(2) if match.lastindex >= 2 else match.group(3)
                return (error_class, error_message)
                
        return None
        
    def _build_call_sequence(self, frames: List[Dict[str, Any]]) -> List[str]:
        """Build call sequence from frames."""
        sequence = []
        
        for frame in reversed(frames):  # Start from bottom of stack
            func_name = frame['function']
            if func_name and func_name != 'unknown':
                sequence.append(func_name)
                
        return sequence
        
    def _find_error_origin(self, frames: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the origin of the error (usually the deepest frame)."""
        if frames:
            return frames[0]  # First frame is usually where error occurred
        return None
        
    def _find_external_deps(self, frames: List[Dict[str, Any]], patterns: Dict[str, str]) -> List[str]:
        """Find external dependencies involved in the error."""
        deps = set()
        module_pattern = patterns.get('module') or patterns.get('package')
        
        if not module_pattern:
            return []
            
        for frame in frames:
            file_path = frame['file']
            match = re.search(module_pattern, file_path)
            if match:
                deps.add(match.group(1))
                
        return sorted(list(deps))
        
    def _find_deepest_user_code(self, frames: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the deepest user code frame (excluding libraries)."""
        exclude_patterns = [
            r'site-packages',
            r'node_modules',
            r'<frozen',
            r'\.pyenv',
            r'\.virtualenv',
            r'\.venv',
            r'/usr/lib',
            r'/System/Library',
        ]
        
        for frame in frames:
            file_path = frame['file']
            is_library = any(re.search(pattern, file_path) for pattern in exclude_patterns)
            
            if not is_library:
                return frame
                
        return None
        
    def _analyze_propagation(self, frames: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Analyze how error propagated through the stack."""
        propagation = []
        
        for i in range(len(frames) - 1):
            current = frames[i]
            next_frame = frames[i + 1]
            
            propagation.append({
                'from': f"{current['function']} ({current['file']}:{current['line']})",
                'to': f"{next_frame['function']} ({next_frame['file']}:{next_frame['line']})",
                'type': 'direct_call'
            })
            
        return propagation
        
    def _analyze_patterns(self, frames: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in the stack trace."""
        patterns = {
            'recursion_detected': False,
            'async_error': False,
            'callback_hell': False,
            'deep_nesting': False,
        }
        
        if not frames:
            return patterns
            
        # Check for recursion
        functions = [f['function'] for f in frames if f['function'] != 'unknown']
        if len(functions) != len(set(functions)):
            patterns['recursion_detected'] = True
            
        # Check for async patterns
        async_keywords = ['async', 'await', 'promise', 'then', 'catch', 'callback']
        for frame in frames:
            if any(keyword in frame['function'].lower() for keyword in async_keywords):
                patterns['async_error'] = True
                break
                
        # Check for callback hell
        callback_count = sum(1 for f in frames if 'callback' in f['function'].lower())
        if callback_count > 3:
            patterns['callback_hell'] = True
            
        # Check for deep nesting
        if len(frames) > 20:
            patterns['deep_nesting'] = True
            
        return patterns