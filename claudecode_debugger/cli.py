"""CLI interface for ClaudeCode-Debugger."""

import sys
from pathlib import Path
from typing import Dict, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core.detector import ErrorDetector
from .core.generator import PromptGenerator
from .utils.clipboard import copy_to_clipboard, paste_from_clipboard

# from rich.syntax import Syntax  # Unused import


console = Console()


@click.command()
@click.argument("error", required=False)
@click.option("-f", "--file", type=click.Path(exists=True), help="Read error from file")
@click.option(
    "-t", "--type", "error_type", help="Error type (auto-detect if not specified)"
)
@click.option("-c", "--copy", is_flag=True, help="Copy to clipboard")
@click.option("-o", "--output", type=click.Path(), help="Save to file")
@click.option("-i", "--interactive", is_flag=True, help="Interactive mode")
@click.option("--history", is_flag=True, help="Show history")
@click.option("--list-templates", is_flag=True, help="List available templates")
@click.option("--agent", help="Override default agent selection")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
def main(
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
):
    """
    ClaudeCode-Debugger: Smart debug prompt generator for Claude Code.

    Transform error messages into actionable debug prompts with AI-powered analysis.

    Examples:

        ccdebug "TypeError: Cannot read property"

        ccdebug -f error.log -c

        ccdebug --interactive
    """

    # Handle special commands
    if list_templates:
        _list_templates()
        return

    if history:
        console.print("[yellow]History feature coming soon![/yellow]")
        return

    if interactive:
        _interactive_mode()
        return

    # Get error content
    error_content = _get_error_content(error, file)
    if not error_content:
        console.print("[red]Error: No error content provided.[/red]")
        console.print("Use --help for usage information.")
        sys.exit(1)

    # Process error
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        # Detect error type
        task = progress.add_task("Analyzing error...", total=None)
        detector = ErrorDetector()
        detected_type = error_type or detector.detect(error_content)
        error_info = detector.extract_key_info(error_content, detected_type)
        severity = detector.get_severity(error_content, detected_type)

        # Generate prompt
        progress.update(task, description="Generating debug prompt...")
        generator = PromptGenerator()
        prompt = generator.generate(
            error_content, detected_type, error_info, custom_agent=agent
        )

        progress.stop()

    # Display results
    _display_results(prompt, detected_type, severity, error_info, verbose)

    # Handle output options
    if copy:
        if copy_to_clipboard(prompt):
            console.print("\n[bold green]✓[/bold green] Copied to clipboard!")
        else:
            console.print("\n[bold red]✗[/bold red] Failed to copy to clipboard.")

    if output:
        try:
            Path(output).write_text(prompt, encoding="utf-8")
            console.print(f"\n[bold green]✓[/bold green] Saved to {output}")
        except Exception as e:
            console.print(f"\n[bold red]✗[/bold red] Failed to save: {e}")


def _get_error_content(error: Optional[str], file: Optional[str]) -> str:
    """Get error content from various sources."""
    if file:
        try:
            return Path(file).read_text(encoding="utf-8")
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            sys.exit(1)
    elif error:
        return error
    else:
        # Try to get from clipboard
        content = paste_from_clipboard()
        if content:
            console.print("[dim]Using content from clipboard...[/dim]")
            return content
        return ""


def _display_results(
    prompt: str, error_type: str, severity: str, error_info: Dict, verbose: bool
):
    """Display analysis results."""
    # Severity colors
    severity_colors = {
        "critical": "bold red",
        "high": "red",
        "medium": "yellow",
        "low": "green",
    }

    severity_color = severity_colors.get(severity, "white")

    # Create title
    title = f"[{severity_color}]🚨 {error_type.title()} Error - {severity.upper()} Priority[/{severity_color}]"

    # Display prompt in panel
    console.print(
        Panel(
            prompt,
            title=title,
            border_style=severity_color.split()[-1],
            padding=(1, 2),
        )
    )

    # Show additional info in verbose mode
    if verbose:
        console.print("\n[bold]Analysis Details:[/bold]")
        console.print(f"  Error Type: {error_type}")
        console.print(f"  Severity: {severity}")

        if error_info.get("files"):
            console.print(f"  Files: {', '.join(error_info['files'])}")

        if error_info.get("error_codes"):
            console.print(f"  Error Codes: {', '.join(error_info['error_codes'])}")

        if error_info.get("line_numbers"):
            console.print(f"  Lines: {', '.join(map(str, error_info['line_numbers']))}")


def _interactive_mode():
    """Run in interactive mode."""
    console.print("[bold cyan]ClaudeCode-Debugger Interactive Mode[/bold cyan]")
    console.print("Enter your error message (Ctrl+D to finish):\n")

    try:
        lines = []
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    error_content = "\n".join(lines)

    if not error_content.strip():
        console.print("\n[red]No error content provided.[/red]")
        return

    # Process the error
    console.print("\n" + "─" * 50 + "\n")

    detector = ErrorDetector()
    error_type = detector.detect(error_content)
    error_info = detector.extract_key_info(error_content, error_type)
    severity = detector.get_severity(error_content, error_type)

    generator = PromptGenerator()
    prompt = generator.generate(error_content, error_type, error_info)

    _display_results(prompt, error_type, severity, error_info, verbose=True)

    # Ask if user wants to copy
    if click.confirm("\nCopy to clipboard?", default=True):
        if copy_to_clipboard(prompt):
            console.print("[bold green]✓[/bold green] Copied to clipboard!")


def _list_templates():
    """List available templates."""
    generator = PromptGenerator()
    templates = generator.list_templates()

    console.print("[bold cyan]Available Templates:[/bold cyan]\n")

    for template in sorted(templates):
        if template.startswith("user_"):
            console.print(f"  • {template[5:]} [dim](user)[/dim]")
        else:
            console.print(f"  • {template}")

    console.print(f"\nTotal: {len(templates)} templates")


if __name__ == "__main__":
    main()
