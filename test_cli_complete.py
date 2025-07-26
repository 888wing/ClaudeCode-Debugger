#!/usr/bin/env python3
"""Complete CLI test for all command options."""

import subprocess
import tempfile
from pathlib import Path

# Test errors
TEST_ERRORS = {
    'python': '''Traceback (most recent call last):
  File "app.py", line 42, in process_data
    result = data.get_value()
AttributeError: 'NoneType' object has no attribute 'get_value'
''',
    
    'javascript': '''TypeError: Cannot read property 'name' of undefined
    at UserProfile (UserProfile.js:15:23)
    at renderWithHooks (react-dom.development.js:14985:18)
''',
    
    'typescript': '''error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
  src/calculator.ts:25:15
''',
}

def run_command(cmd, input_data=None):
    """Run command and return result."""
    result = subprocess.run(
        cmd,
        input=input_data,
        capture_output=True,
        text=True,
        shell=False
    )
    return result

def test_basic_commands():
    """Test basic command functionality."""
    print("=" * 60)
    print("Testing Basic Commands")
    print("=" * 60)
    
    tests = [
        # Help
        ("Help", ["python3", "-m", "claudecode_debugger.cli_new", "--help"]),
        
        # List templates
        ("List Templates", ["python3", "-m", "claudecode_debugger.cli_new", "--list-templates"]),
        
        # Basic error - English
        ("Basic Error (EN)", ["python3", "-m", "claudecode_debugger.cli_new", TEST_ERRORS['python'], "--lang", "en"]),
        
        # Basic error - Chinese
        ("Basic Error (ZH)", ["python3", "-m", "claudecode_debugger.cli_new", TEST_ERRORS['python'], "--lang", "zh"]),
    ]
    
    for name, cmd in tests:
        print(f"\n[{name}]")
        result = run_command(cmd)
        print(f"Exit code: {result.returncode}")
        if result.returncode != 0:
            print(f"Error: {result.stderr[:200]}")
        else:
            print("✅ Success")

def test_analysis_features():
    """Test advanced analysis features."""
    print("\n" + "=" * 60)
    print("Testing Analysis Features")
    print("=" * 60)
    
    tests = [
        # Stack trace analysis
        ("Stack Analysis", ["python3", "-m", "claudecode_debugger.cli_new", 
                          TEST_ERRORS['javascript'], "--analyze-stack"]),
        
        # Suggestions
        ("Suggestions", ["python3", "-m", "claudecode_debugger.cli_new", 
                        TEST_ERRORS['python'], "--suggest"]),
        
        # Verbose mode
        ("Verbose Mode", ["python3", "-m", "claudecode_debugger.cli_new", 
                         TEST_ERRORS['typescript'], "--verbose"]),
        
        # Combined features
        ("Combined Features", ["python3", "-m", "claudecode_debugger.cli_new", 
                              TEST_ERRORS['python'], "--lang", "zh", 
                              "--analyze-stack", "--suggest", "--verbose"]),
    ]
    
    for name, cmd in tests:
        print(f"\n[{name}]")
        result = run_command(cmd)
        print(f"Exit code: {result.returncode}")
        if result.returncode != 0:
            print(f"Error: {result.stderr[:200]}")
        else:
            print("✅ Success")

def test_file_operations():
    """Test file input/output operations."""
    print("\n" + "=" * 60)
    print("Testing File Operations")
    print("=" * 60)
    
    # Create temp files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        f.write(TEST_ERRORS['python'])
        error_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        output_file = f.name
    
    tests = [
        # Read from file
        ("Read from File", ["python3", "-m", "claudecode_debugger.cli_new", 
                           "-f", error_file]),
        
        # Output to file
        ("Output to File", ["python3", "-m", "claudecode_debugger.cli_new", 
                           TEST_ERRORS['javascript'], "-o", output_file]),
        
        # Read and output
        ("Read & Output", ["python3", "-m", "claudecode_debugger.cli_new", 
                          "-f", error_file, "-o", output_file, "--lang", "zh"]),
    ]
    
    for name, cmd in tests:
        print(f"\n[{name}]")
        result = run_command(cmd)
        print(f"Exit code: {result.returncode}")
        if result.returncode != 0:
            print(f"Error: {result.stderr[:200]}")
        else:
            print("✅ Success")
            
    # Check output file
    if Path(output_file).exists():
        content = Path(output_file).read_text()
        print(f"\nOutput file created: {len(content)} bytes")
    
    # Cleanup
    Path(error_file).unlink()
    Path(output_file).unlink()

def test_interactive_mode():
    """Test interactive mode."""
    print("\n" + "=" * 60)
    print("Testing Interactive Mode")
    print("=" * 60)
    
    # Test interactive mode with input
    cmd = ["python3", "-m", "claudecode_debugger.cli_new", "-i"]
    
    print("[Interactive Mode - Basic]")
    result = run_command(cmd, input_data=TEST_ERRORS['python'])
    print(f"Exit code: {result.returncode}")
    if result.returncode != 0:
        print(f"Error: {result.stderr[:200]}")
    else:
        print("✅ Success")
    
    # Test with analysis options
    cmd = ["python3", "-m", "claudecode_debugger.cli_new", "-i", "--suggest", "--lang", "zh"]
    
    print("\n[Interactive Mode - With Options]")
    result = run_command(cmd, input_data=TEST_ERRORS['javascript'])
    print(f"Exit code: {result.returncode}")
    if result.returncode != 0:
        print(f"Error: {result.stderr[:200]}")
    else:
        print("✅ Success")

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "=" * 60)
    print("Testing Edge Cases")
    print("=" * 60)
    
    tests = [
        # Empty input
        ("Empty Input", ["python3", "-m", "claudecode_debugger.cli_new", ""]),
        
        # Invalid language
        ("Invalid File", ["python3", "-m", "claudecode_debugger.cli_new", 
                         "-f", "nonexistent.log"]),
        
        # Multiple errors
        ("Multiple Errors", ["python3", "-m", "claudecode_debugger.cli_new", 
                            TEST_ERRORS['python'] + "\n" + TEST_ERRORS['javascript']]),
    ]
    
    for name, cmd in tests:
        print(f"\n[{name}]")
        result = run_command(cmd)
        print(f"Exit code: {result.returncode}")
        # These might fail, which is expected
        if result.returncode == 0:
            print("✅ Handled gracefully")
        else:
            print("❌ Expected failure")

def main():
    """Run all CLI tests."""
    print("ClaudeCode-Debugger Complete CLI Test")
    print("=" * 60)
    
    test_basic_commands()
    test_analysis_features()
    test_file_operations()
    test_interactive_mode()
    test_edge_cases()
    
    print("\n" + "=" * 60)
    print("All CLI tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()