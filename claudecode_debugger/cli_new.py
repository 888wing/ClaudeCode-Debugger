"""Enhanced CLI interface with i18n and advanced analysis."""

import sys
from pathlib import Path
from typing import Dict, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.syntax import Syntax

from .core.detector import ErrorDetector
from .core.generator import PromptGenerator
from .utils.clipboard import copy_to_clipboard, paste_from_clipboard
from .i18n import get_translator
from .analyzers import StackTraceAnalyzer, PatternAnalyzer, CodeContextAnalyzer
from .suggestions import SuggestionEngine


console = Console()


@click.command()
@click.argument("error", required=False)
@click.option("-f", "--file", type=click.Path(exists=True), help="Read error from file")
@click.option("-t", "--type", "error_type", help="Error type (auto-detect if not specified)")
@click.option("-c", "--copy", is_flag=True, help="Copy to clipboard")
@click.option("-o", "--output", type=click.Path(), help="Save to file")
@click.option("-i", "--interactive", is_flag=True, help="Interactive mode")
@click.option("--history", is_flag=True, help="Show history")
@click.option("--list-templates", is_flag=True, help="List available templates")
@click.option("--agent", help="Override default agent selection")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
@click.option("--lang", type=click.Choice(['en', 'zh']), help="Language (en/zh)")
@click.option("--analyze-stack", is_flag=True, help="Perform deep stack trace analysis")
@click.option("--suggest", is_flag=True, help="Show intelligent suggestions")
@click.option("--context", type=click.Path(exists=True), help="Analyze code context from file")
def cli(
    error: Optional[str],
    file: Optional[str],
    error_type: Optional[str],
    copy: bool,
    output: Optional[str],
    interactive: bool,
    history: bool,
    list_templates: bool,
    agent: Optional[str],
    verbose: bool,
    lang: Optional[str],
    analyze_stack: bool,
    suggest: bool,
    context: Optional[str],
):
    """
    ClaudeCode-Debugger: Smart debug prompt generator with multi-language support.

    Transform error messages into actionable debug prompts with AI-powered analysis.

    Examples:

        ccdebug "TypeError: Cannot read property" --lang zh

        ccdebug -f error.log -c --analyze-stack

        ccdebug --interactive --suggest
    """
    
    # Initialize translator
    _ = get_translator(lang)
    
    # Handle special commands
    if list_templates:
        _list_templates(_)
        return
        
    if history:
        console.print(f"[yellow]{_('cli.history_coming')}[/yellow]")
        return
        
    if interactive:
        _interactive_mode(_, analyze_stack, suggest)
        return
    
    # Get error content
    error_content = _get_error_content(error, file, _)
    if not error_content:
        console.print(f"[red]{_('cli.no_error')}[/red]")
        console.print(_('cli.help_hint'))
        sys.exit(1)
    
    # Process error with enhanced analysis
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        # Basic error detection
        task = progress.add_task(_('cli.analyzing'), total=None)
        detector = ErrorDetector()
        detected_type = error_type or detector.detect(error_content)
        error_info = detector.extract_key_info(error_content, detected_type)
        severity = detector.get_severity(error_content, detected_type)
        
        # Enhanced analysis
        stack_analysis = None
        pattern_matches = []
        code_context_info = None
        suggestions = []
        
        if analyze_stack:
            progress.update(task, description="Analyzing stack trace...")
            stack_analyzer = StackTraceAnalyzer()
            stack_analysis = stack_analyzer.analyze(error_content)
            
        progress.update(task, description="Detecting error patterns...")
        pattern_analyzer = PatternAnalyzer()
        pattern_matches = pattern_analyzer.analyze(error_content)
        
        if context:
            progress.update(task, description="Analyzing code context...")
            context_analyzer = CodeContextAnalyzer()
            # Extract line number from error if possible
            line_nums = error_info.get('line_numbers', [])
            if line_nums:
                code_context_info = context_analyzer.analyze_file_context(
                    context, line_nums[0]
                )
        
        if suggest or pattern_matches:
            progress.update(task, description="Generating suggestions...")
            suggestion_engine = SuggestionEngine()
            error_patterns = [p.name for p in pattern_matches]
            suggestions = suggestion_engine.generate_suggestions(
                detected_type,
                error_patterns,
                stack_analyzer.get_summary(stack_analysis) if stack_analysis else None,
                context_analyzer.get_minimal_context(code_context_info) if code_context_info else None
            )
        
        # Generate prompt
        progress.update(task, description=_('cli.generating'))
        generator = PromptGenerator()
        prompt = generator.generate(
            error_content, detected_type, error_info, custom_agent=agent
        )
        
        progress.stop()
    
    # Display results with enhanced information
    _display_enhanced_results(
        prompt, detected_type, severity, error_info, verbose, _,
        stack_analysis, pattern_matches, code_context_info, suggestions
    )
    
    # Handle output options
    if copy:
        if copy_to_clipboard(prompt):
            console.print(f"\n[bold green]{_('cli.copied')}[/bold green]")
        else:
            console.print(f"\n[bold red]{_('cli.copy_failed')}[/bold red]")
            
    if output:
        try:
            Path(output).write_text(prompt, encoding="utf-8")
            console.print(f"\n[bold green]{_('cli.saved', file=output)}[/bold green]")
        except Exception as e:
            console.print(f"\n[bold red]{_('cli.save_failed', error=e)}[/bold red]")


def _get_error_content(error: Optional[str], file: Optional[str], _) -> str:
    """Get error content from various sources."""
    if file:
        try:
            return Path(file).read_text(encoding="utf-8")
        except Exception as e:
            console.print(f"[red]{_('cli.reading_file_error', error=e)}[/red]")
            sys.exit(1)
    elif error:
        return error
    else:
        # Try to get from clipboard
        content = paste_from_clipboard()
        if content:
            console.print(f"[dim]{_('cli.using_clipboard')}[/dim]")
            return content
        return ""


def _display_enhanced_results(
    prompt: str, error_type: str, severity: str, error_info: Dict, verbose: bool, _,
    stack_analysis, pattern_matches, code_context_info, suggestions
):
    """Display enhanced analysis results."""
    # Severity colors
    severity_colors = {
        "critical": "bold red",
        "high": "red",
        "medium": "yellow",
        "low": "green",
    }
    
    severity_color = severity_colors.get(severity, "white")
    
    # Create title
    title = _('error.title', type=error_type.title(), severity=severity.upper())
    
    # Display prompt in panel
    console.print(
        Panel(
            prompt,
            title=f"[{severity_color}]{title}[/{severity_color}]",
            border_style=severity_color.split()[-1],
            padding=(1, 2),
        )
    )
    
    # Show stack trace analysis
    if stack_analysis:
        console.print(f"\n[bold]{_('error.stack_trace')}:[/bold]")
        stack_analyzer = StackTraceAnalyzer()
        summary = stack_analyzer.get_summary(stack_analysis)
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row("Language:", summary['language'].title())
        table.add_row("Error Type:", summary['error_type'])
        table.add_row("Total Frames:", str(summary['total_frames']))
        table.add_row("User Code Frames:", str(summary['user_frames']))
        
        if summary.get('root_cause'):
            rc = summary['root_cause']
            table.add_row(
                "Root Cause:", 
                f"{rc['file']}:{rc['line']} in {rc['function']}"
            )
        
        console.print(table)
    
    # Show pattern matches
    if pattern_matches:
        console.print(f"\n[bold]Error Patterns Detected:[/bold]")
        for pattern in pattern_matches[:3]:  # Show top 3
            console.print(f"  • {pattern.description} [dim]({pattern.severity})[/dim]")
    
    # Show code context
    if code_context_info:
        console.print(f"\n[bold]Code Context:[/bold]")
        context_analyzer = CodeContextAnalyzer()
        context_str = context_analyzer.format_context(code_context_info)
        syntax = Syntax(context_str, "python", theme="monokai", line_numbers=True)
        console.print(syntax)
    
    # Show suggestions
    if suggestions:
        console.print(f"\n[bold]🎯 Intelligent Suggestions:[/bold]")
        suggestion_engine = SuggestionEngine()
        for i, suggestion in enumerate(suggestions[:3], 1):
            formatted = suggestion_engine.format_suggestion(suggestion)
            console.print(f"\n{i}. {formatted}")
    
    # Show additional info in verbose mode
    if verbose:
        console.print(f"\n[bold]{_('analysis.details')}[/bold]")
        console.print(_('analysis.error_type', type=error_type))
        console.print(_('analysis.severity', severity=severity))
        
        if error_info.get("files"):
            console.print(_('analysis.files', files=', '.join(error_info['files'])))
            
        if error_info.get("error_codes"):
            console.print(_('analysis.error_codes', codes=', '.join(error_info['error_codes'])))
            
        if error_info.get("line_numbers"):
            console.print(_('analysis.lines', lines=', '.join(map(str, error_info['line_numbers']))))


def _interactive_mode(_, analyze_stack: bool, suggest: bool):
    """Run in interactive mode with enhanced features."""
    console.print(f"[bold cyan]{_('cli.interactive_title')}[/bold cyan]")
    console.print(f"{_('cli.interactive_prompt')}\n")
    
    try:
        lines = []
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    error_content = "\n".join(lines)
    
    if not error_content.strip():
        console.print(f"\n[red]{_('cli.no_content')}[/red]")
        return
    
    # Process the error
    console.print("\n" + "─" * 50 + "\n")
    
    detector = ErrorDetector()
    error_type = detector.detect(error_content)
    error_info = detector.extract_key_info(error_content, error_type)
    severity = detector.get_severity(error_content, error_type)
    
    # Enhanced analysis in interactive mode
    stack_analysis = None
    pattern_matches = []
    suggestions = []
    
    if analyze_stack:
        stack_analyzer = StackTraceAnalyzer()
        stack_analysis = stack_analyzer.analyze(error_content)
    
    pattern_analyzer = PatternAnalyzer()
    pattern_matches = pattern_analyzer.analyze(error_content)
    
    if suggest or pattern_matches:
        suggestion_engine = SuggestionEngine()
        error_patterns = [p.name for p in pattern_matches]
        suggestions = suggestion_engine.generate_suggestions(
            error_type, error_patterns
        )
    
    generator = PromptGenerator()
    prompt = generator.generate(error_content, error_type, error_info)
    
    _display_enhanced_results(
        prompt, error_type, severity, error_info, True, _,
        stack_analysis, pattern_matches, None, suggestions
    )
    
    # Ask if user wants to copy
    if click.confirm(f"\n{_('cli.copy_prompt')}", default=True):
        if copy_to_clipboard(prompt):
            console.print(f"[bold green]{_('cli.copied')}[/bold green]")


def _list_templates(_):
    """List available templates."""
    generator = PromptGenerator()
    templates = generator.list_templates()
    
    console.print(f"[bold cyan]{_('cli.available_templates')}[/bold cyan]\n")
    
    for template in sorted(templates):
        if template.startswith("user_"):
            console.print(f"  • {template[5:]} [dim](user)[/dim]")
        else:
            console.print(f"  • {template}")
            
    console.print(f"\n{_('cli.template_count', count=len(templates))}")


if __name__ == "__main__":
    cli()