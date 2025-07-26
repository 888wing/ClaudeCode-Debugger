"""Intelligent suggestion engine for debugging solutions."""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class Suggestion:
    """Represents a debugging suggestion."""
    title: str
    description: str
    steps: List[str]
    confidence: float  # 0.0 to 1.0
    category: str  # 'fix', 'diagnostic', 'workaround', 'prevention'
    tags: List[str] = None
    code_snippet: Optional[str] = None
    references: List[str] = None


class SuggestionEngine:
    """Generate intelligent debugging suggestions based on error analysis."""
    
    def __init__(self):
        """Initialize the suggestion engine."""
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self) -> Dict[str, List[Dict]]:
        """Load suggestion knowledge base."""
        # For now, use a hardcoded knowledge base
        # In production, this could load from a file or database
        return {
            "null_reference": [
                {
                    "title": "Add Null Check",
                    "description": "Add explicit null/undefined check before accessing properties",
                    "steps": [
                        "Identify the variable causing the error",
                        "Add null check before property access",
                        "Consider using optional chaining (?.) if available"
                    ],
                    "confidence": 0.9,
                    "category": "fix",
                    "code_snippet": "if (obj && obj.property) { /* safe to use */ }"
                },
                {
                    "title": "Initialize Variables",
                    "description": "Ensure all variables are properly initialized",
                    "steps": [
                        "Check variable declaration",
                        "Add default value initialization",
                        "Verify async operations complete before access"
                    ],
                    "confidence": 0.8,
                    "category": "prevention"
                }
            ],
            "type_mismatch": [
                {
                    "title": "Add Type Validation",
                    "description": "Validate input types before processing",
                    "steps": [
                        "Identify expected vs actual types",
                        "Add type checking function",
                        "Handle type conversion if needed"
                    ],
                    "confidence": 0.85,
                    "category": "fix",
                    "code_snippet": "if (typeof value === 'string') { /* process */ }"
                }
            ],
            "import_error": [
                {
                    "title": "Install Missing Dependencies",
                    "description": "Install required packages using package manager",
                    "steps": [
                        "Check package.json or requirements.txt",
                        "Run package installation command",
                        "Verify installation succeeded"
                    ],
                    "confidence": 0.95,
                    "category": "fix",
                    "code_snippet": "npm install <package> or pip install <package>"
                },
                {
                    "title": "Fix Import Path",
                    "description": "Correct the import path to match file structure",
                    "steps": [
                        "Verify file exists at specified path",
                        "Check relative vs absolute imports",
                        "Update import statement"
                    ],
                    "confidence": 0.9,
                    "category": "fix"
                }
            ]
        }
    
    def generate_suggestions(
        self, 
        error_type: str,
        error_patterns: List[str],
        stack_trace_info: Optional[Dict] = None,
        code_context: Optional[Dict] = None
    ) -> List[Suggestion]:
        """Generate suggestions based on error analysis."""
        suggestions = []
        
        # Get base suggestions from knowledge base
        for pattern in error_patterns:
            if pattern in self.knowledge_base:
                for suggestion_data in self.knowledge_base[pattern]:
                    suggestion = Suggestion(
                        title=suggestion_data["title"],
                        description=suggestion_data["description"],
                        steps=suggestion_data["steps"],
                        confidence=suggestion_data["confidence"],
                        category=suggestion_data["category"],
                        code_snippet=suggestion_data.get("code_snippet"),
                        tags=suggestion_data.get("tags", []),
                        references=suggestion_data.get("references", [])
                    )
                    suggestions.append(suggestion)
        
        # Enhance suggestions based on context
        if stack_trace_info:
            suggestions = self._enhance_with_stack_trace(suggestions, stack_trace_info)
            
        if code_context:
            suggestions = self._enhance_with_code_context(suggestions, code_context)
        
        # Sort by confidence
        suggestions.sort(key=lambda s: s.confidence, reverse=True)
        
        # Add generic suggestions if no specific ones found
        if not suggestions:
            suggestions.extend(self._get_generic_suggestions(error_type))
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _enhance_with_stack_trace(
        self, 
        suggestions: List[Suggestion], 
        stack_trace_info: Dict
    ) -> List[Suggestion]:
        """Enhance suggestions with stack trace information."""
        # If error is in user code, increase confidence
        if stack_trace_info.get('root_cause', {}).get('file'):
            for suggestion in suggestions:
                if suggestion.category == 'fix':
                    suggestion.confidence *= 1.1  # 10% boost
                    
        # Add language-specific suggestions
        language = stack_trace_info.get('language')
        if language:
            for suggestion in suggestions:
                suggestion.tags = suggestion.tags or []
                suggestion.tags.append(f"lang:{language}")
                
        return suggestions
    
    def _enhance_with_code_context(
        self, 
        suggestions: List[Suggestion], 
        code_context: Dict
    ) -> List[Suggestion]:
        """Enhance suggestions with code context."""
        # If we know the function/class, make suggestions more specific
        if code_context.get('function'):
            for suggestion in suggestions:
                suggestion.description = f"In function '{code_context['function']}': {suggestion.description}"
                
        return suggestions
    
    def _get_generic_suggestions(self, error_type: str) -> List[Suggestion]:
        """Get generic debugging suggestions."""
        return [
            Suggestion(
                title="Check Recent Changes",
                description="Review recent code changes that might have introduced the error",
                steps=[
                    "Check git log for recent commits",
                    "Review changes in error-related files",
                    "Test reverting recent changes"
                ],
                confidence=0.6,
                category="diagnostic",
                tags=["generic"]
            ),
            Suggestion(
                title="Enable Debug Logging",
                description="Add logging to understand program flow",
                steps=[
                    "Add console.log/print statements",
                    "Log variable values before error",
                    "Check application logs"
                ],
                confidence=0.5,
                category="diagnostic",
                tags=["generic"]
            ),
            Suggestion(
                title="Search for Similar Issues",
                description="Look for similar errors in documentation or forums",
                steps=[
                    "Search error message on Stack Overflow",
                    "Check project issues on GitHub",
                    "Review framework documentation"
                ],
                confidence=0.4,
                category="workaround",
                tags=["generic"]
            )
        ]
    
    def format_suggestion(self, suggestion: Suggestion) -> str:
        """Format a suggestion for display."""
        output = []
        
        # Title with confidence indicator
        confidence_emoji = "🟢" if suggestion.confidence > 0.8 else "🟡" if suggestion.confidence > 0.6 else "🔴"
        output.append(f"{confidence_emoji} {suggestion.title} ({suggestion.confidence:.0%} confidence)")
        output.append(f"   {suggestion.description}")
        
        # Steps
        output.append("   Steps:")
        for i, step in enumerate(suggestion.steps, 1):
            output.append(f"   {i}. {step}")
            
        # Code snippet if available
        if suggestion.code_snippet:
            output.append(f"   Example: {suggestion.code_snippet}")
            
        return "\n".join(output)
    
    def get_suggestions_summary(self, suggestions: List[Suggestion]) -> Dict[str, Any]:
        """Get a summary of suggestions for templates."""
        return {
            'total': len(suggestions),
            'categories': list(set(s.category for s in suggestions)),
            'avg_confidence': sum(s.confidence for s in suggestions) / len(suggestions) if suggestions else 0,
            'top_suggestion': suggestions[0].title if suggestions else None
        }