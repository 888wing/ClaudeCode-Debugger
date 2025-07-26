"""Template management and editing tool for ClaudeCode-Debugger."""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import click
import yaml
from jinja2 import Template, TemplateSyntaxError
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table

from .template_system import AdvancedTemplateSystem

console = Console()


class TemplateManager:
    """Manage and edit debug templates."""

    def __init__(self, template_system: Optional[AdvancedTemplateSystem] = None):
        """Initialize template manager."""
        self.template_system = template_system or AdvancedTemplateSystem()
        self.user_template_dir = Path.home() / ".ccdebug" / "templates"
        self.backup_dir = Path.home() / ".ccdebug" / "backups"

        # Ensure directories exist
        self.user_template_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def list_templates(
        self, category: Optional[str] = None, show_details: bool = False
    ) -> None:
        """List all available templates."""
        templates = self.template_system.list_templates(category)

        if not templates:
            console.print("[yellow]No templates found.[/yellow]")
            return

        table = Table(title="Available Templates", show_header=True)
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Display Name", style="green")
        table.add_column("Category", style="magenta")
        table.add_column("Version", style="blue")

        if show_details:
            table.add_column("Agent", style="yellow")
            table.add_column("Tags", style="dim")

        for template in templates:
            row = [
                template["name"],
                template["display_name"],
                template["category"],
                template["version"],
            ]

            if show_details:
                row.extend(
                    [
                        template["agent"],
                        ", ".join(template["tags"]),
                    ]
                )

            table.add_row(*row)

        console.print(table)

    def show_template(self, template_name: str, raw: bool = False) -> None:
        """Display template content."""
        if template_name not in self.template_system.templates:
            console.print(f"[red]Template '{template_name}' not found.[/red]")
            return

        template_data = self.template_system.templates[template_name]

        if raw:
            # Show raw YAML
            yaml_content = yaml.dump(template_data, allow_unicode=True, sort_keys=False)
            syntax = Syntax(yaml_content, "yaml", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"Template: {template_name}"))
        else:
            # Show rendered preview
            sample_context = self._get_sample_context()

            try:
                rendered = self.template_system.render(template_name, sample_context)
                syntax = Syntax(rendered, "markdown", theme="monokai")
                console.print(Panel(syntax, title=f"Template Preview: {template_name}"))
            except Exception as e:
                console.print(f"[red]Error rendering template: {e}[/red]")

    def create_template(self, name: str, base_template: Optional[str] = None) -> None:
        """Create a new template."""
        if name in self.template_system.templates:
            if not Confirm.ask(f"Template '{name}' already exists. Overwrite?"):
                return

        template_data = {
            "name": name.replace("_", " ").title(),
            "version": "1.0.0",
            "description": Prompt.ask("Description"),
            "category": Prompt.ask("Category", default="custom"),
            "agent": Prompt.ask("Agent", default="general-purpose"),
            "tags": Prompt.ask("Tags (comma-separated)", default="").split(","),
        }

        if base_template and base_template in self.template_system.templates:
            template_data["extends"] = base_template
            console.print(f"[green]Extending from '{base_template}'[/green]")

        # Get template content
        console.print("\n[cyan]Enter template content (Jinja2 format).[/cyan]")
        console.print("[dim]Type 'END' on a new line when finished.[/dim]\n")

        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)

        template_data["template"] = "\n".join(lines)

        # Validate template
        valid, errors = self._validate_template_data(template_data)

        if not valid:
            console.print("[red]Template validation failed:[/red]")
            for error in errors:
                console.print(f"  - {error}")
            if not Confirm.ask("Save anyway?"):
                return

        # Save template
        output_path = self.user_template_dir / f"{name}.yaml"

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(template_data, f, allow_unicode=True, sort_keys=False)

        console.print(f"[green]Template saved to: {output_path}[/green]")

        # Reload templates
        self.template_system.reload_template(output_path)

    def edit_template(self, template_name: str) -> None:
        """Edit an existing template."""
        if template_name not in self.template_system.templates:
            console.print(f"[red]Template '{template_name}' not found.[/red]")
            return

        # Get template file path
        template_path = self._find_template_file(template_name)

        if not template_path:
            console.print(
                f"[red]Cannot find template file for '{template_name}'.[/red]"
            )
            return

        # Check if it's a built-in template
        if ".ccdebug" not in str(template_path):
            # Copy to user directory for editing
            user_path = self.user_template_dir / f"{template_name}.yaml"
            shutil.copy2(template_path, user_path)
            template_path = user_path
            console.print(
                f"[yellow]Copied built-in template to user directory for editing.[/yellow]"
            )

        # Create backup
        self._backup_template(template_path)

        # Open in editor
        editor = os.environ.get("EDITOR", "nano")
        os.system(f"{editor} {template_path}")

        # Reload template
        self.template_system.reload_template(template_path)

        # Validate
        valid, errors = self.template_system.validate_template(template_name)

        if not valid:
            console.print("[red]Template validation failed:[/red]")
            for error in errors:
                console.print(f"  - {error}")

    def delete_template(self, template_name: str) -> None:
        """Delete a template."""
        template_path = self._find_template_file(template_name)

        if not template_path:
            console.print(
                f"[red]Cannot find template file for '{template_name}'.[/red]"
            )
            return

        # Check if it's a built-in template
        if ".ccdebug" not in str(template_path):
            console.print("[red]Cannot delete built-in templates.[/red]")
            return

        if Confirm.ask(f"Delete template '{template_name}'?"):
            # Create backup
            self._backup_template(template_path)

            # Delete file
            os.remove(template_path)

            # Remove from system
            self.template_system.templates.pop(template_name, None)

            console.print(f"[green]Template '{template_name}' deleted.[/green]")

    def test_template(
        self, template_name: str, sample_file: Optional[Path] = None
    ) -> None:
        """Test a template with sample data."""
        if template_name not in self.template_system.templates:
            console.print(f"[red]Template '{template_name}' not found.[/red]")
            return

        # Load or generate sample context
        if sample_file and sample_file.exists():
            with open(sample_file, "r") as f:
                context = json.load(f)
        else:
            context = self._get_sample_context()

        # Render template
        try:
            rendered = self.template_system.render(template_name, context)

            # Display result
            syntax = Syntax(rendered, "markdown", theme="monokai")
            console.print(Panel(syntax, title=f"Template Test: {template_name}"))

            # Show statistics
            console.print("\n[cyan]Template Statistics:[/cyan]")
            console.print(f"  - Output length: {len(rendered)} characters")
            console.print(f"  - Line count: {rendered.count(chr(10)) + 1}")

            # Validate output
            if len(rendered) < 100:
                console.print("  [yellow]⚠️  Output seems too short[/yellow]")
            if "{{" in rendered or "{%" in rendered:
                console.print("  [red]⚠️  Unrendered template syntax detected[/red]")

        except Exception as e:
            console.print(f"[red]Error rendering template: {e}[/red]")

    def export_template(self, template_name: str, output_path: Path) -> None:
        """Export a template."""
        try:
            self.template_system.export_template(template_name, output_path)
            console.print(f"[green]Template exported to: {output_path}[/green]")
        except Exception as e:
            console.print(f"[red]Export failed: {e}[/red]")

    def import_template(self, input_path: Path, name: Optional[str] = None) -> None:
        """Import a template."""
        if not input_path.exists():
            console.print(f"[red]File not found: {input_path}[/red]")
            return

        try:
            self.template_system.import_template(input_path, name)
            console.print(f"[green]Template imported successfully.[/green]")
        except Exception as e:
            console.print(f"[red]Import failed: {e}[/red]")

    def share_template(self, template_name: str) -> None:
        """Share a template (export with metadata)."""
        if template_name not in self.template_system.templates:
            console.print(f"[red]Template '{template_name}' not found.[/red]")
            return

        # Create share package
        share_dir = Path.home() / ".ccdebug" / "shared"
        share_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_name = f"{template_name}_{timestamp}"
        package_dir = share_dir / package_name
        package_dir.mkdir()

        # Export template
        template_file = package_dir / f"{template_name}.yaml"
        self.template_system.export_template(template_name, template_file)

        # Add metadata
        metadata = {
            "template_name": template_name,
            "exported_at": datetime.now().isoformat(),
            "version": self.template_system.templates[template_name].get(
                "version", "1.0.0"
            ),
            "description": self.template_system.templates[template_name].get(
                "description", ""
            ),
        }

        with open(package_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        # Create archive
        archive_path = share_dir / f"{package_name}.tar.gz"
        shutil.make_archive(str(archive_path.with_suffix("")), "gztar", package_dir)

        # Cleanup
        shutil.rmtree(package_dir)

        console.print(f"[green]Template package created: {archive_path}[/green]")
        console.print(f"\n[cyan]Share this file to distribute your template.[/cyan]")

    def _find_template_file(self, template_name: str) -> Optional[Path]:
        """Find the file path for a template."""
        # Check all template directories
        for template_dir in self.template_system.template_dirs:
            template_file = template_dir / f"{template_name}.yaml"
            if template_file.exists():
                return template_file

        # Check with .yaml extension variations
        for template_dir in self.template_system.template_dirs:
            for ext in [".yaml", ".yml"]:
                template_file = template_dir / f"{template_name}{ext}"
                if template_file.exists():
                    return template_file

        return None

    def _backup_template(self, template_path: Path) -> None:
        """Create a backup of a template."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{template_path.stem}_{timestamp}.yaml"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(template_path, backup_path)
        console.print(f"[dim]Backup created: {backup_path}[/dim]")

    def _validate_template_data(self, template_data: Dict) -> Tuple[bool, List[str]]:
        """Validate template data structure."""
        errors = []

        # Check required fields
        required = ["name", "template"]
        for field in required:
            if field not in template_data:
                errors.append(f"Missing required field: {field}")

        # Validate template syntax
        if "template" in template_data:
            try:
                Template(template_data["template"])
            except TemplateSyntaxError as e:
                errors.append(f"Template syntax error: {e}")

        return len(errors) == 0, errors

    def _get_sample_context(self) -> Dict[str, Any]:
        """Generate sample context for testing."""
        return {
            "error_text": 'TypeError: Cannot read property "name" of undefined\n'
            "    at processUser (app.js:42:15)\n"
            "    at main (app.js:10:5)",
            "error_type": "javascript",
            "error_type_display": "JavaScript Runtime Error",
            "error_count": 3,
            "files": ["src/app.js", "src/utils.js", "src/models/user.js"],
            "line_numbers": [42, 15, 127],
            "error_codes": ["TypeError", "ReferenceError"],
            "error_messages": [
                'Cannot read property "name" of undefined',
                "user is not defined",
            ],
            "stack_trace": "Full stack trace here...",
            "severity": "error",
            "recommended_agent": "debug-specialist",
            "pod_name": "app-deployment-abc123",
            "namespace": "production",
            "memory_stats": {
                "heap_used": 1024,
                "heap_total": 2048,
                "rss": 1536,
            },
        }


@click.group()
def template_cli():
    """Template management CLI."""
    pass


@template_cli.command()
@click.option("--category", "-c", help="Filter by category")
@click.option("--details", "-d", is_flag=True, help="Show detailed information")
def list(category, details):
    """List all available templates."""
    manager = TemplateManager()
    manager.list_templates(category, details)


@template_cli.command()
@click.argument("template_name")
@click.option("--raw", "-r", is_flag=True, help="Show raw YAML")
def show(template_name, raw):
    """Show template content."""
    manager = TemplateManager()
    manager.show_template(template_name, raw)


@template_cli.command()
@click.argument("name")
@click.option("--base", "-b", help="Base template to extend")
def create(name, base):
    """Create a new template."""
    manager = TemplateManager()
    manager.create_template(name, base)


@template_cli.command()
@click.argument("template_name")
def edit(template_name):
    """Edit an existing template."""
    manager = TemplateManager()
    manager.edit_template(template_name)


@template_cli.command()
@click.argument("template_name")
def delete(template_name):
    """Delete a template."""
    manager = TemplateManager()
    manager.delete_template(template_name)


@template_cli.command()
@click.argument("template_name")
@click.option(
    "--sample", "-s", type=click.Path(exists=True), help="Sample data file (JSON)"
)
def test(template_name, sample):
    """Test a template."""
    manager = TemplateManager()
    manager.test_template(template_name, Path(sample) if sample else None)


@template_cli.command()
@click.argument("template_name")
@click.argument("output_path", type=click.Path())
def export(template_name, output_path):
    """Export a template."""
    manager = TemplateManager()
    manager.export_template(template_name, Path(output_path))


@template_cli.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--name", "-n", help="Template name")
def import_cmd(input_path, name):
    """Import a template."""
    manager = TemplateManager()
    manager.import_template(Path(input_path), name)


@template_cli.command()
@click.argument("template_name")
def share(template_name):
    """Share a template."""
    manager = TemplateManager()
    manager.share_template(template_name)


if __name__ == "__main__":
    template_cli()
