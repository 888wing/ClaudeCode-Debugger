"""Tests for PromptGenerator module."""

import pytest
from pathlib import Path
from claudecode_debugger.core.generator import PromptGenerator


class TestPromptGenerator:
    """Test cases for PromptGenerator class."""
    
    @pytest.fixture
    def generator(self):
        """Create PromptGenerator instance."""
        return PromptGenerator()
    
    def test_generate_basic_prompt(self, generator):
        """Test basic prompt generation."""
        error_text = "TypeError: Cannot read property 'name' of undefined"
        prompt = generator.generate(error_text, "javascript")
        
        assert "JavaScript" in prompt
        assert "Debug" in prompt
        assert error_text in prompt
    
    def test_generate_with_error_info(self, generator):
        """Test prompt generation with additional info."""
        error_text = "TS2322: Type error"
        error_info = {
            'files': ['app.ts', 'main.ts'],
            'line_numbers': [42, 100],
            'error_codes': ['TS2322'],
            'error_messages': ["Type 'string' is not assignable to type 'number'"]
        }
        
        prompt = generator.generate(error_text, "typescript", error_info)
        
        assert "app.ts" in prompt
        assert "main.ts" in prompt
        assert "TS2322" in prompt
    
    def test_custom_agent_selection(self, generator):
        """Test custom agent override."""
        prompt = generator.generate(
            "Some error",
            "general",
            custom_agent="frontend-system-builder"
        )
        
        assert "frontend-system-builder" in prompt
    
    def test_default_agent_mapping(self, generator):
        """Test default agent mappings."""
        assert generator.get_agent_for_error("typescript") == "debug-specialist"
        assert generator.get_agent_for_error("python") == "backend-system-architect"
        assert generator.get_agent_for_error("memory") == "backend-system-architect"
        assert generator.get_agent_for_error("unknown") == "general-purpose"
    
    def test_list_templates(self, generator):
        """Test template listing."""
        templates = generator.list_templates()
        
        # Should have at least the templates we created
        expected_templates = [
            'typescript', 'javascript', 'python',
            'memory', 'network', 'general'
        ]
        
        for template in expected_templates:
            assert template in templates
    
    def test_template_context_preparation(self, generator):
        """Test context preparation for templates."""
        error_info = {
            'files': ['file1.js', 'file2.js'],
            'line_numbers': [10, 20, 30],
            'error_codes': ['E001', 'E002'],
            'error_messages': ['Error 1', 'Error 2'],
        }
        
        context = generator._prepare_context(
            "Test error",
            "javascript",
            error_info
        )
        
        assert context['error_text'] == "Test error"
        assert context['error_type'] == "javascript"
        assert context['file_count'] == 2
        assert context['error_count'] == 2
        assert "- file1.js" in context['affected_files']
        assert "- file2.js" in context['affected_files']
    
    def test_empty_error_info_handling(self, generator):
        """Test handling of empty error info."""
        prompt = generator.generate("Some error", "general", {})
        
        # Should still generate a valid prompt
        assert "Debug" in prompt
        assert "Some error" in prompt
    
    def test_template_fallback(self, generator):
        """Test fallback to general template."""
        # Use a non-existent error type
        prompt = generator.generate(
            "Unknown error type",
            "nonexistent_type"
        )
        
        # Should still generate a prompt
        assert "Debug" in prompt
        assert "Unknown error type" in prompt