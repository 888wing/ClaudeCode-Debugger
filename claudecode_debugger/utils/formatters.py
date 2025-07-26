"""Output formatters for ClaudeCode-Debugger."""

import json
import yaml
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime
import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter, TerminalFormatter


class OutputFormatter:
    """Formats output for different targets and formats."""
    
    def __init__(self):
        """Initialize formatter."""
        self.html_formatter = HtmlFormatter(style='monokai')
        self.terminal_formatter = TerminalFormatter()
        
    def format(self, data: Dict[str, Any], format: str) -> str:
        """Format data for output."""
        if format == 'text':
            return self._format_text(data)
        elif format == 'json':
            return self._format_json(data)
        elif format == 'markdown':
            return self._format_markdown(data)
        elif format == 'html':
            return self._format_html(data)
        elif format == 'yaml':
            return self._format_yaml(data)
        else:
            raise ValueError(f"Unknown format: {format}")
            
    def format_batch(self, results: List[Dict[str, Any]], format: str) -> str:
        """Format batch results."""
        if format == 'json':
            return json.dumps(results, indent=2)
        elif format == 'yaml':
            return yaml.dump(results, default_flow_style=False)
        elif format == 'markdown':
            return self._format_batch_markdown(results)
        elif format == 'html':
            return self._format_batch_html(results)
        else:
            return self._format_batch_text(results)
            
    def format_for_clipboard(self, content: str, format: str) -> str:
        """Format content specifically for clipboard."""
        if format == 'plain':
            return content
        elif format == 'markdown':
            return self._format_clipboard_markdown(content)
        elif format == 'code':
            return self._format_clipboard_code(content)
        elif format == 'json':
            return self._format_clipboard_json(content)
        else:
            return content
            
    def _format_text(self, data: Dict[str, Any]) -> str:
        """Format as plain text."""
        lines = []
        lines.append(f"Error Type: {data['error_type']}")
        lines.append(f"Severity: {data['severity']}")
        lines.append("")
        lines.append("Debug Prompt:")
        lines.append("-" * 50)
        lines.append(data['prompt'])
        
        if data.get('error_info'):
            lines.append("")
            lines.append("Extracted Information:")
            lines.append("-" * 50)
            
            info = data['error_info']
            if info.get('files'):
                lines.append(f"Files: {', '.join(info['files'])}")
            if info.get('error_codes'):
                lines.append(f"Error Codes: {', '.join(info['error_codes'])}")
            if info.get('line_numbers'):
                lines.append(f"Lines: {', '.join(map(str, info['line_numbers']))}")
                
        return '\n'.join(lines)
        
    def _format_json(self, data: Dict[str, Any]) -> str:
        """Format as JSON."""
        # Clean up data for JSON serialization
        clean_data = {
            'error_type': data['error_type'],
            'severity': data['severity'],
            'prompt': data['prompt'],
            'error_info': data.get('error_info', {}),
            'timestamp': datetime.now().isoformat(),
        }
        
        if data.get('plugin_results'):
            clean_data['plugin_results'] = data['plugin_results']
            
        return json.dumps(clean_data, indent=2)
        
    def _format_markdown(self, data: Dict[str, Any]) -> str:
        """Format as Markdown."""
        lines = []
        
        # Header
        severity_emoji = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '⚡',
            'low': 'ℹ️'
        }.get(data['severity'], '❓')
        
        lines.append(f"# {severity_emoji} {data['error_type'].title()} Error Analysis")
        lines.append("")
        lines.append(f"**Severity:** {data['severity'].upper()}")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Debug prompt
        lines.append("## Debug Prompt")
        lines.append("")
        lines.append(data['prompt'])
        lines.append("")
        
        # Error info
        if data.get('error_info'):
            lines.append("## Extracted Information")
            lines.append("")
            
            info = data['error_info']
            if info.get('files'):
                lines.append("### Files")
                for file in info['files']:
                    lines.append(f"- `{file}`")
                lines.append("")
                
            if info.get('error_codes'):
                lines.append("### Error Codes")
                for code in info['error_codes']:
                    lines.append(f"- `{code}`")
                lines.append("")
                
            if info.get('line_numbers'):
                lines.append("### Line Numbers")
                lines.append(f"- {', '.join(map(str, info['line_numbers']))}")
                lines.append("")
                
        # Plugin results
        if data.get('plugin_results'):
            lines.append("## Plugin Analysis")
            lines.append("")
            
            for plugin, results in data['plugin_results'].items():
                lines.append(f"### {plugin}")
                if isinstance(results, dict):
                    for key, value in results.items():
                        lines.append(f"- **{key}:** {value}")
                else:
                    lines.append(str(results))
                lines.append("")
                
        return '\n'.join(lines)
        
    def _format_html(self, data: Dict[str, Any]) -> str:
        """Format as HTML."""
        # Convert markdown to HTML
        md_content = self._format_markdown(data)
        html_content = markdown.markdown(
            md_content,
            extensions=['fenced_code', 'tables', 'toc']
        )
        
        # Add CSS styling
        css = self.html_formatter.get_style_defs('.highlight')
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ClaudeCode-Debugger Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        pre {{
            background-color: #282c34;
            color: #abb2bf;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        .severity-critical {{ color: #e74c3c; }}
        .severity-high {{ color: #f39c12; }}
        .severity-medium {{ color: #3498db; }}
        .severity-low {{ color: #27ae60; }}
        {css}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""
        return html
        
    def _format_yaml(self, data: Dict[str, Any]) -> str:
        """Format as YAML."""
        clean_data = {
            'error_type': data['error_type'],
            'severity': data['severity'],
            'prompt': data['prompt'],
            'error_info': data.get('error_info', {}),
            'timestamp': datetime.now().isoformat(),
        }
        
        if data.get('plugin_results'):
            clean_data['plugin_results'] = data['plugin_results']
            
        return yaml.dump(clean_data, default_flow_style=False, sort_keys=False)
        
    def _format_batch_text(self, results: List[Dict[str, Any]]) -> str:
        """Format batch results as text."""
        lines = []
        lines.append("ClaudeCode-Debugger Batch Report")
        lines.append("=" * 50)
        lines.append(f"Total Errors: {len(results)}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Summary
        severity_counts = {}
        type_counts = {}
        
        for result in results:
            severity = result['severity']
            error_type = result['error_type']
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            type_counts[error_type] = type_counts.get(error_type, 0) + 1
            
        lines.append("Summary:")
        lines.append("-" * 20)
        
        lines.append("By Severity:")
        for severity in ['critical', 'high', 'medium', 'low']:
            if severity in severity_counts:
                lines.append(f"  {severity.title()}: {severity_counts[severity]}")
                
        lines.append("")
        lines.append("By Type:")
        for error_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {error_type}: {count}")
            
        lines.append("")
        lines.append("=" * 50)
        lines.append("")
        
        # Individual results
        for i, result in enumerate(results, 1):
            lines.append(f"Error #{i}")
            lines.append("-" * 30)
            if 'source_file' in result:
                lines.append(f"Source: {result['source_file']}")
            lines.append(self._format_text(result))
            lines.append("")
            lines.append("")
            
        return '\n'.join(lines)
        
    def _format_batch_markdown(self, results: List[Dict[str, Any]]) -> str:
        """Format batch results as Markdown."""
        lines = []
        lines.append("# ClaudeCode-Debugger Batch Report")
        lines.append("")
        lines.append(f"**Total Errors:** {len(results)}")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Summary table
        lines.append("## Summary")
        lines.append("")
        lines.append("### By Severity")
        lines.append("")
        lines.append("| Severity | Count |")
        lines.append("|----------|-------|")
        
        severity_counts = {}
        for result in results:
            severity = result['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
        for severity in ['critical', 'high', 'medium', 'low']:
            if severity in severity_counts:
                lines.append(f"| {severity.title()} | {severity_counts[severity]} |")
                
        lines.append("")
        
        # Individual results
        lines.append("## Detailed Results")
        lines.append("")
        
        for i, result in enumerate(results, 1):
            if 'source_file' in result:
                lines.append(f"### Error #{i} - {Path(result['source_file']).name}")
            else:
                lines.append(f"### Error #{i}")
            lines.append("")
            
            # Add content without the header
            md_content = self._format_markdown(result)
            # Skip the first header line
            content_lines = md_content.split('\n')[4:]
            lines.extend(content_lines)
            lines.append("")
            lines.append("---")
            lines.append("")
            
        return '\n'.join(lines)
        
    def _format_batch_html(self, results: List[Dict[str, Any]]) -> str:
        """Format batch results as HTML."""
        md_content = self._format_batch_markdown(results)
        return self._format_html({'prompt': md_content, 'error_type': 'batch', 'severity': 'info'})
        
    def _format_clipboard_markdown(self, content: str) -> str:
        """Format for clipboard as Markdown."""
        lines = []
        lines.append("```")
        lines.append(content)
        lines.append("```")
        lines.append("")
        lines.append("*Generated by ClaudeCode-Debugger*")
        return '\n'.join(lines)
        
    def _format_clipboard_code(self, content: str) -> str:
        """Format for clipboard as code block."""
        # Try to detect language for syntax
        try:
            lexer = guess_lexer(content)
            lang = lexer.aliases[0] if lexer.aliases else ''
        except:
            lang = ''
            
        if lang:
            return f"```{lang}\n{content}\n```"
        else:
            return f"```\n{content}\n```"
            
    def _format_clipboard_json(self, content: str) -> str:
        """Format for clipboard as JSON."""
        data = {
            'prompt': content,
            'timestamp': datetime.now().isoformat(),
            'source': 'ClaudeCode-Debugger'
        }
        return json.dumps(data, indent=2)
        
    def highlight_code(self, code: str, language: str = None) -> str:
        """Highlight code with syntax coloring."""
        try:
            if language:
                lexer = get_lexer_by_name(language)
            else:
                lexer = guess_lexer(code)
                
            return highlight(code, lexer, self.terminal_formatter)
        except:
            return code