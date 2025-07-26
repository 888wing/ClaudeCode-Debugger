"""Pattern analyzer for identifying common error patterns."""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ErrorPattern:
    """Represents a known error pattern."""
    name: str
    pattern: str
    description: str
    category: str
    severity: str
    common_causes: List[str]
    solutions: List[str]
    

class PatternAnalyzer:
    """Analyze errors for common patterns and provide solutions."""
    
    # Common error patterns across languages
    ERROR_PATTERNS = [
        # Null/Undefined errors
        ErrorPattern(
            name="null_reference",
            pattern=r"(null|undefined|None|nil).*(reference|property|attribute|method)",
            description="Attempting to access property of null/undefined value",
            category="runtime",
            severity="high",
            common_causes=[
                "Variable not initialized",
                "Async operation returned null",
                "Optional chaining not used",
                "Missing null checks"
            ],
            solutions=[
                "Add null/undefined checks before access",
                "Use optional chaining (?.) operator",
                "Initialize variables with default values",
                "Verify async operations completed successfully"
            ]
        ),
        
        # Type errors
        ErrorPattern(
            name="type_mismatch",
            pattern=r"(TypeError|type mismatch|expected .* got|cannot convert)",
            description="Type mismatch or invalid type operation",
            category="type",
            severity="high",
            common_causes=[
                "Incorrect function argument types",
                "Implicit type conversion issues",
                "Missing type annotations",
                "API response format changed"
            ],
            solutions=[
                "Add explicit type checks",
                "Use proper type annotations",
                "Validate input data types",
                "Update TypeScript definitions"
            ]
        ),
        
        # Array/Index errors
        ErrorPattern(
            name="index_out_of_bounds",
            pattern=r"(IndexError|out of (bounds|range)|index .* size|Array index)",
            description="Array index out of bounds",
            category="runtime",
            severity="medium",
            common_causes=[
                "Off-by-one errors",
                "Empty array access",
                "Incorrect loop boundaries",
                "Dynamic array size changes"
            ],
            solutions=[
                "Check array length before access",
                "Use safe array access methods",
                "Verify loop conditions",
                "Handle empty arrays explicitly"
            ]
        ),
        
        # Import/Module errors
        ErrorPattern(
            name="import_error",
            pattern=r"(ImportError|ModuleNotFoundError|Cannot find module|Module not found)",
            description="Module or dependency not found",
            category="dependency",
            severity="high",
            common_causes=[
                "Missing dependency installation",
                "Incorrect import path",
                "Circular dependencies",
                "Version mismatch"
            ],
            solutions=[
                "Install missing dependencies",
                "Verify import paths",
                "Check for circular imports",
                "Update package versions"
            ]
        ),
        
        # Memory errors
        ErrorPattern(
            name="memory_error",
            pattern=r"(MemoryError|OutOfMemory|heap out of memory|stack overflow)",
            description="Memory allocation or stack overflow error",
            category="performance",
            severity="critical",
            common_causes=[
                "Infinite recursion",
                "Large data structures",
                "Memory leaks",
                "Insufficient heap size"
            ],
            solutions=[
                "Check for infinite loops/recursion",
                "Process data in chunks",
                "Clear unused references",
                "Increase memory limits"
            ]
        ),
        
        # Permission errors
        ErrorPattern(
            name="permission_denied",
            pattern=r"(PermissionError|Permission denied|Access denied|EACCES)",
            description="Insufficient permissions for operation",
            category="security",
            severity="medium",
            common_causes=[
                "File system permissions",
                "API authentication issues",
                "User role restrictions",
                "OS-level security policies"
            ],
            solutions=[
                "Check file/directory permissions",
                "Verify authentication credentials",
                "Run with appropriate privileges",
                "Review security policies"
            ]
        ),
        
        # Network errors
        ErrorPattern(
            name="network_error",
            pattern=r"(NetworkError|ConnectionError|ECONNREFUSED|timeout|unreachable)",
            description="Network connectivity or timeout issue",
            category="network",
            severity="medium",
            common_causes=[
                "Service unavailable",
                "Network connectivity issues",
                "Firewall blocking",
                "Incorrect URL/port"
            ],
            solutions=[
                "Check network connectivity",
                "Verify service is running",
                "Check firewall rules",
                "Validate URLs and ports"
            ]
        ),
        
        # Syntax errors
        ErrorPattern(
            name="syntax_error",
            pattern=r"(SyntaxError|ParseError|Unexpected token|Invalid syntax)",
            description="Code syntax error",
            category="syntax",
            severity="high",
            common_causes=[
                "Missing brackets/parentheses",
                "Incorrect indentation",
                "Typos in keywords",
                "Unsupported syntax for version"
            ],
            solutions=[
                "Check matching brackets",
                "Verify indentation",
                "Review syntax highlighting",
                "Check language version compatibility"
            ]
        ),
    ]
    
    def __init__(self):
        """Initialize the pattern analyzer."""
        self.patterns = {p.name: p for p in self.ERROR_PATTERNS}
        
    def analyze(self, error_text: str) -> List[ErrorPattern]:
        """Find matching error patterns in the error text."""
        matches = []
        
        for pattern in self.ERROR_PATTERNS:
            if re.search(pattern.pattern, error_text, re.IGNORECASE):
                matches.append(pattern)
                
        return matches
    
    def get_suggestions(self, patterns: List[ErrorPattern]) -> Dict[str, List[str]]:
        """Get aggregated suggestions from matched patterns."""
        suggestions = {
            'causes': [],
            'solutions': [],
            'categories': set(),
            'severity': 'low'
        }
        
        severity_order = ['low', 'medium', 'high', 'critical']
        max_severity_index = 0
        
        for pattern in patterns:
            suggestions['causes'].extend(pattern.common_causes)
            suggestions['solutions'].extend(pattern.solutions)
            suggestions['categories'].add(pattern.category)
            
            # Track highest severity
            severity_index = severity_order.index(pattern.severity)
            if severity_index > max_severity_index:
                max_severity_index = severity_index
                suggestions['severity'] = pattern.severity
        
        # Remove duplicates while preserving order
        suggestions['causes'] = list(dict.fromkeys(suggestions['causes']))
        suggestions['solutions'] = list(dict.fromkeys(suggestions['solutions']))
        suggestions['categories'] = list(suggestions['categories'])
        
        return suggestions
    
    def get_pattern_by_name(self, name: str) -> Optional[ErrorPattern]:
        """Get a specific pattern by name."""
        return self.patterns.get(name)
    
    def add_custom_pattern(self, pattern: ErrorPattern):
        """Add a custom error pattern."""
        self.patterns[pattern.name] = pattern
        self.ERROR_PATTERNS.append(pattern)
        
    def format_pattern_match(self, pattern: ErrorPattern) -> str:
        """Format a pattern match for display."""
        return f"""
Pattern Detected: {pattern.name}
Category: {pattern.category}
Severity: {pattern.severity}
Description: {pattern.description}

Common Causes:
{chr(10).join(f'  • {cause}' for cause in pattern.common_causes)}

Suggested Solutions:
{chr(10).join(f'  ✓ {solution}' for solution in pattern.solutions)}
"""