"""Prompt generation module for ClaudeCode-Debugger."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
from jinja2 import Environment, FileSystemLoader, Template

# Import advanced template system
from .template_system import AdvancedTemplateSystem


class PromptGenerator:
    """Generates debug prompts using templates."""
    
    # Default agent mappings
    DEFAULT_AGENTS = {
        'typescript': 'debug-specialist',
        'javascript': 'debug-specialist', 
        'python': 'backend-system-architect',
        'memory': 'backend-system-architect',
        'network': 'backend-system-architect',
        'react': 'frontend-system-builder',
        'build': 'debug-specialist',
        'general': 'general-purpose',
        'docker': 'backend-system-architect',
        'kubernetes': 'backend-system-architect',
        'k8s': 'backend-system-architect',
        'container': 'backend-system-architect',
    }
    
    def __init__(self, template_dir: Optional[Path] = None, use_advanced: bool = True):
        """
        Initialize prompt generator.
        
        Args:
            template_dir: Directory containing templates. Defaults to built-in templates.
            use_advanced: Whether to use the advanced template system.
        """
        self.use_advanced = use_advanced
        
        if self.use_advanced:
            # Use advanced template system
            template_dirs = []
            if template_dir:
                template_dirs.append(template_dir)
            self.template_system = AdvancedTemplateSystem(template_dirs)
            self.templates = self.template_system.templates
        else:
            # Legacy mode
            if template_dir is None:
                # Use built-in templates
                self.template_dir = Path(__file__).parent.parent / 'templates'
            else:
                self.template_dir = Path(template_dir)
                
            # Initialize Jinja2 environment
            self.env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                trim_blocks=True,
                lstrip_blocks=True,
            )
            
            # Add custom filters
            self.env.filters['capitalize_first'] = lambda s: s[0].upper() + s[1:] if s else ''
            self.env.filters['format_list'] = lambda l: '\n'.join(f'- {item}' for item in l)
            
            # Load templates
            self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, Dict]:
        """Load all available templates (legacy mode)."""
        templates = {}
        
        # Load built-in templates
        for template_file in self.template_dir.glob('*.yaml'):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = yaml.safe_load(f)
                    template_name = template_file.stem
                    templates[template_name] = template_data
            except Exception as e:
                print(f"Warning: Failed to load template {template_file}: {e}")
                
        # Load user templates if they exist
        user_template_dir = Path.home() / '.ccdebug' / 'templates'
        if user_template_dir.exists():
            for template_file in user_template_dir.glob('*.yaml'):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = yaml.safe_load(f)
                        template_name = f"user_{template_file.stem}"
                        templates[template_name] = template_data
                except Exception:
                    pass
                    
        return templates
    
    def generate(self, error_text: str, error_type: str, 
                 error_info: Optional[Dict] = None,
                 custom_agent: Optional[str] = None) -> str:
        """
        Generate debug prompt for given error.
        
        Args:
            error_text: The error message text.
            error_type: The detected error type.
            error_info: Additional extracted information.
            custom_agent: Override default agent selection.
            
        Returns:
            Generated debug prompt.
        """
        if self.use_advanced:
            # Use advanced template system
            # Try to find more specific template first
            template_name = self._find_best_template(error_type, error_text, error_info)
            
            # Prepare context
            context = self._prepare_context(error_text, error_type, error_info)
            
            # Add agent recommendation
            context['recommended_agent'] = custom_agent or self._get_recommended_agent(
                template_name, error_type
            )
            
            # Add severity based on error type
            context['severity'] = self._determine_severity(error_type, error_info)
            
            try:
                prompt = self.template_system.render(template_name, context)
            except Exception as e:
                # Fallback to general template
                print(f"Warning: Failed to render template {template_name}: {e}")
                prompt = self.template_system.render('general', context)
                
            return prompt
        else:
            # Legacy mode
            # Get template for error type
            template_data = self._get_template(error_type)
            
            # Prepare context
            context = self._prepare_context(error_text, error_type, error_info)
            
            # Add agent recommendation
            context['recommended_agent'] = custom_agent or self.DEFAULT_AGENTS.get(
                error_type, 'general-purpose'
            )
            
            # Render template
            template_str = template_data.get('template', self._get_default_template())
            template = Template(template_str)
            
            prompt = template.render(**context)
            
            return prompt
    
    def _get_template(self, error_type: str) -> Dict:
        """Get template for error type."""
        # Check for specific template
        if error_type in self.templates:
            return self.templates[error_type]
            
        # Check for user override
        user_template = f"user_{error_type}"
        if user_template in self.templates:
            return self.templates[user_template]
            
        # Fall back to general template
        if 'general' in self.templates:
            return self.templates['general']
            
        # Return minimal default
        return {'template': self._get_default_template()}
    
    def _prepare_context(self, error_text: str, error_type: str,
                        error_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Prepare template context."""
        context = {
            'error_text': error_text,
            'error_type': error_type,
            'error_type_display': error_type.replace('_', ' ').title(),
        }
        
        if error_info:
            context.update({
                'files': error_info.get('files', []),
                'line_numbers': error_info.get('line_numbers', []),
                'error_codes': error_info.get('error_codes', []),
                'error_messages': error_info.get('error_messages', []),
                'stack_trace': error_info.get('stack_trace', ''),
                'file_count': len(error_info.get('files', [])),
                'error_count': len(error_info.get('error_messages', [])),
            })
            
            # Format file list
            if context['files']:
                context['affected_files'] = '\n'.join(f'- {f}' for f in context['files'])
            else:
                context['affected_files'] = '- Unknown files'
                
        return context
    
    def _get_default_template(self) -> str:
        """Get default template when no specific template exists."""
        return """🚨 {{ error_type_display }} Debug

## Error Summary
Detected {{ error_count or 1 }} error(s) in {{ error_type }} code.

{% if files %}
### Affected Files:
{{ affected_files }}
{% endif %}

{% if error_codes %}
### Error Codes:
{% for code in error_codes %}
- {{ code }}
{% endfor %}
{% endif %}

## Error Details
```
{{ error_text }}
```

## Debug Tasks

1. **Analyze the Error**
   - Identify the root cause
   - Check for common patterns
   - Review recent changes

2. **Fix Strategy**
   - Apply appropriate fixes
   - Test the solution
   - Verify no side effects

3. **Prevention**
   - Add tests to prevent recurrence
   - Update documentation
   - Consider refactoring if needed

## Recommended Agent
Use the `{{ recommended_agent }}` agent for this type of error.
"""
    
    def list_templates(self) -> List[str]:
        """List all available templates."""
        if self.use_advanced:
            return self.template_system.list_templates()
        return list(self.templates.keys())
    
    def get_agent_for_error(self, error_type: str) -> str:
        """Get recommended agent for error type."""
        return self.DEFAULT_AGENTS.get(error_type, 'general-purpose')
    
    def _find_best_template(self, error_type: str, error_text: str, 
                           error_info: Optional[Dict] = None) -> str:
        """Find the best matching template for the error."""
        # Check for advanced templates first
        candidates = []
        
        # Direct match with advanced template
        if f"{error_type}_advanced" in self.templates:
            candidates.append(f"{error_type}_advanced")
            
        # Check for framework-specific templates
        if error_type == 'typescript':
            if 'react' in error_text.lower():
                if 'react_typescript' in self.templates:
                    candidates.append('react_typescript')
            elif 'vue' in error_text.lower():
                if 'vue_typescript' in self.templates:
                    candidates.append('vue_typescript')
            elif 'angular' in error_text.lower():
                if 'angular_typescript' in self.templates:
                    candidates.append('angular_typescript')
                    
        # Check for container-related templates
        if any(kw in error_text.lower() for kw in ['docker', 'container', 'kubernetes', 'k8s', 'pod']):
            if 'docker_k8s' in self.templates:
                candidates.append('docker_k8s')
                
        # Check for memory-related templates
        if any(kw in error_text.lower() for kw in ['memory', 'heap', 'oom', 'outofmemory']):
            if 'memory_advanced' in self.templates:
                candidates.append('memory_advanced')
                
        # Add basic template as fallback
        if error_type in self.templates:
            candidates.append(error_type)
            
        # Return first available candidate
        for candidate in candidates:
            if candidate in self.templates:
                return candidate
                
        return 'general'
    
    def _get_recommended_agent(self, template_name: str, error_type: str) -> str:
        """Get recommended agent based on template and error type."""
        # Check template metadata first
        if template_name in self.templates:
            template_data = self.templates[template_name]
            if 'agent' in template_data:
                return template_data['agent']
                
        # Fall back to default mapping
        return self.DEFAULT_AGENTS.get(error_type, 'general-purpose')
    
    def _determine_severity(self, error_type: str, error_info: Optional[Dict] = None) -> str:
        """Determine error severity level."""
        # Critical errors
        critical_keywords = ['fatal', 'panic', 'crash', 'segfault', 'sigsegv', 'oom']
        if any(kw in error_type.lower() for kw in critical_keywords):
            return 'critical'
            
        if error_info:
            error_text = ' '.join(error_info.get('error_messages', []))
            if any(kw in error_text.lower() for kw in critical_keywords):
                return 'critical'
                
        # Warnings
        warning_keywords = ['warning', 'deprecated', 'notice']
        if any(kw in error_type.lower() for kw in warning_keywords):
            return 'warning'
            
        # Default to error
        return 'error'