"""Configuration management for ClaudeCode-Debugger."""

import json
import configparser
from pathlib import Path
from typing import Dict, Any, Optional
from rich.theme import Theme


class ConfigManager:
    """Manages application configuration."""
    
    DEFAULT_CONFIG = {
        'general': {
            'theme': 'default',
            'verbose': False,
            'auto_copy': False,
            'default_format': 'markdown',
            'history_limit': 100,
        },
        'output': {
            'max_width': 120,
            'syntax_theme': 'monokai',
            'show_line_numbers': False,
            'wrap_code': True,
        },
        'clipboard': {
            'default_format': 'markdown',
            'include_metadata': False,
            'include_timestamp': True,
        },
        'plugins': {
            'auto_enable': [],
            'disabled': [],
        },
        'agents': {
            'default': 'auto',
            'prefer_specialized': True,
        },
        'advanced': {
            'cache_ttl': 3600,
            'max_file_size': 1048576,  # 1MB
            'batch_size': 10,
            'parallel_processing': True,
        }
    }
    
    THEMES = {
        'default': Theme({
            'info': 'cyan',
            'warning': 'yellow',
            'error': 'bold red',
            'success': 'bold green',
            'critical': 'bold red on yellow',
        }),
        'dark': Theme({
            'info': 'bright_cyan',
            'warning': 'bright_yellow',
            'error': 'bright_red',
            'success': 'bright_green',
            'critical': 'bright_red on bright_yellow',
        }),
        'light': Theme({
            'info': 'blue',
            'warning': 'yellow',
            'error': 'red',
            'success': 'green',
            'critical': 'red on yellow',
        }),
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager."""
        if config_path is None:
            config_path = Path.home() / '.ccdebug' / 'config.ini'
            
        self.config_path = config_path
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.config = configparser.ConfigParser()
        self._load_or_create()
        
    def _load_or_create(self):
        """Load existing config or create default."""
        if self.config_path.exists():
            self.config.read(self.config_path)
            self._migrate_config()
        else:
            self._create_default()
            
    def _create_default(self):
        """Create default configuration."""
        for section, values in self.DEFAULT_CONFIG.items():
            self.config[section] = {}
            for key, value in values.items():
                if isinstance(value, list):
                    self.config[section][key] = json.dumps(value)
                else:
                    self.config[section][key] = str(value)
                    
        self.save()
        
    def _migrate_config(self):
        """Migrate old config versions to current format."""
        # Add any missing sections/keys
        changed = False
        
        for section, values in self.DEFAULT_CONFIG.items():
            if section not in self.config:
                self.config[section] = {}
                changed = True
                
            for key, default_value in values.items():
                if key not in self.config[section]:
                    if isinstance(default_value, list):
                        self.config[section][key] = json.dumps(default_value)
                    else:
                        self.config[section][key] = str(default_value)
                    changed = True
                    
        if changed:
            self.save()
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        section, _, option = key.partition('.')
        
        if not option:
            # If no section specified, search all sections
            for sec in self.config.sections():
                if key in self.config[sec]:
                    return self._parse_value(self.config[sec][key])
            return default
            
        if section in self.config and option in self.config[section]:
            return self._parse_value(self.config[section][option])
            
        return default
        
    def set(self, key: str, value: Any):
        """Set a configuration value."""
        section, _, option = key.partition('.')
        
        if not option:
            raise ValueError("Key must be in format 'section.option'")
            
        if section not in self.config:
            self.config[section] = {}
            
        if isinstance(value, list):
            self.config[section][option] = json.dumps(value)
        else:
            self.config[section][option] = str(value)
            
        self.save()
        
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Get all configuration values."""
        result = {}
        
        for section in self.config.sections():
            result[section] = {}
            for key, value in self.config[section].items():
                result[section][key] = self._parse_value(value)
                
        return result
        
    def reset(self, section: Optional[str] = None):
        """Reset configuration to defaults."""
        if section:
            if section in self.DEFAULT_CONFIG:
                self.config[section] = {}
                for key, value in self.DEFAULT_CONFIG[section].items():
                    if isinstance(value, list):
                        self.config[section][key] = json.dumps(value)
                    else:
                        self.config[section][key] = str(value)
        else:
            self.config.clear()
            self._create_default()
            
        self.save()
        
    def save(self):
        """Save configuration to disk."""
        with open(self.config_path, 'w') as f:
            self.config.write(f)
            
    def load_file(self, path: Path):
        """Load configuration from a specific file."""
        if path.exists():
            self.config.read(path)
            self._migrate_config()
        else:
            raise FileNotFoundError(f"Config file not found: {path}")
            
    def load_default(self):
        """Load default configuration."""
        self._load_or_create()
        
    def export(self, path: Path):
        """Export configuration to a file."""
        with open(path, 'w') as f:
            self.config.write(f)
            
    def get_theme(self, name: str) -> Theme:
        """Get a theme by name."""
        if name == 'custom':
            # Load custom theme from config
            return self._load_custom_theme()
        return self.THEMES.get(name, self.THEMES['default'])
        
    def _load_custom_theme(self) -> Theme:
        """Load custom theme from configuration."""
        theme_config = {}
        
        if 'theme.custom' in self.config:
            for key, value in self.config['theme.custom'].items():
                theme_config[key] = value
                
        return Theme(theme_config or self.THEMES['default'].styles)
        
    def _parse_value(self, value: str) -> Any:
        """Parse a configuration value."""
        # Try to parse as JSON first (for lists)
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
            
        # Try to parse as boolean
        if value.lower() in ('true', 'yes', 'on', '1'):
            return True
        elif value.lower() in ('false', 'no', 'off', '0'):
            return False
            
        # Try to parse as int
        try:
            return int(value)
        except ValueError:
            pass
            
        # Try to parse as float
        try:
            return float(value)
        except ValueError:
            pass
            
        # Return as string
        return value
        
    def validate(self) -> List[str]:
        """Validate configuration and return any issues."""
        issues = []
        
        # Check theme
        theme = self.get('general.theme')
        if theme not in self.THEMES and theme != 'custom':
            issues.append(f"Unknown theme: {theme}")
            
        # Check numeric values
        for key, min_val, max_val in [
            ('general.history_limit', 1, 10000),
            ('advanced.cache_ttl', 0, 86400),
            ('advanced.max_file_size', 1024, 104857600),  # 1KB - 100MB
            ('advanced.batch_size', 1, 100),
        ]:
            value = self.get(key)
            if value is not None:
                if value < min_val or value > max_val:
                    issues.append(f"{key} must be between {min_val} and {max_val}")
                    
        # Check output format
        format_value = self.get('general.default_format')
        if format_value not in ['text', 'json', 'markdown', 'html', 'yaml']:
            issues.append(f"Unknown output format: {format_value}")
            
        return issues