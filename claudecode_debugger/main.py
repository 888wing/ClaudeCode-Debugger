"""Main entry point for ClaudeCode-Debugger with advanced features."""

import click
from rich.console import Console
from .cli_enhanced import create_app
from .core.advanced_detector import AdvancedErrorDetector
from .templates.generator import AdvancedPromptGenerator
from .utils.config import Config, init_config
from .utils.history import HistoryManager
from .plugins.base import PluginManager

console = Console()

def initialize_app():
    """Initialize the application with all components."""
    # Initialize configuration
    config = init_config()
    
    # Initialize history manager
    history = HistoryManager()
    
    # Initialize plugin manager
    plugins = PluginManager()
    plugins.load_plugins()
    
    # Initialize advanced components
    detector = AdvancedErrorDetector()
    generator = AdvancedPromptGenerator()
    
    return {
        'config': config,
        'history': history,
        'plugins': plugins,
        'detector': detector,
        'generator': generator
    }

@click.command()
@click.option('--use-legacy', is_flag=True, help='Use legacy CLI instead of enhanced version')
@click.pass_context
def main(ctx, use_legacy):
    """
    ClaudeCode-Debugger: Intelligent error analysis and debug prompt generation.
    
    This is the main entry point that routes to either legacy or enhanced CLI.
    """
    if use_legacy:
        # Import and run legacy CLI
        from .cli import main as legacy_main
        ctx.invoke(legacy_main)
    else:
        # Initialize and run enhanced CLI
        components = initialize_app()
        app = create_app(**components)
        app()

if __name__ == '__main__':
    main()