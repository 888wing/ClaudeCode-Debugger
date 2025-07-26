"""Enhanced CLI interface for ClaudeCode-Debugger with advanced features."""

import sys
import json
import glob
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from collections import defaultdict
import configparser

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.tree import Tree
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich import box
from rich.columns import Columns
from rich.markdown import Markdown
from rich.traceback import install as install_rich_traceback

from .core.detector import ErrorDetector
from .core.generator import PromptGenerator
from .utils.clipboard import copy_to_clipboard, paste_from_clipboard
from .utils.history import HistoryManager
from .utils.config import ConfigManager
from .utils.formatters import OutputFormatter
from .plugins.base import PluginManager

# Install rich traceback for better error display
install_rich_traceback()

console = Console()

# Error type autocomplete choices
ERROR_TYPES = [
    'typescript', 'javascript', 'python', 'rust', 'go', 'java',
    'memory', 'network', 'permission', 'syntax', 'runtime',
    'build', 'test', 'deployment', 'database', 'api'
]

# Output format choices
OUTPUT_FORMATS = ['text', 'json', 'markdown', 'html', 'yaml']

# Clipboard format choices
CLIPBOARD_FORMATS = ['plain', 'markdown', 'code', 'json']


class CCDebugCLI:
    """Enhanced CLI for ClaudeCode-Debugger."""
    
    def __init__(self):
        """Initialize the enhanced CLI."""
        self.config = ConfigManager()
        self.history = HistoryManager()
        self.plugins = PluginManager()
        self.formatter = OutputFormatter()
        
    def run(self):
        """Main entry point for the CLI."""
        cli()


def error_type_completion(ctx, args, incomplete):
    """Provide autocompletion for error types."""
    return [t for t in ERROR_TYPES if t.startswith(incomplete)]


def output_format_completion(ctx, args, incomplete):
    """Provide autocompletion for output formats."""
    return [f for f in OUTPUT_FORMATS if f.startswith(incomplete)]


def clipboard_format_completion(ctx, args, incomplete):
    """Provide autocompletion for clipboard formats."""
    return [f for f in CLIPBOARD_FORMATS if f.startswith(incomplete)]


@click.group(invoke_without_command=True)
@click.pass_context
@click.argument('error', required=False)
@click.option('-f', '--file', 'files', multiple=True, 
              help='Read error from file(s). Supports wildcards.')
@click.option('-t', '--type', 'error_type', shell_complete=error_type_completion,
              help='Specify error type (auto-detect if not specified)')
@click.option('-c', '--copy', 'copy_format', shell_complete=clipboard_format_completion,
              help='Copy to clipboard with format (plain/markdown/code/json)')
@click.option('-o', '--output', 'output_path', type=click.Path(),
              help='Save to file')
@click.option('--format', 'output_format', shell_complete=output_format_completion,
              default='text', help='Output format (text/json/markdown/html/yaml)')
@click.option('-i', '--interactive', is_flag=True, help='Interactive mode')
@click.option('--history', is_flag=True, help='Show command history')
@click.option('--list-templates', is_flag=True, help='List available templates')
@click.option('--agent', help='Override default agent selection')
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
@click.option('--config', type=click.Path(exists=True), help='Use custom config file')
@click.option('--plugin', 'plugins', multiple=True, help='Enable specific plugins')
@click.option('--theme', default='default', help='Output theme (default/dark/light/custom)')
@click.option('--watch', is_flag=True, help='Watch mode for continuous monitoring')
@click.option('--batch', is_flag=True, help='Batch process multiple errors')
@click.option('--stats', is_flag=True, help='Show statistics')
def cli(ctx, error: Optional[str], files: tuple, error_type: Optional[str],
        copy_format: Optional[str], output_path: Optional[str], output_format: str,
        interactive: bool, history: bool, list_templates: bool, agent: Optional[str],
        verbose: bool, config: Optional[str], plugins: tuple, theme: str,
        watch: bool, batch: bool, stats: bool):
    """
    ClaudeCode-Debugger: Advanced debug prompt generator for Claude Code.
    
    Transform error messages into actionable debug prompts with AI-powered analysis.
    
    Examples:
    
        ccdebug "TypeError: Cannot read property"
        
        ccdebug -f error.log -c markdown
        
        ccdebug -f "logs/*.log" --batch -o report.json --format json
        
        ccdebug --interactive --theme dark
        
        ccdebug config set default.theme dark
        
        ccdebug history show --limit 10
    """
    
    # If a subcommand is provided, let Click handle it
    if ctx.invoked_subcommand is not None:
        return
    
    # Initialize CLI handler
    cli_handler = CCDebugCLI()
    
    # Load configuration
    if config:
        cli_handler.config.load_file(config)
    else:
        cli_handler.config.load_default()
        
    # Apply theme
    console.theme = cli_handler.config.get_theme(theme)
    
    # Enable plugins
    for plugin_name in plugins:
        cli_handler.plugins.enable(plugin_name)
    
    # Handle special commands
    if list_templates:
        _list_templates_enhanced(cli_handler)
        return
        
    if history:
        _show_history_enhanced(cli_handler)
        return
        
    if stats:
        _show_statistics(cli_handler)
        return
        
    if interactive:
        _interactive_mode_enhanced(cli_handler)
        return
        
    if watch:
        _watch_mode(cli_handler, files)
        return
        
    if batch and files:
        _batch_process(cli_handler, files, error_type, output_path, output_format)
        return
    
    # Get error content
    error_content = _get_error_content_enhanced(error, files)
    if not error_content:
        console.print("[red]Error: No error content provided.[/red]")
        console.print("Use --help for usage information.")
        sys.exit(1)
    
    # Process error with enhanced progress display
    result = _process_error_enhanced(
        cli_handler, error_content, error_type, agent, verbose
    )
    
    # Handle output with formatting
    _handle_output_enhanced(
        cli_handler, result, copy_format, output_path, output_format, verbose
    )
    
    # Save to history
    cli_handler.history.add_entry({
        'timestamp': datetime.now().isoformat(),
        'error_content': error_content[:500],  # Truncate for storage
        'error_type': result['error_type'],
        'severity': result['severity'],
        'agent': agent,
        'output_format': output_format
    })


@cli.group()
def config():
    """Manage configuration settings."""
    pass


@config.command()
@click.argument('key')
@click.argument('value')
def set(key: str, value: str):
    """Set a configuration value."""
    config_manager = ConfigManager()
    config_manager.set(key, value)
    console.print(f"[green]✓[/green] Set {key} = {value}")


@config.command()
@click.argument('key')
def get(key: str):
    """Get a configuration value."""
    config_manager = ConfigManager()
    value = config_manager.get(key)
    if value:
        console.print(f"{key} = {value}")
    else:
        console.print(f"[yellow]Key '{key}' not found[/yellow]")


@config.command()
def show():
    """Show all configuration settings."""
    config_manager = ConfigManager()
    settings = config_manager.get_all()
    
    table = Table(title="Configuration Settings", box=box.ROUNDED)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    
    for section in settings:
        for key, value in settings[section].items():
            table.add_row(f"{section}.{key}", str(value))
            
    console.print(table)


@cli.group()
def history():
    """Manage command history."""
    pass


@history.command()
@click.option('--limit', default=10, help='Number of entries to show')
@click.option('--filter', 'filter_type', help='Filter by error type')
def show(limit: int, filter_type: Optional[str]):
    """Show command history."""
    history_manager = HistoryManager()
    entries = history_manager.get_entries(limit=limit, filter_type=filter_type)
    
    if not entries:
        console.print("[yellow]No history entries found[/yellow]")
        return
        
    table = Table(title="Command History", box=box.ROUNDED)
    table.add_column("Time", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Severity", style="yellow")
    table.add_column("Error Preview", style="dim")
    
    for entry in entries:
        timestamp = datetime.fromisoformat(entry['timestamp'])
        time_str = timestamp.strftime("%Y-%m-%d %H:%M")
        preview = entry['error_content'][:50] + "..." if len(entry['error_content']) > 50 else entry['error_content']
        
        severity_color = {
            'critical': 'red',
            'high': 'yellow',
            'medium': 'blue',
            'low': 'green'
        }.get(entry['severity'], 'white')
        
        table.add_row(
            time_str,
            entry['error_type'],
            f"[{severity_color}]{entry['severity']}[/{severity_color}]",
            preview.replace('\n', ' ')
        )
        
    console.print(table)


@history.command()
def clear():
    """Clear command history."""
    if Confirm.ask("Are you sure you want to clear all history?"):
        history_manager = HistoryManager()
        history_manager.clear()
        console.print("[green]✓[/green] History cleared")


@cli.group()
def plugin():
    """Manage plugins."""
    pass


@plugin.command()
def list():
    """List available plugins."""
    plugin_manager = PluginManager()
    plugins = plugin_manager.list_plugins()
    
    table = Table(title="Available Plugins", box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Description", style="dim")
    
    for p in plugins:
        status = "✓ Enabled" if p['enabled'] else "✗ Disabled"
        status_color = "green" if p['enabled'] else "red"
        table.add_row(
            p['name'],
            f"[{status_color}]{status}[/{status_color}]",
            p['description']
        )
        
    console.print(table)


@plugin.command()
@click.argument('name')
def enable(name: str):
    """Enable a plugin."""
    plugin_manager = PluginManager()
    if plugin_manager.enable(name):
        console.print(f"[green]✓[/green] Plugin '{name}' enabled")
    else:
        console.print(f"[red]✗[/red] Failed to enable plugin '{name}'")


@plugin.command()
@click.argument('name')
def disable(name: str):
    """Disable a plugin."""
    plugin_manager = PluginManager()
    if plugin_manager.disable(name):
        console.print(f"[green]✓[/green] Plugin '{name}' disabled")
    else:
        console.print(f"[red]✗[/red] Failed to disable plugin '{name}'")


def _get_error_content_enhanced(error: Optional[str], files: tuple) -> str:
    """Get error content from various sources with wildcard support."""
    if files:
        contents = []
        for file_pattern in files:
            # Expand wildcards
            file_paths = glob.glob(file_pattern)
            if not file_paths:
                file_paths = [file_pattern]  # Try as literal path
                
            for file_path in file_paths:
                try:
                    content = Path(file_path).read_text(encoding='utf-8')
                    contents.append(f"=== File: {file_path} ===\n{content}")
                except Exception as e:
                    console.print(f"[red]Error reading {file_path}: {e}[/red]")
                    
        return "\n\n".join(contents) if contents else ""
        
    elif error:
        return error
    else:
        # Try to get from clipboard
        content = paste_from_clipboard()
        if content:
            console.print("[dim]Using content from clipboard...[/dim]")
            return content
        return ""


def _process_error_enhanced(cli_handler: CCDebugCLI, error_content: str, 
                           error_type: Optional[str], agent: Optional[str],
                           verbose: bool) -> Dict[str, Any]:
    """Process error with enhanced progress display and analysis."""
    result = {}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=True,
    ) as progress:
        # Create main task
        main_task = progress.add_task("Processing error...", total=100)
        
        # Step 1: Detect error type (20%)
        progress.update(main_task, description="Analyzing error type...", completed=0)
        detector = ErrorDetector()
        detected_type = error_type or detector.detect(error_content)
        error_info = detector.extract_key_info(error_content, detected_type)
        severity = detector.get_severity(error_content, detected_type)
        progress.update(main_task, completed=20)
        
        # Step 2: Run plugins (20%)
        progress.update(main_task, description="Running analysis plugins...")
        plugin_results = cli_handler.plugins.run_all('analyze', {
            'error_content': error_content,
            'error_type': detected_type,
            'error_info': error_info
        })
        progress.update(main_task, completed=40)
        
        # Step 3: Generate prompt (40%)
        progress.update(main_task, description="Generating debug prompt...")
        generator = PromptGenerator()
        prompt = generator.generate(
            error_content, 
            detected_type,
            error_info,
            custom_agent=agent,
            plugin_data=plugin_results
        )
        progress.update(main_task, completed=80)
        
        # Step 4: Finalize results (20%)
        progress.update(main_task, description="Finalizing analysis...")
        result = {
            'prompt': prompt,
            'error_type': detected_type,
            'severity': severity,
            'error_info': error_info,
            'plugin_results': plugin_results
        }
        progress.update(main_task, completed=100)
        
    return result


def _handle_output_enhanced(cli_handler: CCDebugCLI, result: Dict[str, Any],
                           copy_format: Optional[str], output_path: Optional[str],
                           output_format: str, verbose: bool):
    """Handle output with enhanced formatting options."""
    # Format the output
    formatted_output = cli_handler.formatter.format(result, output_format)
    
    # Display results with enhanced styling
    _display_results_enhanced(result, verbose)
    
    # Handle clipboard copy with format
    if copy_format:
        clipboard_content = cli_handler.formatter.format_for_clipboard(
            result['prompt'], copy_format
        )
        if copy_to_clipboard(clipboard_content):
            console.print(f"\n[bold green]✓[/bold green] Copied to clipboard as {copy_format}!")
        else:
            console.print("\n[bold red]✗[/bold red] Failed to copy to clipboard.")
            
    # Handle file output
    if output_path:
        try:
            Path(output_path).write_text(formatted_output, encoding='utf-8')
            console.print(f"\n[bold green]✓[/bold green] Saved to {output_path} as {output_format}")
        except Exception as e:
            console.print(f"\n[bold red]✗[/bold red] Failed to save: {e}")


def _display_results_enhanced(result: Dict[str, Any], verbose: bool):
    """Display analysis results with enhanced visualization."""
    # Severity colors and icons
    severity_config = {
        'critical': {'color': 'bold red', 'icon': '🚨'},
        'high': {'color': 'red', 'icon': '⚠️'},
        'medium': {'color': 'yellow', 'icon': '⚡'},
        'low': {'color': 'green', 'icon': 'ℹ️'},
    }
    
    config = severity_config.get(result['severity'], {'color': 'white', 'icon': '❓'})
    
    # Create layout
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=8 if verbose else 0)
    )
    
    # Header
    title = f"{config['icon']} {result['error_type'].title()} Error - {result['severity'].upper()} Priority"
    header_panel = Panel(
        Text(title, justify="center", style=config['color']),
        box=box.HEAVY,
        style=config['color'].split()[-1]
    )
    layout["header"].update(header_panel)
    
    # Body - Main prompt
    if len(result['prompt']) > 2000:
        # Use syntax highlighting for long prompts
        body_content = Syntax(result['prompt'], "markdown", theme="monokai", line_numbers=False)
    else:
        body_content = Markdown(result['prompt'])
        
    body_panel = Panel(
        body_content,
        title="Debug Prompt",
        border_style=config['color'].split()[-1],
        padding=(1, 2),
    )
    layout["body"].update(body_panel)
    
    # Footer - Additional info in verbose mode
    if verbose:
        footer_content = _create_verbose_info(result)
        layout["footer"].update(footer_content)
        
    console.print(layout)


def _create_verbose_info(result: Dict[str, Any]) -> Panel:
    """Create verbose information panel."""
    info_tree = Tree("Analysis Details")
    
    # Basic info
    basic = info_tree.add("Basic Information")
    basic.add(f"Error Type: {result['error_type']}")
    basic.add(f"Severity: {result['severity']}")
    
    # Error info details
    if result['error_info']:
        error_details = info_tree.add("Extracted Information")
        
        if result['error_info'].get('files'):
            files_branch = error_details.add("Files")
            for file in result['error_info']['files']:
                files_branch.add(file)
                
        if result['error_info'].get('error_codes'):
            codes_branch = error_details.add("Error Codes")
            for code in result['error_info']['error_codes']:
                codes_branch.add(code)
                
        if result['error_info'].get('line_numbers'):
            lines_branch = error_details.add("Line Numbers")
            for line in result['error_info']['line_numbers']:
                lines_branch.add(str(line))
                
    # Plugin results
    if result.get('plugin_results'):
        plugins_branch = info_tree.add("Plugin Analysis")
        for plugin_name, plugin_data in result['plugin_results'].items():
            plugin_branch = plugins_branch.add(plugin_name)
            if isinstance(plugin_data, dict):
                for key, value in plugin_data.items():
                    plugin_branch.add(f"{key}: {value}")
            else:
                plugin_branch.add(str(plugin_data))
                
    return Panel(info_tree, title="Detailed Analysis", border_style="blue")


def _interactive_mode_enhanced(cli_handler: CCDebugCLI):
    """Enhanced interactive mode with better UX."""
    console.print(Panel(
        "[bold cyan]ClaudeCode-Debugger Interactive Mode[/bold cyan]\n\n"
        "Enter your error message below. Press [bold]Ctrl+D[/bold] to analyze.\n"
        "Type [bold]'help'[/bold] for commands or [bold]'exit'[/bold] to quit.",
        title="Welcome",
        border_style="cyan"
    ))
    
    while True:
        console.print("\n[bold cyan]>[/bold cyan] ", end="")
        
        try:
            # Multi-line input
            lines = []
            first_line = input()
            
            # Check for commands
            if first_line.lower() == 'exit':
                break
            elif first_line.lower() == 'help':
                _show_interactive_help()
                continue
            elif first_line.lower() == 'clear':
                console.clear()
                continue
                
            lines.append(first_line)
            
            # Continue reading until Ctrl+D
            if first_line:
                console.print("[dim]... (Press Ctrl+D to analyze)[/dim]")
                while True:
                    line = input()
                    lines.append(line)
                    
        except EOFError:
            pass
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled[/yellow]")
            continue
            
        error_content = '\n'.join(lines)
        
        if not error_content.strip():
            console.print("[red]No error content provided.[/red]")
            continue
            
        # Process the error
        console.print("\n" + "─" * console.width + "\n")
        
        with console.status("Analyzing error...", spinner="dots"):
            result = _process_error_enhanced(cli_handler, error_content, None, None, True)
            
        _display_results_enhanced(result, verbose=True)
        
        # Interactive options
        console.print("\n[bold]Options:[/bold]")
        console.print("  [cyan]c[/cyan] - Copy to clipboard")
        console.print("  [cyan]s[/cyan] - Save to file")
        console.print("  [cyan]r[/cyan] - Re-analyze with different settings")
        console.print("  [cyan]n[/cyan] - New error")
        console.print("  [cyan]q[/cyan] - Quit")
        
        choice = Prompt.ask("Choose an option", choices=['c', 's', 'r', 'n', 'q'], default='n')
        
        if choice == 'c':
            format_choice = Prompt.ask("Format", choices=CLIPBOARD_FORMATS, default='markdown')
            clipboard_content = cli_handler.formatter.format_for_clipboard(
                result['prompt'], format_choice
            )
            if copy_to_clipboard(clipboard_content):
                console.print("[bold green]✓[/bold green] Copied to clipboard!")
                
        elif choice == 's':
            filename = Prompt.ask("Filename", default="debug_prompt.md")
            format_choice = Prompt.ask("Format", choices=OUTPUT_FORMATS, default='markdown')
            formatted_output = cli_handler.formatter.format(result, format_choice)
            try:
                Path(filename).write_text(formatted_output, encoding='utf-8')
                console.print(f"[bold green]✓[/bold green] Saved to {filename}")
            except Exception as e:
                console.print(f"[bold red]✗[/bold red] Failed to save: {e}")
                
        elif choice == 'r':
            error_type = Prompt.ask("Error type (leave empty for auto)", default="")
            agent = Prompt.ask("Agent override (leave empty for default)", default="")
            
            with console.status("Re-analyzing error...", spinner="dots"):
                result = _process_error_enhanced(
                    cli_handler, error_content, 
                    error_type if error_type else None,
                    agent if agent else None,
                    True
                )
                
            _display_results_enhanced(result, verbose=True)
            
        elif choice == 'q':
            break


def _show_interactive_help():
    """Show help for interactive mode."""
    help_text = """
[bold cyan]Interactive Mode Commands:[/bold cyan]

[bold]During input:[/bold]
  • Type or paste your error message
  • Press [cyan]Ctrl+D[/cyan] to analyze the error
  • Press [cyan]Ctrl+C[/cyan] to cancel input

[bold]Commands:[/bold]
  • [cyan]help[/cyan]  - Show this help message
  • [cyan]clear[/cyan] - Clear the screen
  • [cyan]exit[/cyan]  - Exit interactive mode

[bold]After analysis:[/bold]
  • [cyan]c[/cyan] - Copy prompt to clipboard
  • [cyan]s[/cyan] - Save prompt to file
  • [cyan]r[/cyan] - Re-analyze with different settings
  • [cyan]n[/cyan] - Analyze a new error
  • [cyan]q[/cyan] - Quit interactive mode
"""
    console.print(Panel(help_text, title="Help", border_style="green"))


def _watch_mode(cli_handler: CCDebugCLI, files: tuple):
    """Watch files for changes and analyze errors automatically."""
    console.print(Panel(
        "[bold cyan]Watch Mode[/bold cyan]\n\n"
        f"Watching {len(files)} file(s) for changes...\n"
        "Press [bold]Ctrl+C[/bold] to stop.",
        title="Watch Mode Active",
        border_style="cyan"
    ))
    
    # Implementation would use watchdog or similar library
    console.print("[yellow]Watch mode implementation pending...[/yellow]")


def _batch_process(cli_handler: CCDebugCLI, files: tuple, error_type: Optional[str],
                  output_path: Optional[str], output_format: str):
    """Process multiple error files in batch."""
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        # Expand all file patterns
        all_files = []
        for pattern in files:
            all_files.extend(glob.glob(pattern))
            
        if not all_files:
            console.print("[red]No files found matching patterns[/red]")
            return
            
        task = progress.add_task(f"Processing {len(all_files)} files...", total=len(all_files))
        
        for file_path in all_files:
            progress.update(task, description=f"Processing {Path(file_path).name}...")
            
            try:
                content = Path(file_path).read_text(encoding='utf-8')
                result = _process_error_enhanced(cli_handler, content, error_type, None, False)
                result['source_file'] = file_path
                results.append(result)
            except Exception as e:
                console.print(f"[red]Error processing {file_path}: {e}[/red]")
                
            progress.advance(task)
            
    # Display summary
    console.print(f"\n[bold green]Processed {len(results)} files[/bold green]")
    
    # Create summary table
    table = Table(title="Batch Processing Results", box=box.ROUNDED)
    table.add_column("File", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Severity", style="yellow")
    table.add_column("Status", style="green")
    
    for result in results:
        severity_color = {
            'critical': 'red',
            'high': 'yellow',
            'medium': 'blue',
            'low': 'green'
        }.get(result['severity'], 'white')
        
        table.add_row(
            Path(result['source_file']).name,
            result['error_type'],
            f"[{severity_color}]{result['severity']}[/{severity_color}]",
            "✓ Processed"
        )
        
    console.print(table)
    
    # Save batch results
    if output_path:
        batch_output = cli_handler.formatter.format_batch(results, output_format)
        try:
            Path(output_path).write_text(batch_output, encoding='utf-8')
            console.print(f"\n[bold green]✓[/bold green] Batch results saved to {output_path}")
        except Exception as e:
            console.print(f"\n[bold red]✗[/bold red] Failed to save: {e}")


def _show_statistics(cli_handler: CCDebugCLI):
    """Show usage statistics."""
    stats = cli_handler.history.get_statistics()
    
    # Create statistics dashboard
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="stats", size=10),
        Layout(name="charts", size=15)
    )
    
    # Header
    layout["header"].update(Panel(
        Text("ClaudeCode-Debugger Statistics", justify="center", style="bold cyan"),
        box=box.HEAVY
    ))
    
    # Statistics table
    stats_table = Table(box=box.ROUNDED)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")
    
    stats_table.add_row("Total Errors Analyzed", str(stats.get('total', 0)))
    stats_table.add_row("Unique Error Types", str(len(stats.get('types', {}))))
    stats_table.add_row("Critical Errors", str(stats.get('critical_count', 0)))
    stats_table.add_row("Success Rate", f"{stats.get('success_rate', 0):.1f}%")
    
    layout["stats"].update(Panel(stats_table, title="Summary"))
    
    # Error type distribution
    if stats.get('types'):
        type_chart = Table(title="Error Type Distribution", box=box.SIMPLE)
        type_chart.add_column("Type", style="magenta")
        type_chart.add_column("Count", style="yellow")
        type_chart.add_column("Percentage", style="cyan")
        
        total = sum(stats['types'].values())
        for error_type, count in sorted(stats['types'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            bar = "█" * int(percentage / 2)
            type_chart.add_row(
                error_type,
                str(count),
                f"{bar} {percentage:.1f}%"
            )
            
        layout["charts"].update(Panel(type_chart))
    
    console.print(layout)


def _list_templates_enhanced(cli_handler: CCDebugCLI):
    """List available templates with enhanced display."""
    generator = PromptGenerator()
    templates = generator.list_templates()
    
    # Group templates by category
    categorized = defaultdict(list)
    for template in templates:
        if template.startswith('user_'):
            categorized['User Templates'].append(template[5:])
        elif template.startswith('error_'):
            categorized['Error Templates'].append(template[6:])
        elif template.startswith('agent_'):
            categorized['Agent Templates'].append(template[6:])
        else:
            categorized['General Templates'].append(template)
    
    # Create tree view
    tree = Tree("[bold cyan]Available Templates[/bold cyan]")
    
    for category, items in sorted(categorized.items()):
        branch = tree.add(f"[yellow]{category}[/yellow] ({len(items)})")
        for item in sorted(items):
            branch.add(f"[green]•[/green] {item}")
            
    console.print(tree)
    console.print(f"\n[dim]Total: {len(templates)} templates[/dim]")


def _show_history_enhanced(cli_handler: CCDebugCLI):
    """Show enhanced history view."""
    entries = cli_handler.history.get_entries(limit=20)
    
    if not entries:
        console.print(Panel(
            "[yellow]No history entries found[/yellow]\n\n"
            "Start analyzing errors to build your history.",
            title="History Empty",
            border_style="yellow"
        ))
        return
        
    # Create history timeline
    console.print(Panel(
        Text("Command History Timeline", justify="center", style="bold cyan"),
        box=box.HEAVY
    ))
    
    current_date = None
    
    for entry in entries:
        timestamp = datetime.fromisoformat(entry['timestamp'])
        date_str = timestamp.strftime("%Y-%m-%d")
        
        # Show date header
        if date_str != current_date:
            current_date = date_str
            console.print(f"\n[bold blue]{date_str}[/bold blue]")
            console.print("─" * 40)
            
        # Entry details
        time_str = timestamp.strftime("%H:%M:%S")
        severity_color = {
            'critical': 'red',
            'high': 'yellow',
            'medium': 'blue',
            'low': 'green'
        }.get(entry['severity'], 'white')
        
        console.print(
            f"  [dim]{time_str}[/dim] "
            f"[{severity_color}]●[/{severity_color}] "
            f"[cyan]{entry['error_type']}[/cyan] - "
            f"{entry['error_content'][:60]}..."
        )


if __name__ == '__main__':
    cli()