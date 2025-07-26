#!/usr/bin/env python3
"""
Demonstration of the advanced template system in ClaudeCode-Debugger.
"""

import sys
sys.path.insert(0, '..')

from claudecode_debugger.core.template_system import AdvancedTemplateSystem
from claudecode_debugger.core.generator import PromptGenerator
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

console = Console()


def demo_basic_template():
    """Demo basic template rendering."""
    console.print("\n[bold cyan]1. Basic Template Rendering[/bold cyan]")
    
    generator = PromptGenerator(use_advanced=True)
    
    # TypeScript error
    error_text = """
src/components/UserProfile.tsx:42:15 - error TS2322: Type 'string' is not assignable to type 'number'.

42   const age: number = "25";
                ~~~~~~

Found 1 error in src/components/UserProfile.tsx:42
"""
    
    prompt = generator.generate(
        error_text=error_text,
        error_type='typescript',
        error_info={
            'files': ['src/components/UserProfile.tsx'],
            'line_numbers': [42],
            'error_codes': ['TS2322'],
            'error_messages': ["Type 'string' is not assignable to type 'number'"],
        }
    )
    
    syntax = Syntax(prompt, "markdown", theme="monokai")
    console.print(Panel(syntax, title="TypeScript Error Debug Prompt"))


def demo_advanced_features():
    """Demo advanced template features."""
    console.print("\n[bold cyan]2. Advanced Template Features[/bold cyan]")
    
    template_system = AdvancedTemplateSystem()
    
    # Memory error with detailed info
    context = {
        'error_text': """
FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory
 1: 0x1012e4da5 node::Abort() (.cold.1) [node]
 2: 0x1000a6239 node::Abort() [node]
 3: 0x1000a63bf node::OnFatalError(char const*, char const*) [node]
 4: 0x1001e9007 v8::Utils::ReportOOMFailure(v8::internal::Isolate*, char const*, bool) [node]
""",
        'error_type': 'memory',
        'error_type_display': 'Memory Error',
        'severity': 'critical',
        'memory_usage': 95,
        'memory_stats': {
            'heap_used': 1980,
            'heap_total': 2048,
            'rss': 2400,
            'external': 150,
        },
        'recommended_agent': 'backend-system-architect',
    }
    
    if 'memory_advanced' in template_system.templates:
        prompt = template_system.render('memory_advanced', context)
        syntax = Syntax(prompt, "markdown", theme="monokai")
        console.print(Panel(syntax, title="Memory Error with Advanced Template"))
    else:
        console.print("[yellow]Memory advanced template not found[/yellow]")


def demo_docker_kubernetes():
    """Demo Docker/Kubernetes template."""
    console.print("\n[bold cyan]3. Docker/Kubernetes Error Template[/bold cyan]")
    
    generator = PromptGenerator(use_advanced=True)
    
    # Kubernetes error
    error_text = """
Events:
  Type     Reason             Age                From               Message
  ----     ------             ----               ----               -------
  Normal   Scheduled          5m                 default-scheduler  Successfully assigned default/app-deployment-7b9f6d6f5-xkz4p to node-1
  Normal   Pulling            5m                 kubelet            Pulling image "myapp:latest"
  Warning  Failed             3m (x3 over 5m)    kubelet            Failed to pull image "myapp:latest": rpc error: code = Unknown desc = Error response from daemon: pull access denied for myapp, repository does not exist or may require 'docker login'
  Warning  Failed             3m (x3 over 5m)    kubelet            Error: ErrImagePull
  Normal   BackOff            2m (x7 over 5m)    kubelet            Back-off pulling image "myapp:latest"
  Warning  Failed             2m (x7 over 5m)    kubelet            Error: ImagePullBackOff
"""
    
    prompt = generator.generate(
        error_text=error_text,
        error_type='kubernetes',
        error_info={
            'pod_name': 'app-deployment-7b9f6d6f5-xkz4p',
            'namespace': 'default',
            'pod_status': 'ImagePullBackOff',
            'container_name': 'app',
            'image_name': 'myapp:latest',
        }
    )
    
    syntax = Syntax(prompt, "markdown", theme="monokai")
    console.print(Panel(syntax, title="Kubernetes ImagePullBackOff Error"))


def demo_api_network():
    """Demo API/Network error template."""
    console.print("\n[bold cyan]4. API/Network Error Template[/bold cyan]")
    
    template_system = AdvancedTemplateSystem()
    
    # API error context
    context = {
        'error_text': """
Error: Request failed with status code 429
    at createError (axios/lib/core/createError.js:16:15)
    at settle (axios/lib/core/settle.js:17:12)
    at IncomingMessage.handleStreamEnd (axios/lib/adapters/http.js:260:11)
    
Response Headers:
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1642789200
  Retry-After: 3600
""",
        'error_type': 'network',
        'error_type_display': 'API Rate Limit Error',
        'http_status': '429',
        'request_info': {
            'method': 'GET',
            'url': 'https://api.example.com/v1/users',
            'host': 'api.example.com',
        },
        'response_info': {
            'status': 429,
            'time': 250,
        },
        'recommended_agent': 'backend-system-architect',
    }
    
    if 'api_network' in template_system.templates:
        prompt = template_system.render('api_network', context)
        syntax = Syntax(prompt, "markdown", theme="monokai")
        console.print(Panel(syntax, title="API Rate Limit Error"))
    else:
        console.print("[yellow]API/Network template not found[/yellow]")


def demo_template_management():
    """Demo template management features."""
    console.print("\n[bold cyan]5. Template Management Features[/bold cyan]")
    
    template_system = AdvancedTemplateSystem()
    
    # List templates
    console.print("\n[bold]Available Templates:[/bold]")
    templates = template_system.list_templates()
    
    for template in templates[:10]:  # Show first 10
        console.print(f"  • {template['name']} [dim]({template['category']})[/dim] - {template['description']}")
    
    if len(templates) > 10:
        console.print(f"  [dim]... and {len(templates) - 10} more[/dim]")
    
    # Validate a template
    console.print("\n[bold]Template Validation:[/bold]")
    valid, errors = template_system.validate_template('typescript_advanced')
    
    if valid:
        console.print("  ✅ typescript_advanced template is valid")
    else:
        console.print("  ❌ typescript_advanced template has errors:")
        for error in errors:
            console.print(f"    - {error}")


def main():
    """Run all demos."""
    console.print("[bold magenta]ClaudeCode-Debugger Advanced Template System Demo[/bold magenta]")
    console.print("=" * 60)
    
    try:
        demo_basic_template()
        demo_advanced_features()
        demo_docker_kubernetes()
        demo_api_network()
        demo_template_management()
        
        console.print("\n[bold green]✅ All demos completed successfully![/bold green]")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Demo failed: {e}[/bold red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()