"""Code context analyzer for understanding error surroundings."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CodeContext:
    """Represents code context around an error."""
    file_path: str
    error_line: int
    context_lines: List[Tuple[int, str]]  # (line_number, content)
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    imports: List[str] = None
    variables: List[str] = None
    

class CodeContextAnalyzer:
    """Analyze code context around errors."""
    
    # Language detection patterns
    LANGUAGE_PATTERNS = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.php': 'php',
    }
    
    # Function detection patterns by language
    FUNCTION_PATTERNS = {
        'python': r'^\s*def\s+(\w+)\s*\(',
        'javascript': r'^\s*(?:async\s+)?function\s+(\w+)\s*\(|^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(.*?\)\s*=>',
        'typescript': r'^\s*(?:async\s+)?function\s+(\w+)\s*\(|^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(.*?\)\s*=>',
        'java': r'^\s*(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(',
        'go': r'^\s*func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(',
    }
    
    # Class detection patterns by language
    CLASS_PATTERNS = {
        'python': r'^\s*class\s+(\w+)',
        'javascript': r'^\s*class\s+(\w+)',
        'typescript': r'^\s*class\s+(\w+)',
        'java': r'^\s*(?:public|private|protected)?\s*class\s+(\w+)',
        'csharp': r'^\s*(?:public|private|protected)?\s*class\s+(\w+)',
    }
    
    # Import detection patterns
    IMPORT_PATTERNS = {
        'python': r'^\s*(?:from\s+\S+\s+)?import\s+(.+)',
        'javascript': r'^\s*import\s+.*?from\s+[\'"](.+?)[\'"]',
        'typescript': r'^\s*import\s+.*?from\s+[\'"](.+?)[\'"]',
        'java': r'^\s*import\s+(.+);',
        'go': r'^\s*import\s+(?:\(|")(.+?)(?:\)|")',
    }
    
    def __init__(self, context_window: int = 5):
        """Initialize with context window size."""
        self.context_window = context_window
        
    def analyze_file_context(self, file_path: str, error_line: int) -> Optional[CodeContext]:
        """Analyze context around an error in a file."""
        path = Path(file_path)
        
        if not path.exists() or not path.is_file():
            return None
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
            return None
            
        if error_line < 1 or error_line > len(lines):
            return None
            
        # Detect language
        language = self._detect_language(file_path)
        
        # Extract context lines
        start_line = max(1, error_line - self.context_window)
        end_line = min(len(lines) + 1, error_line + self.context_window + 1)
        
        context_lines = [
            (i, lines[i-1].rstrip()) 
            for i in range(start_line, end_line)
        ]
        
        # Find enclosing function/class
        function_name = self._find_enclosing_function(lines, error_line, language)
        class_name = self._find_enclosing_class(lines, error_line, language)
        
        # Extract imports
        imports = self._extract_imports(lines, language)
        
        # Extract variables in scope
        variables = self._extract_variables(lines, error_line, language)
        
        return CodeContext(
            file_path=file_path,
            error_line=error_line,
            context_lines=context_lines,
            function_name=function_name,
            class_name=class_name,
            imports=imports,
            variables=variables
        )
    
    def _detect_language(self, file_path: str) -> str:
        """Detect language from file extension."""
        ext = Path(file_path).suffix.lower()
        return self.LANGUAGE_PATTERNS.get(ext, 'unknown')
    
    def _find_enclosing_function(self, lines: List[str], error_line: int, language: str) -> Optional[str]:
        """Find the function containing the error line."""
        pattern = self.FUNCTION_PATTERNS.get(language)
        if not pattern:
            return None
            
        regex = re.compile(pattern)
        
        # Search backwards for function definition
        for i in range(error_line - 1, -1, -1):
            match = regex.match(lines[i])
            if match:
                # Get first non-None group (handles multiple capture groups)
                for group in match.groups():
                    if group:
                        return group
                        
        return None
    
    def _find_enclosing_class(self, lines: List[str], error_line: int, language: str) -> Optional[str]:
        """Find the class containing the error line."""
        pattern = self.CLASS_PATTERNS.get(language)
        if not pattern:
            return None
            
        regex = re.compile(pattern)
        
        # Search backwards for class definition
        for i in range(error_line - 1, -1, -1):
            match = regex.match(lines[i])
            if match:
                return match.group(1)
                
        return None
    
    def _extract_imports(self, lines: List[str], language: str) -> List[str]:
        """Extract import statements from the file."""
        pattern = self.IMPORT_PATTERNS.get(language)
        if not pattern:
            return []
            
        regex = re.compile(pattern)
        imports = []
        
        for line in lines:
            match = regex.match(line)
            if match:
                imports.append(match.group(1).strip())
                
        return imports
    
    def _extract_variables(self, lines: List[str], error_line: int, language: str) -> List[str]:
        """Extract variable names in scope around error."""
        variables = set()
        
        # Simple variable detection patterns
        var_patterns = {
            'python': r'^\s*(\w+)\s*=',
            'javascript': r'^\s*(?:const|let|var)\s+(\w+)\s*=',
            'typescript': r'^\s*(?:const|let|var)\s+(\w+)\s*[:=]',
            'java': r'^\s*(?:\w+)\s+(\w+)\s*=',
        }
        
        pattern = var_patterns.get(language)
        if not pattern:
            return []
            
        regex = re.compile(pattern)
        
        # Look for variables in the function scope
        start = max(0, error_line - 20)
        end = min(len(lines), error_line + 5)
        
        for i in range(start, end):
            match = regex.match(lines[i])
            if match:
                variables.add(match.group(1))
                
        return list(variables)
    
    def format_context(self, context: CodeContext) -> str:
        """Format code context for display."""
        output = []
        
        # File and location info
        output.append(f"File: {context.file_path}")
        if context.class_name:
            output.append(f"Class: {context.class_name}")
        if context.function_name:
            output.append(f"Function: {context.function_name}")
        output.append(f"Error at line {context.error_line}")
        output.append("")
        
        # Code context with line numbers
        output.append("Code Context:")
        for line_num, content in context.context_lines:
            marker = ">>> " if line_num == context.error_line else "    "
            output.append(f"{marker}{line_num:4d} | {content}")
            
        # Variables in scope
        if context.variables:
            output.append("")
            output.append("Variables in scope:")
            for var in sorted(context.variables):
                output.append(f"  • {var}")
                
        return "\n".join(output)
    
    def get_minimal_context(self, context: CodeContext) -> Dict[str, any]:
        """Get minimal context information for templates."""
        return {
            'file': Path(context.file_path).name,
            'line': context.error_line,
            'function': context.function_name,
            'class': context.class_name,
            'error_line_content': next(
                (content for line_num, content in context.context_lines 
                 if line_num == context.error_line),
                ""
            )
        }