"""Advanced template system for ClaudeCode-Debugger."""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
import yaml
from jinja2 import (
    Environment, FileSystemLoader, Template, 
    TemplateNotFound, TemplateSyntaxError,
    select_autoescape, meta
)
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from collections import defaultdict

class TemplateCache:
    """In-memory template cache with versioning."""
    
    def __init__(self, ttl: int = 3600):
        self.cache: Dict[str, Tuple[Any, float, str]] = {}
        self.ttl = ttl
        self.lock = threading.RLock()
        
    def get(self, key: str, version: str) -> Optional[Any]:
        """Get cached item if valid."""
        with self.lock:
            if key in self.cache:
                data, timestamp, cached_version = self.cache[key]
                if cached_version == version and (datetime.now().timestamp() - timestamp) < self.ttl:
                    return data
        return None
        
    def set(self, key: str, value: Any, version: str):
        """Cache an item with version."""
        with self.lock:
            self.cache[key] = (value, datetime.now().timestamp(), version)
            
    def invalidate(self, key: str):
        """Invalidate cache entry."""
        with self.lock:
            self.cache.pop(key, None)
            
    def clear(self):
        """Clear all cache."""
        with self.lock:
            self.cache.clear()


class TemplateFileWatcher(FileSystemEventHandler):
    """Watch template files for changes."""
    
    def __init__(self, template_system):
        self.template_system = template_system
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.yaml'):
            self.template_system.reload_template(Path(event.src_path))
            
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.yaml'):
            self.template_system.reload_template(Path(event.src_path))


class AdvancedTemplateSystem:
    """Advanced template system with inheritance, composition, and hot reload."""
    
    def __init__(self, template_dirs: Optional[List[Path]] = None):
        """
        Initialize advanced template system.
        
        Args:
            template_dirs: List of directories containing templates.
        """
        # Default template directories
        self.template_dirs = template_dirs or []
        
        # Add built-in templates
        builtin_dir = Path(__file__).parent.parent / 'templates'
        if builtin_dir.exists():
            self.template_dirs.append(builtin_dir)
            
        # Add user templates
        user_dir = Path.home() / '.ccdebug' / 'templates'
        if user_dir.exists():
            self.template_dirs.append(user_dir)
            
        # Add advanced templates
        advanced_dir = Path(__file__).parent.parent / 'templates' / 'advanced'
        if not advanced_dir.exists():
            advanced_dir.mkdir(parents=True, exist_ok=True)
        self.template_dirs.append(advanced_dir)
        
        # Initialize components
        self.cache = TemplateCache()
        self.templates: Dict[str, Dict] = {}
        self.template_versions: Dict[str, str] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        
        # Initialize Jinja2 environment
        self._init_jinja_env()
        
        # Load all templates
        self.reload_all_templates()
        
        # Setup file watching
        self._setup_file_watching()
        
    def _init_jinja_env(self):
        """Initialize Jinja2 environment with custom features."""
        self.env = Environment(
            loader=FileSystemLoader([str(d) for d in self.template_dirs]),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=select_autoescape(['html', 'xml']),
            extensions=['jinja2.ext.do', 'jinja2.ext.loopcontrols']
        )
        
        # Add custom filters
        self._add_custom_filters()
        
        # Add custom functions
        self._add_custom_functions()
        
        # Add global variables
        self._add_globals()
        
    def _add_custom_filters(self):
        """Add custom Jinja2 filters."""
        filters = {
            'capitalize_first': lambda s: s[0].upper() + s[1:] if s else '',
            'format_list': lambda l: '\n'.join(f'- {item}' for item in l),
            'format_code': lambda code, lang='': f'```{lang}\n{code}\n```',
            'truncate_middle': lambda s, n=50: s if len(s) <= n else s[:n//2] + '...' + s[-(n//2):],
            'to_camel_case': lambda s: ''.join(w.capitalize() for w in s.split('_')),
            'to_snake_case': lambda s: ''.join(['_' + c.lower() if c.isupper() else c for c in s]).lstrip('_'),
            'format_error_code': self._format_error_code,
            'severity_color': lambda s: {'error': '🔴', 'warning': '🟡', 'info': '🔵'}.get(s.lower(), '⚪'),
            'format_timestamp': lambda ts: datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'),
            'pluralize': lambda n, singular, plural: singular if n == 1 else plural,
            'file_icon': self._get_file_icon,
            'language_name': self._get_language_name,
        }
        
        for name, func in filters.items():
            self.env.filters[name] = func
            
    def _add_custom_functions(self):
        """Add custom Jinja2 functions."""
        functions = {
            'include_template': self._include_template,
            'has_template': self._has_template,
            'get_template_var': self._get_template_var,
            'format_stack_trace': self._format_stack_trace,
            'suggest_fix': self._suggest_fix,
            'get_related_errors': self._get_related_errors,
        }
        
        for name, func in functions.items():
            self.env.globals[name] = func
            
    def _add_globals(self):
        """Add global variables."""
        self.env.globals.update({
            'now': datetime.now,
            'version': '2.0.0',
            'debug_mode': os.getenv('CCDEBUG_DEBUG', 'false').lower() == 'true',
            'languages': ['typescript', 'javascript', 'python', 'java', 'go', 'rust', 'cpp'],
            'frameworks': {
                'frontend': ['react', 'vue', 'angular', 'svelte', 'nextjs'],
                'backend': ['express', 'fastapi', 'django', 'spring', 'gin'],
                'mobile': ['react-native', 'flutter', 'ionic'],
            },
        })
        
    def _format_error_code(self, code: str) -> str:
        """Format error code with description."""
        error_descriptions = {
            # TypeScript
            'TS2322': 'Type mismatch',
            'TS2339': 'Property does not exist',
            'TS2345': 'Argument type mismatch',
            'TS2304': 'Cannot find name',
            'TS2307': 'Cannot find module',
            # Python
            'E0001': 'Syntax error',
            'E1101': 'No member',
            'E0401': 'Import error',
            # General
            'ENOENT': 'File not found',
            'EACCES': 'Permission denied',
            'ENOMEM': 'Out of memory',
        }
        
        desc = error_descriptions.get(code, '')
        return f"{code}: {desc}" if desc else code
        
    def _get_file_icon(self, filename: str) -> str:
        """Get icon for file type."""
        ext = Path(filename).suffix.lower()
        icons = {
            '.ts': '📘', '.tsx': '⚛️', '.js': '📄', '.jsx': '⚛️',
            '.py': '🐍', '.java': '☕', '.go': '🐹', '.rs': '🦀',
            '.cpp': '⚙️', '.c': '⚙️', '.h': '📋', '.hpp': '📋',
            '.json': '📊', '.yaml': '📝', '.yml': '📝', '.xml': '📰',
            '.md': '📖', '.txt': '📃', '.log': '📜',
        }
        return icons.get(ext, '📄')
        
    def _get_language_name(self, ext: str) -> str:
        """Get language display name."""
        languages = {
            'ts': 'TypeScript', 'tsx': 'TypeScript React',
            'js': 'JavaScript', 'jsx': 'JavaScript React',
            'py': 'Python', 'java': 'Java', 'go': 'Go',
            'rs': 'Rust', 'cpp': 'C++', 'c': 'C',
        }
        return languages.get(ext.lower(), ext.upper())
        
    def _include_template(self, name: str, **kwargs) -> str:
        """Include another template."""
        try:
            template = self.get_template(name)
            return template.render(**kwargs)
        except Exception as e:
            return f"<!-- Error including template {name}: {e} -->"
            
    def _has_template(self, name: str) -> bool:
        """Check if template exists."""
        return name in self.templates
        
    def _get_template_var(self, template_name: str, var_name: str, default=None):
        """Get variable from template metadata."""
        if template_name in self.templates:
            return self.templates[template_name].get(var_name, default)
        return default
        
    def _format_stack_trace(self, stack_trace: str, max_frames: int = 10) -> str:
        """Format stack trace for display."""
        lines = stack_trace.strip().split('\n')
        if len(lines) > max_frames * 2:  # Each frame is usually 2 lines
            lines = lines[:max_frames * 2] + ['... (truncated)']
        return '\n'.join(lines)
        
    def _suggest_fix(self, error_type: str, error_code: str) -> List[str]:
        """Suggest possible fixes for error."""
        suggestions = {
            'typescript': {
                'TS2322': [
                    'Check if types are compatible',
                    'Add type assertion if safe',
                    'Update type definitions',
                ],
                'TS2339': [
                    'Add missing property to interface',
                    'Check for typos in property name',
                    'Verify object type is correct',
                ],
            },
            'python': {
                'NameError': [
                    'Check variable is defined before use',
                    'Import missing module',
                    'Check for typos in variable name',
                ],
                'ImportError': [
                    'Install missing package',
                    'Check import path',
                    'Verify module exists',
                ],
            },
        }
        
        return suggestions.get(error_type, {}).get(error_code, [])
        
    def _get_related_errors(self, error_type: str, error_code: str) -> List[str]:
        """Get related error codes."""
        related = {
            'typescript': {
                'TS2322': ['TS2339', 'TS2345'],
                'TS2304': ['TS2307', 'TS2552'],
            },
            'python': {
                'ImportError': ['ModuleNotFoundError', 'AttributeError'],
                'TypeError': ['AttributeError', 'ValueError'],
            },
        }
        
        return related.get(error_type, {}).get(error_code, [])
        
    def _setup_file_watching(self):
        """Setup file system watching for hot reload."""
        if not os.getenv('CCDEBUG_NO_WATCH', '').lower() == 'true':
            self.observer = Observer()
            handler = TemplateFileWatcher(self)
            
            for template_dir in self.template_dirs:
                if template_dir.exists():
                    self.observer.schedule(handler, str(template_dir), recursive=True)
                    
            self.observer.start()
            
    def reload_all_templates(self):
        """Reload all templates from disk."""
        self.templates.clear()
        self.dependencies.clear()
        self.cache.clear()
        
        for template_dir in self.template_dirs:
            if template_dir.exists():
                for template_file in template_dir.rglob('*.yaml'):
                    self._load_template(template_file)
                    
        # Resolve dependencies
        self._resolve_dependencies()
        
    def reload_template(self, template_path: Path):
        """Reload a single template."""
        template_name = template_path.stem
        
        # Invalidate cache
        self.cache.invalidate(template_name)
        
        # Reload template
        self._load_template(template_path)
        
        # Reload dependent templates
        for dependent in self._get_dependents(template_name):
            if dependent in self.templates:
                self.cache.invalidate(dependent)
                
    def _load_template(self, template_path: Path):
        """Load a template from file."""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                template_data = yaml.safe_load(content)
                
            template_name = template_path.stem
            
            # Handle namespacing for user templates
            if '.ccdebug' in str(template_path):
                template_name = f"user.{template_name}"
                
            # Store template
            self.templates[template_name] = template_data
            
            # Calculate version hash
            self.template_versions[template_name] = hashlib.md5(content.encode()).hexdigest()
            
            # Extract dependencies
            if 'extends' in template_data:
                self.dependencies[template_name].add(template_data['extends'])
                
            if 'includes' in template_data:
                for include in template_data['includes']:
                    self.dependencies[template_name].add(include)
                    
        except Exception as e:
            print(f"Error loading template {template_path}: {e}")
            
    def _resolve_dependencies(self):
        """Resolve template dependencies and check for cycles."""
        # Check for circular dependencies
        for template_name in self.templates:
            visited = set()
            if self._has_circular_dependency(template_name, visited):
                print(f"Warning: Circular dependency detected for template {template_name}")
                self.dependencies[template_name].clear()
                
    def _has_circular_dependency(self, template_name: str, visited: Set[str]) -> bool:
        """Check if template has circular dependencies."""
        if template_name in visited:
            return True
            
        visited.add(template_name)
        
        for dep in self.dependencies.get(template_name, []):
            if self._has_circular_dependency(dep, visited.copy()):
                return True
                
        return False
        
    def _get_dependents(self, template_name: str) -> Set[str]:
        """Get templates that depend on this template."""
        dependents = set()
        
        for name, deps in self.dependencies.items():
            if template_name in deps:
                dependents.add(name)
                dependents.update(self._get_dependents(name))
                
        return dependents
        
    def get_template(self, name: str) -> Template:
        """Get compiled template."""
        # Check cache
        version = self.template_versions.get(name, '')
        cached = self.cache.get(f"compiled_{name}", version)
        if cached:
            return cached
            
        # Get template data
        template_data = self._resolve_template(name)
        
        if not template_data:
            raise TemplateNotFound(name)
            
        # Compile template
        template_str = template_data.get('template', '')
        template = self.env.from_string(template_str)
        
        # Cache compiled template
        self.cache.set(f"compiled_{name}", template, version)
        
        return template
        
    def _resolve_template(self, name: str) -> Dict:
        """Resolve template with inheritance and includes."""
        # Check cache
        version = self.template_versions.get(name, '')
        cached = self.cache.get(f"resolved_{name}", version)
        if cached:
            return cached
            
        if name not in self.templates:
            return None
            
        # Start with base template
        resolved = self.templates[name].copy()
        
        # Handle inheritance
        if 'extends' in resolved:
            parent_name = resolved['extends']
            parent = self._resolve_template(parent_name)
            
            if parent:
                # Merge with parent
                merged = parent.copy()
                merged.update(resolved)
                
                # Merge template strings
                if 'template' in parent and 'template' in resolved:
                    # Use Jinja2 template inheritance
                    parent_template = f"{{% raw %}}{parent['template']}{{% endraw %}}"
                    child_template = resolved['template']
                    
                    merged['template'] = f"""
{{% extends "{parent_name}_base" %}}
{child_template}
"""
                    
                resolved = merged
                
        # Handle includes
        if 'includes' in resolved:
            includes_content = []
            
            for include_name in resolved['includes']:
                include_data = self._resolve_template(include_name)
                if include_data and 'template' in include_data:
                    includes_content.append(include_data['template'])
                    
            if includes_content:
                resolved['template'] = '\n'.join(includes_content) + '\n' + resolved.get('template', '')
                
        # Cache resolved template
        self.cache.set(f"resolved_{name}", resolved, version)
        
        return resolved
        
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with context."""
        template = self.get_template(template_name)
        
        # Add template metadata to context
        template_data = self._resolve_template(template_name)
        context['_template'] = {
            'name': template_name,
            'version': template_data.get('version', '1.0.0'),
            'agent': template_data.get('agent', 'general-purpose'),
            'language': template_data.get('language', 'en'),
        }
        
        return template.render(**context)
        
    def validate_template(self, template_name: str) -> Tuple[bool, List[str]]:
        """Validate template syntax and structure."""
        errors = []
        
        try:
            # Check if template exists
            if template_name not in self.templates:
                errors.append(f"Template '{template_name}' not found")
                return False, errors
                
            template_data = self.templates[template_name]
            
            # Validate required fields
            required_fields = ['name', 'template']
            for field in required_fields:
                if field not in template_data:
                    errors.append(f"Missing required field: {field}")
                    
            # Validate template syntax
            if 'template' in template_data:
                try:
                    self.env.from_string(template_data['template'])
                except TemplateSyntaxError as e:
                    errors.append(f"Template syntax error: {e}")
                    
            # Check undefined variables
            if 'template' in template_data:
                ast = self.env.parse(template_data['template'])
                undefined = meta.find_undeclared_variables(ast)
                
                # Common variables that should be available
                common_vars = {
                    'error_text', 'error_type', 'error_count', 'files',
                    'line_numbers', 'error_codes', 'error_messages',
                    'stack_trace', 'recommended_agent', 'severity',
                }
                
                undefined_vars = undefined - common_vars
                if undefined_vars:
                    errors.append(f"Undefined variables: {', '.join(undefined_vars)}")
                    
            # Validate dependencies
            if 'extends' in template_data:
                if template_data['extends'] not in self.templates:
                    errors.append(f"Parent template '{template_data['extends']}' not found")
                    
            if 'includes' in template_data:
                for include in template_data['includes']:
                    if include not in self.templates:
                        errors.append(f"Include template '{include}' not found")
                        
        except Exception as e:
            errors.append(f"Validation error: {e}")
            
        return len(errors) == 0, errors
        
    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available templates."""
        templates = []
        
        for name, data in self.templates.items():
            if category and data.get('category') != category:
                continue
                
            templates.append({
                'name': name,
                'display_name': data.get('name', name),
                'description': data.get('description', ''),
                'category': data.get('category', 'general'),
                'version': data.get('version', '1.0.0'),
                'agent': data.get('agent', 'general-purpose'),
                'language': data.get('language', 'en'),
                'tags': data.get('tags', []),
            })
            
        return sorted(templates, key=lambda x: x['name'])
        
    def export_template(self, template_name: str, output_path: Path):
        """Export a template to file."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
            
        template_data = self.templates[template_name]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(template_data, f, allow_unicode=True, sort_keys=False)
            
    def import_template(self, input_path: Path, name: Optional[str] = None):
        """Import a template from file."""
        with open(input_path, 'r', encoding='utf-8') as f:
            template_data = yaml.safe_load(f)
            
        template_name = name or input_path.stem
        
        # Save to user templates directory
        user_dir = Path.home() / '.ccdebug' / 'templates'
        user_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = user_dir / f"{template_name}.yaml"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(template_data, f, allow_unicode=True, sort_keys=False)
            
        # Reload template
        self.reload_template(output_path)