#!/usr/bin/env python3
"""Complete test suite for ClaudeCode-Debugger before deployment."""

import unittest
import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Test data
TEST_ERRORS = {
    'python_null': '''Traceback (most recent call last):
  File "/app.py", line 42, in process_data
    result = data.get_value()
AttributeError: 'NoneType' object has no attribute 'get_value'
''',
    
    'javascript_type': '''TypeError: Cannot read property 'name' of undefined
    at UserProfile (/components/UserProfile.js:15:23)
    at renderWithHooks (react-dom.development.js:14985:18)
''',
    
    'python_import': '''Traceback (most recent call last):
  File "main.py", line 1, in <module>
    import pandas as pd
ModuleNotFoundError: No module named 'pandas'
''',
    
    'memory_error': '''MemoryError: Unable to allocate array with shape (1000000, 1000000)''',
    
    'network_error': '''ConnectionError: HTTPSConnectionPool(host='api.example.com', port=443): Max retries exceeded'''
}


class TestI18n(unittest.TestCase):
    """Test internationalization features."""
    
    def test_translator_import(self):
        """Test translator can be imported."""
        from claudecode_debugger.i18n import get_translator, Translator
        self.assertIsNotNone(get_translator)
        self.assertIsNotNone(Translator)
    
    def test_language_detection(self):
        """Test language detection."""
        from claudecode_debugger.i18n import Translator
        translator = Translator()
        self.assertIn(translator.language, ['en', 'zh'])
    
    def test_chinese_messages(self):
        """Test Chinese messages."""
        from claudecode_debugger.i18n import get_translator
        translator = get_translator('zh')
        
        # Test basic messages
        self.assertEqual(translator('app.name'), 'ClaudeCode-Debugger')
        self.assertEqual(translator('cli.analyzing'), '分析錯誤中...')
        self.assertEqual(translator('cli.copied'), '✓ 已複製到剪貼板！')
    
    def test_english_messages(self):
        """Test English messages."""
        from claudecode_debugger.i18n import get_translator
        translator = get_translator('en')
        
        # Test basic messages
        self.assertEqual(translator('app.name'), 'ClaudeCode-Debugger')
        self.assertEqual(translator('cli.analyzing'), 'Analyzing error...')
        self.assertEqual(translator('cli.copied'), '✓ Copied to clipboard!')
    
    def test_message_formatting(self):
        """Test message formatting with parameters."""
        from claudecode_debugger.i18n import get_translator
        
        # Test Chinese formatting
        zh = get_translator('zh')
        msg = zh('error.count', count=5)
        self.assertIn('5', msg)
        
        # Test English formatting
        en = get_translator('en')
        msg = en('error.count', count=3)
        self.assertIn('3', msg)


class TestAnalyzers(unittest.TestCase):
    """Test analyzer modules."""
    
    def test_stack_trace_analyzer(self):
        """Test stack trace analysis."""
        from claudecode_debugger.analyzers import StackTraceAnalyzer
        
        analyzer = StackTraceAnalyzer()
        
        # Test Python stack trace
        result = analyzer.analyze(TEST_ERRORS['python_null'])
        self.assertIsNotNone(result)
        self.assertEqual(result.language, 'python')
        self.assertEqual(result.error_type, 'AttributeError')
        self.assertIn('NoneType', result.error_message)
        
        # Test JavaScript stack trace
        result = analyzer.analyze(TEST_ERRORS['javascript_type'])
        self.assertIsNotNone(result)
        self.assertEqual(result.language, 'javascript')
        self.assertEqual(result.error_type, 'TypeError')
    
    def test_pattern_analyzer(self):
        """Test pattern analysis."""
        from claudecode_debugger.analyzers import PatternAnalyzer
        
        analyzer = PatternAnalyzer()
        
        # Test null reference pattern
        patterns = analyzer.analyze(TEST_ERRORS['python_null'])
        self.assertTrue(len(patterns) > 0)
        pattern_names = [p.name for p in patterns]
        self.assertIn('null_reference', pattern_names)
        
        # Test import error pattern
        patterns = analyzer.analyze(TEST_ERRORS['python_import'])
        pattern_names = [p.name for p in patterns]
        self.assertIn('import_error', pattern_names)
        
        # Test memory error pattern
        patterns = analyzer.analyze(TEST_ERRORS['memory_error'])
        pattern_names = [p.name for p in patterns]
        self.assertIn('memory_error', pattern_names)
    
    def test_code_context_analyzer(self):
        """Test code context analysis."""
        from claudecode_debugger.analyzers import CodeContextAnalyzer
        
        analyzer = CodeContextAnalyzer()
        
        # Test language detection
        self.assertEqual(analyzer._detect_language('test.py'), 'python')
        self.assertEqual(analyzer._detect_language('test.js'), 'javascript')
        self.assertEqual(analyzer._detect_language('test.ts'), 'typescript')


class TestSuggestions(unittest.TestCase):
    """Test suggestion engine."""
    
    def test_suggestion_engine(self):
        """Test suggestion generation."""
        from claudecode_debugger.suggestions import SuggestionEngine
        
        engine = SuggestionEngine()
        
        # Test null reference suggestions
        suggestions = engine.generate_suggestions(
            error_type='AttributeError',
            error_patterns=['null_reference']
        )
        self.assertTrue(len(suggestions) > 0)
        self.assertTrue(all(s.confidence > 0 for s in suggestions))
        
        # Test import error suggestions
        suggestions = engine.generate_suggestions(
            error_type='ModuleNotFoundError',
            error_patterns=['import_error']
        )
        self.assertTrue(len(suggestions) > 0)
        
        # Check suggestion structure
        if suggestions:
            s = suggestions[0]
            self.assertIsNotNone(s.title)
            self.assertIsNotNone(s.description)
            self.assertIsInstance(s.steps, list)
            self.assertTrue(0 <= s.confidence <= 1)


class TestCLIEnhanced(unittest.TestCase):
    """Test enhanced CLI functionality."""
    
    def test_cli_import(self):
        """Test CLI can be imported."""
        try:
            from claudecode_debugger.cli_new import cli
            self.assertIsNotNone(cli)
        except ImportError as e:
            self.fail(f"Failed to import cli_new: {e}")
    
    def test_translator_usage(self):
        """Test translator is used correctly in CLI."""
        from claudecode_debugger.cli_new import _get_error_content
        from claudecode_debugger.i18n import get_translator
        
        # This tests that the function accepts translator
        translator = get_translator('en')
        # Would need to mock or provide actual error to fully test


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_full_analysis_pipeline(self):
        """Test complete analysis pipeline."""
        from claudecode_debugger.analyzers import StackTraceAnalyzer, PatternAnalyzer
        from claudecode_debugger.suggestions import SuggestionEngine
        
        # Analyze error
        error = TEST_ERRORS['python_null']
        
        # Stack trace analysis
        stack_analyzer = StackTraceAnalyzer()
        stack_result = stack_analyzer.analyze(error)
        self.assertIsNotNone(stack_result)
        
        # Pattern analysis
        pattern_analyzer = PatternAnalyzer()
        patterns = pattern_analyzer.analyze(error)
        self.assertTrue(len(patterns) > 0)
        
        # Generate suggestions
        engine = SuggestionEngine()
        pattern_names = [p.name for p in patterns]
        suggestions = engine.generate_suggestions(
            error_type=stack_result.error_type if stack_result else 'unknown',
            error_patterns=pattern_names
        )
        self.assertTrue(len(suggestions) > 0)
    
    def test_multi_language_pipeline(self):
        """Test pipeline works with both languages."""
        from claudecode_debugger.i18n import get_translator
        from claudecode_debugger.core.detector import ErrorDetector
        
        # Test with both languages
        for lang in ['en', 'zh']:
            translator = get_translator(lang)
            
            # Test basic operations
            detector = ErrorDetector()
            error_type = detector.detect(TEST_ERRORS['python_null'])
            self.assertIsNotNone(error_type)
            
            # Test messages
            msg = translator('error.title', type=error_type, severity='HIGH')
            self.assertIsNotNone(msg)


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 70)
    print("ClaudeCode-Debugger Complete Test Suite")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestI18n,
        TestAnalyzers,
        TestSuggestions,
        TestCLIEnhanced,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)