"""Plugin system for ClaudeCode-Debugger."""

import importlib
import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
import json


class Plugin(ABC):
    """Base class for all plugins."""
    
    def __init__(self):
        """Initialize plugin."""
        self.name = self.__class__.__name__
        self.enabled = True
        
    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze error data and return insights."""
        pass
        
    @abstractmethod
    def get_description(self) -> str:
        """Return plugin description."""
        pass
        
    def get_version(self) -> str:
        """Return plugin version."""
        return "1.0.0"
        
    def get_requirements(self) -> List[str]:
        """Return list of required dependencies."""
        return []
        
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data."""
        return 'error_content' in data and 'error_type' in data
        
    def format_output(self, results: Dict[str, Any]) -> str:
        """Format plugin output for display."""
        return json.dumps(results, indent=2)


class PluginManager:
    """Manages plugin lifecycle and execution."""
    
    def __init__(self, plugin_dir: Optional[Path] = None):
        """Initialize plugin manager."""
        if plugin_dir is None:
            plugin_dir = Path(__file__).parent
            
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Plugin] = {}
        self._discover_plugins()
        
    def _discover_plugins(self):
        """Discover and load available plugins."""
        # Built-in plugins
        self._load_builtin_plugins()
        
        # User plugins
        user_plugin_dir = Path.home() / '.ccdebug' / 'plugins'
        if user_plugin_dir.exists():
            self._load_user_plugins(user_plugin_dir)
            
    def _load_builtin_plugins(self):
        """Load built-in plugins."""
        builtin_plugins = [
            'stack_trace_analyzer',
            'dependency_analyzer',
            'performance_analyzer',
            'security_analyzer',
            'pattern_matcher',
            'ai_suggestions',
        ]
        
        for plugin_name in builtin_plugins:
            try:
                module = importlib.import_module(f'claudecode_debugger.plugins.{plugin_name}')
                
                # Find plugin class
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, Plugin) and 
                        obj != Plugin):
                        plugin = obj()
                        self.plugins[plugin_name] = plugin
                        break
                        
            except ImportError:
                pass  # Plugin not available
                
    def _load_user_plugins(self, plugin_dir: Path):
        """Load user-defined plugins."""
        for plugin_file in plugin_dir.glob('*.py'):
            if plugin_file.name.startswith('_'):
                continue
                
            try:
                spec = importlib.util.spec_from_file_location(
                    plugin_file.stem, 
                    plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find plugin class
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, Plugin) and 
                        obj != Plugin):
                        plugin = obj()
                        self.plugins[f"user_{plugin_file.stem}"] = plugin
                        break
                        
            except Exception as e:
                print(f"Failed to load plugin {plugin_file}: {e}")
                
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all available plugins."""
        result = []
        
        for name, plugin in self.plugins.items():
            result.append({
                'name': name,
                'class': plugin.name,
                'enabled': plugin.enabled,
                'description': plugin.get_description(),
                'version': plugin.get_version(),
                'requirements': plugin.get_requirements(),
            })
            
        return result
        
    def enable(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            return True
        return False
        
    def disable(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            return True
        return False
        
    def run_all(self, hook: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all enabled plugins for a specific hook."""
        results = {}
        
        for name, plugin in self.plugins.items():
            if not plugin.enabled:
                continue
                
            try:
                if hook == 'analyze' and plugin.validate_input(data):
                    result = plugin.analyze(data)
                    if result:
                        results[name] = result
                        
            except Exception as e:
                results[name] = {'error': str(e)}
                
        return results
        
    def run_plugin(self, plugin_name: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Run a specific plugin."""
        if plugin_name not in self.plugins:
            return None
            
        plugin = self.plugins[plugin_name]
        if not plugin.enabled:
            return None
            
        try:
            if plugin.validate_input(data):
                return plugin.analyze(data)
        except Exception as e:
            return {'error': str(e)}
            
        return None
        
    def register_plugin(self, plugin: Plugin, name: Optional[str] = None):
        """Register a plugin instance."""
        if name is None:
            name = plugin.__class__.__name__.lower()
            
        self.plugins[name] = plugin
        
    def unregister_plugin(self, name: str) -> bool:
        """Unregister a plugin."""
        if name in self.plugins:
            del self.plugins[name]
            return True
        return False
        
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a plugin instance."""
        return self.plugins.get(name)
        
    def reload_plugins(self):
        """Reload all plugins."""
        self.plugins.clear()
        self._discover_plugins()