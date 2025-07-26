#!/usr/bin/env python3
"""
Enhanced CLI Demo for ClaudeCode-Debugger

This script demonstrates the advanced features of the enhanced CLI.
"""

import subprocess
import time
from pathlib import Path


def run_command(cmd: str, description: str):
    """Run a CLI command and display the description."""
    print(f"\n{'='*60}")
    print(f"🎯 {description}")
    print(f"{'='*60}")
    print(f"$ {cmd}\n")
    
    # Add a small delay for dramatic effect
    time.sleep(1)
    
    # Run the command
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
        
    time.sleep(2)  # Pause between commands


def main():
    """Run the demo."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     ClaudeCode-Debugger Enhanced CLI Demo                 ║
    ╚═══════════════════════════════════════════════════════════╝
    
    This demo showcases the advanced features of the enhanced CLI.
    """)
    
    # Create sample error files
    error_dir = Path("sample_errors")
    error_dir.mkdir(exist_ok=True)
    
    # TypeScript error
    ts_error = error_dir / "typescript_error.log"
    ts_error.write_text("""
src/components/Button.tsx:15:5 - error TS2322: Type 'string' is not assignable to type 'number'.

15     size = "large";
       ~~~~

src/components/Button.tsx:20:3 - error TS2554: Expected 2 arguments, but got 1.

20   onClick(event);
     ~~~~~~~~~~~~~~

Found 2 errors in the same file, starting at: src/components/Button.tsx:15
""")

    # Python error with stack trace
    py_error = error_dir / "python_error.log"
    py_error.write_text("""
Traceback (most recent call last):
  File "/Users/dev/project/app.py", line 42, in process_data
    result = calculate_metrics(data)
  File "/Users/dev/project/metrics.py", line 15, in calculate_metrics
    average = sum(values) / len(values)
  File "/Users/dev/project/metrics.py", line 8, in sum
    return total + item
TypeError: unsupported operand type(s) for +: 'int' and 'str'
""")

    # Multiple errors for batch processing
    js_error1 = error_dir / "js_error_1.log"
    js_error1.write_text("""
ReferenceError: fetchData is not defined
    at processRequest (api.js:25:10)
    at Object.<anonymous> (server.js:15:5)
    at Module._compile (internal/modules/cjs/loader.js:1063:30)
""")

    js_error2 = error_dir / "js_error_2.log"
    js_error2.write_text("""
TypeError: Cannot read property 'map' of undefined
    at renderList (components/List.js:10:15)
    at render (components/App.js:25:12)
""")

    # Demo commands
    commands = [
        # Basic usage with type detection
        (
            'ccdebug-enhanced "TypeError: Cannot read property \'name\' of undefined"',
            "Basic error analysis with auto-detection"
        ),
        
        # File input with specified type
        (
            f'ccdebug-enhanced -f {ts_error} -t typescript -v',
            "Analyze TypeScript error from file with verbose output"
        ),
        
        # Copy to clipboard with format
        (
            f'ccdebug-enhanced -f {py_error} -c markdown',
            "Analyze Python error and copy as Markdown"
        ),
        
        # Batch processing with wildcard
        (
            f'ccdebug-enhanced -f "{error_dir}/*.log" --batch -o batch_report.json --format json',
            "Batch process multiple error files and save as JSON"
        ),
        
        # List available templates
        (
            'ccdebug-enhanced --list-templates',
            "List all available prompt templates"
        ),
        
        # Show configuration
        (
            'ccdebug-enhanced config show',
            "Display current configuration settings"
        ),
        
        # Plugin management
        (
            'ccdebug-enhanced plugin list',
            "List available plugins and their status"
        ),
        
        # History display
        (
            'ccdebug-enhanced history show --limit 5',
            "Show recent command history"
        ),
        
        # Statistics
        (
            'ccdebug-enhanced --stats',
            "Display usage statistics and insights"
        ),
    ]
    
    # Run each command
    for cmd, description in commands:
        try:
            run_command(cmd, description)
        except Exception as e:
            print(f"Error running command: {e}")
            
    # Interactive mode demo
    print(f"\n{'='*60}")
    print("🎯 Interactive Mode Demo")
    print(f"{'='*60}")
    print("\nTo try interactive mode, run:")
    print("$ ccdebug-enhanced --interactive")
    print("\nFeatures:")
    print("  • Multi-line error input")
    print("  • Real-time analysis")
    print("  • Copy/save options")
    print("  • Re-analysis with different settings")
    
    # Watch mode demo
    print(f"\n{'='*60}")
    print("🎯 Watch Mode Demo")
    print(f"{'='*60}")
    print("\nTo monitor log files continuously, run:")
    print(f'$ ccdebug-enhanced --watch -f "{error_dir}/*.log"')
    print("\nThe tool will automatically analyze new errors as they appear.")
    
    # Cleanup
    print(f"\n{'='*60}")
    print("✅ Demo Complete!")
    print(f"{'='*60}")
    print("\nSample error files created in:", error_dir)
    print("\nTo install the enhanced CLI:")
    print("$ pip install -e .")
    print("\nThen use 'ccdebug-enhanced' command to access all features!")


if __name__ == "__main__":
    main()