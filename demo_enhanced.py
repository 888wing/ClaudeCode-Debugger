#!/usr/bin/env python3
"""Demo script for enhanced ClaudeCode-Debugger features."""

from claudecode_debugger.i18n import get_translator
from claudecode_debugger.analyzers import StackTraceAnalyzer, PatternAnalyzer
from claudecode_debugger.suggestions import SuggestionEngine

# Sample error for demo
SAMPLE_ERROR = '''
Traceback (most recent call last):
  File "/Users/test/app.py", line 42, in process_data
    result = data.get_value()
AttributeError: 'NoneType' object has no attribute 'get_value'
'''

def demo_i18n():
    """Demo internationalization features."""
    print("=== i18n Demo ===\n")
    
    # Chinese translator
    zh_translator = get_translator('zh')
    print("Chinese Messages:")
    print(f"  {zh_translator('app.name')}: {zh_translator('app.description')}")
    print(f"  {zh_translator('cli.analyzing')}")
    print(f"  {zh_translator('error.title', type='AttributeError', severity='HIGH')}")
    
    print("\nEnglish Messages:")
    # English translator
    en_translator = get_translator('en')
    print(f"  {en_translator('app.name')}: {en_translator('app.description')}")
    print(f"  {en_translator('cli.analyzing')}")
    print(f"  {en_translator('error.title', type='AttributeError', severity='HIGH')}")

def demo_stack_analysis():
    """Demo stack trace analysis."""
    print("\n\n=== Stack Trace Analysis Demo ===\n")
    
    analyzer = StackTraceAnalyzer()
    result = analyzer.analyze(SAMPLE_ERROR)
    
    if result:
        print(f"Language: {result.language}")
        print(f"Error Type: {result.error_type}")
        print(f"Error Message: {result.error_message}")
        print(f"Total Frames: {len(result.frames)}")
        
        if result.root_cause_frame:
            print(f"\nRoot Cause:")
            print(f"  File: {result.root_cause_frame.file}")
            print(f"  Line: {result.root_cause_frame.line}")
            print(f"  Function: {result.root_cause_frame.function}")

def demo_pattern_analysis():
    """Demo error pattern analysis."""
    print("\n\n=== Pattern Analysis Demo ===\n")
    
    analyzer = PatternAnalyzer()
    patterns = analyzer.analyze(SAMPLE_ERROR)
    
    if patterns:
        print(f"Found {len(patterns)} patterns:")
        for pattern in patterns:
            print(f"\n• {pattern.name}")
            print(f"  Description: {pattern.description}")
            print(f"  Severity: {pattern.severity}")
            print(f"  Category: {pattern.category}")

def demo_suggestions():
    """Demo suggestion engine."""
    print("\n\n=== Suggestion Engine Demo ===\n")
    
    engine = SuggestionEngine()
    suggestions = engine.generate_suggestions(
        error_type='AttributeError',
        error_patterns=['null_reference']
    )
    
    print(f"Generated {len(suggestions)} suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. {suggestion.title} ({suggestion.confidence:.0%} confidence)")
        print(f"   {suggestion.description}")
        print("   Steps:")
        for j, step in enumerate(suggestion.steps, 1):
            print(f"   {j}. {step}")
        if suggestion.code_snippet:
            print(f"   Example: {suggestion.code_snippet}")

def main():
    """Run all demos."""
    print("ClaudeCode-Debugger Enhanced Features Demo")
    print("=" * 50)
    
    demo_i18n()
    demo_stack_analysis()
    demo_pattern_analysis()
    demo_suggestions()
    
    print("\n\n" + "=" * 50)
    print("Demo completed!")
    print("\nTry the enhanced CLI:")
    print("  ccdebug --help")
    print("  ccdebug 'Your error message' --lang zh")
    print("  ccdebug 'Your error message' --analyze-stack --suggest")

if __name__ == "__main__":
    main()