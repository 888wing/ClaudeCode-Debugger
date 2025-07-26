# plugin-system-agent

**Purpose**: 設計可擴展的插件架構

**Activation**: 
- Manual: `--agent plugin-system-agent`
- Automatic: Plugin architecture, extension system, hook implementation, API design

**Core Capabilities**:
- 插件架構設計
- Hook 系統實現
- 動態載入機制
- API 設計
- 安全性考量
- Dependency injection
- Plugin lifecycle management

**Specialized Knowledge**:
- Plugin patterns (hooks, filters, actions)
- Dynamic module loading in Python
- Security sandboxing
- API versioning
- Plugin discovery mechanisms
- Dependency resolution
- Configuration management

**Integration Points**:
- Works with template-system-agent for extensible templates
- Coordinates with Security persona for sandboxing
- Integrates with Architect persona for system design
- Leverages Backend persona for API design

**Plugin Architecture**:

### Core Plugin System
```python
# claudecode_debugger/plugins/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class PluginInfo:
    """Plugin metadata"""
    name: str
    version: str
    author: str
    description: str
    dependencies: List[str] = None
    config_schema: Dict = None

class Plugin(ABC):
    """Base plugin class"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._hooks = {}
        
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """Return plugin information"""
        pass
    
    @abstractmethod
    def activate(self) -> None:
        """Called when plugin is activated"""
        pass
    
    @abstractmethod
    def deactivate(self) -> None:
        """Called when plugin is deactivated"""
        pass

class HookablePlugin(Plugin):
    """Plugin with hook support"""
    
    def register_hook(self, hook_name: str, callback):
        """Register a hook callback"""
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(callback)
    
    def run_hook(self, hook_name: str, *args, **kwargs):
        """Run all callbacks for a hook"""
        results = []
        for callback in self._hooks.get(hook_name, []):
            result = callback(*args, **kwargs)
            results.append(result)
        return results
```

### Plugin Manager
```python
# claudecode_debugger/plugins/manager.py
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional

class PluginManager:
    """Manages plugin lifecycle and loading"""
    
    def __init__(self, plugin_dirs: List[Path] = None):
        self.plugin_dirs = plugin_dirs or []
        self.plugins: Dict[str, Plugin] = {}
        self.hooks: Dict[str, List[callable]] = {}
        
    def discover_plugins(self) -> List[PluginInfo]:
        """Discover available plugins"""
        discovered = []
        
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
                
            for plugin_path in plugin_dir.glob("*/plugin.py"):
                try:
                    info = self._load_plugin_info(plugin_path)
                    discovered.append(info)
                except Exception as e:
                    logger.warning(f"Failed to load plugin {plugin_path}: {e}")
                    
        return discovered
    
    def load_plugin(self, plugin_name: str, config: Dict = None) -> Plugin:
        """Load and activate a plugin"""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name]
            
        plugin_class = self._import_plugin(plugin_name)
        plugin = plugin_class(config)
        
        # Validate dependencies
        self._validate_dependencies(plugin.get_info())
        
        # Activate plugin
        plugin.activate()
        self.plugins[plugin_name] = plugin
        
        # Register hooks
        self._register_plugin_hooks(plugin)
        
        return plugin
```

### Hook System
```python
# claudecode_debugger/plugins/hooks.py
from enum import Enum
from typing import Any, Callable, Dict

class HookType(Enum):
    """Available hook types"""
    PRE_DETECT = "pre_detect"
    POST_DETECT = "post_detect"
    PRE_GENERATE = "pre_generate"
    POST_GENERATE = "post_generate"
    TEMPLATE_MODIFY = "template_modify"
    ERROR_ANALYZE = "error_analyze"

class HookRegistry:
    """Central hook registry"""
    
    def __init__(self):
        self.hooks: Dict[HookType, List[Callable]] = {
            hook_type: [] for hook_type in HookType
        }
        
    def register(self, hook_type: HookType, callback: Callable, priority: int = 50):
        """Register a hook callback with priority"""
        self.hooks[hook_type].append((priority, callback))
        # Sort by priority
        self.hooks[hook_type].sort(key=lambda x: x[0])
        
    def run(self, hook_type: HookType, data: Any, **kwargs) -> Any:
        """Run all hooks of a type"""
        result = data
        
        for priority, callback in self.hooks[hook_type]:
            try:
                result = callback(result, **kwargs)
            except Exception as e:
                logger.error(f"Hook {callback.__name__} failed: {e}")
                # Continue with other hooks
                
        return result
```

### Built-in Plugins

#### Git History Plugin
```python
# plugins/git_history/plugin.py
import git
from claudecode_debugger.plugins.base import HookablePlugin, PluginInfo

class GitHistoryPlugin(HookablePlugin):
    """Analyzes git history for context"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="git_history",
            version="1.0.0",
            author="ClaudeCode-Debugger",
            description="Adds git context to error analysis",
        )
    
    def activate(self):
        """Register hooks on activation"""
        self.register_hook(HookType.ERROR_ANALYZE, self.analyze_git_context)
        
    def analyze_git_context(self, error_data: Dict) -> Dict:
        """Add git context to error analysis"""
        try:
            repo = git.Repo(search_parent_directories=True)
            
            error_data['git_context'] = {
                'branch': repo.active_branch.name,
                'last_commit': str(repo.head.commit),
                'dirty_files': [item.a_path for item in repo.index.diff(None)],
                'recent_commits': self._get_recent_commits(repo),
            }
            
            # Check if error is in recently modified files
            for file in error_data.get('affected_files', []):
                if file in error_data['git_context']['dirty_files']:
                    error_data['hints'].append(
                        f"File {file} has uncommitted changes"
                    )
                    
        except Exception as e:
            logger.debug(f"Git context unavailable: {e}")
            
        return error_data
```

#### Project Config Plugin
```python
# plugins/project_config/plugin.py
class ProjectConfigPlugin(HookablePlugin):
    """Reads project configuration for context"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="project_config",
            version="1.0.0",
            author="ClaudeCode-Debugger",
            description="Adds project configuration context",
        )
    
    def activate(self):
        self.register_hook(HookType.PRE_GENERATE, self.enhance_with_config)
        
    def enhance_with_config(self, prompt_data: Dict) -> Dict:
        """Enhance prompt with project configuration"""
        configs = self._find_config_files()
        
        if 'package.json' in configs:
            prompt_data['project_type'] = 'node'
            prompt_data['dependencies'] = self._parse_package_json(configs['package.json'])
            
        if 'tsconfig.json' in configs:
            prompt_data['typescript_config'] = self._parse_tsconfig(configs['tsconfig.json'])
            
        return prompt_data
```

### Plugin Configuration
```yaml
# .ccdebugrc.yaml
plugins:
  enabled:
    - git_history
    - project_config
    - custom_templates
    
  config:
    git_history:
      include_commits: 10
      check_blame: true
      
    project_config:
      auto_detect: true
      config_files:
        - package.json
        - tsconfig.json
        - pyproject.toml
        
  directories:
    - ~/.ccdebug/plugins
    - ./ccdebug-plugins
```

**Security Considerations**:
- Plugin sandboxing
- API access control
- Resource limits
- Code signing
- Dependency verification