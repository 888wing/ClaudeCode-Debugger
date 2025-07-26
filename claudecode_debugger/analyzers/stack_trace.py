"""Stack trace analyzer for intelligent error analysis."""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from pathlib import Path


@dataclass
class StackFrame:
    """Represents a single frame in a stack trace."""
    file: str
    line: int
    function: str
    code: Optional[str] = None
    is_user_code: bool = True
    language: Optional[str] = None


@dataclass
class StackTraceInfo:
    """Analyzed stack trace information."""
    frames: List[StackFrame]
    error_type: str
    error_message: str
    root_cause_frame: Optional[StackFrame] = None
    language: str = "unknown"
    
    
class StackTraceAnalyzer:
    """Analyze stack traces from various programming languages."""
    
    # Language-specific patterns
    PATTERNS = {
        'python': {
            'frame': r'File "([^"]+)", line (\d+), in (.+)',
            'error': r'^(\w+(?:Error|Exception|Warning)): (.+)$',
            'code': r'^\s*(.+)$',  # Code line after frame
        },
        'javascript': {
            'frame': r'at\s+(?:(.+?)\s+\()?([^:]+):(\d+):(\d+)\)?',
            'error': r'^(\w+(?:Error|Exception)): (.+)$',
            'code': None,
        },
        'typescript': {
            'frame': r'at\s+(?:(.+?)\s+\()?([^:]+):(\d+):(\d+)\)?',
            'error': r'^(\w+(?:Error|Exception)): (.+)$',
            'code': None,
        },
        'java': {
            'frame': r'at\s+(.+?)\(([^:]+):(\d+)\)',
            'error': r'^(.+?Exception|.+?Error): (.+)$',
            'code': None,
        },
        'ruby': {
            'frame': r'from\s+([^:]+):(\d+):in\s+`(.+?)\'',
            'error': r'^(.+?Error|.+?Exception): (.+)$',
            'code': None,
        },
        'go': {
            'frame': r'(.+?):(\d+)\s+\+0x',
            'error': r'^panic: (.+)$',
            'code': None,
        }
    }
    
    # Common library/framework patterns to identify non-user code
    LIBRARY_PATTERNS = [
        r'node_modules',
        r'site-packages',
        r'dist-packages',
        r'vendor/',
        r'\.npm/',
        r'\.cargo/',
        r'\.rustup/',
        r'<frozen',
        r'__pycache__',
    ]
    
    def __init__(self):
        """Initialize the stack trace analyzer."""
        self.library_pattern = re.compile('|'.join(self.LIBRARY_PATTERNS))
        
    def analyze(self, error_text: str) -> Optional[StackTraceInfo]:
        """Analyze a stack trace and extract structured information."""
        language = self._detect_language(error_text)
        
        if language == "unknown":
            return None
            
        frames = self._extract_frames(error_text, language)
        error_type, error_message = self._extract_error_info(error_text, language)
        
        if not frames:
            return None
            
        # Find root cause frame (first user code frame from bottom)
        root_cause = None
        for frame in reversed(frames):
            if frame.is_user_code:
                root_cause = frame
                break
                
        return StackTraceInfo(
            frames=frames,
            error_type=error_type or "UnknownError",
            error_message=error_message or "No error message",
            root_cause_frame=root_cause,
            language=language
        )
    
    def _detect_language(self, error_text: str) -> str:
        """Detect programming language from stack trace format."""
        # Check for language-specific patterns
        if 'File "' in error_text and '", line' in error_text:
            return 'python'
        elif ' at ' in error_text and ('.js:' in error_text or '.ts:' in error_text):
            return 'typescript' if '.ts:' in error_text else 'javascript'
        elif ' at ' in error_text and '.java:' in error_text:
            return 'java'
        elif 'from ' in error_text and ':in `' in error_text:
            return 'ruby'
        elif 'panic:' in error_text and '+0x' in error_text:
            return 'go'
            
        return 'unknown'
    
    def _extract_frames(self, error_text: str, language: str) -> List[StackFrame]:
        """Extract stack frames based on language patterns."""
        frames = []
        patterns = self.PATTERNS.get(language, {})
        frame_pattern = patterns.get('frame')
        
        if not frame_pattern:
            return frames
            
        frame_regex = re.compile(frame_pattern, re.MULTILINE)
        
        for match in frame_regex.finditer(error_text):
            if language == 'python':
                file_path, line_num, function = match.groups()
                frame = StackFrame(
                    file=file_path,
                    line=int(line_num),
                    function=function,
                    is_user_code=not self._is_library_code(file_path),
                    language=language
                )
            elif language in ['javascript', 'typescript']:
                groups = match.groups()
                function = groups[0] or 'anonymous'
                file_path = groups[1]
                line_num = groups[2]
                frame = StackFrame(
                    file=file_path,
                    line=int(line_num),
                    function=function,
                    is_user_code=not self._is_library_code(file_path),
                    language=language
                )
            elif language == 'java':
                function, file_path, line_num = match.groups()
                frame = StackFrame(
                    file=file_path,
                    line=int(line_num),
                    function=function,
                    is_user_code=not self._is_library_code(function),
                    language=language
                )
            else:
                # Generic handling for other languages
                groups = match.groups()
                if len(groups) >= 3:
                    frame = StackFrame(
                        file=groups[0],
                        line=int(groups[1]),
                        function=groups[2] if len(groups) > 2 else 'unknown',
                        is_user_code=not self._is_library_code(groups[0]),
                        language=language
                    )
            
            if frame:
                frames.append(frame)
                
        return frames
    
    def _extract_error_info(self, error_text: str, language: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract error type and message."""
        patterns = self.PATTERNS.get(language, {})
        error_pattern = patterns.get('error')
        
        if not error_pattern:
            return None, None
            
        error_regex = re.compile(error_pattern, re.MULTILINE)
        match = error_regex.search(error_text)
        
        if match:
            return match.groups()
            
        return None, None
    
    def _is_library_code(self, path: str) -> bool:
        """Check if a path represents library/framework code."""
        return bool(self.library_pattern.search(path))
    
    def get_summary(self, trace_info: StackTraceInfo) -> Dict[str, any]:
        """Get a summary of the stack trace analysis."""
        summary = {
            'language': trace_info.language,
            'error_type': trace_info.error_type,
            'error_message': trace_info.error_message,
            'total_frames': len(trace_info.frames),
            'user_frames': sum(1 for f in trace_info.frames if f.is_user_code),
            'library_frames': sum(1 for f in trace_info.frames if not f.is_user_code),
        }
        
        if trace_info.root_cause_frame:
            summary['root_cause'] = {
                'file': trace_info.root_cause_frame.file,
                'line': trace_info.root_cause_frame.line,
                'function': trace_info.root_cause_frame.function,
            }
            
        return summary
    
    def format_frame(self, frame: StackFrame) -> str:
        """Format a single stack frame for display."""
        if frame.language == 'python':
            return f'  File "{frame.file}", line {frame.line}, in {frame.function}'
        elif frame.language in ['javascript', 'typescript']:
            return f'    at {frame.function} ({frame.file}:{frame.line})'
        elif frame.language == 'java':
            return f'    at {frame.function}({frame.file}:{frame.line})'
        else:
            return f'    {frame.file}:{frame.line} in {frame.function}'