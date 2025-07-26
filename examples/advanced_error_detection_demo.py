"""Demo script for the advanced error detection system."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from claudecode_debugger.core.advanced_detector import (
    AdvancedErrorDetector, ErrorPattern, ErrorCategory
)
from claudecode_debugger.core.ml_classifier import ErrorMLClassifier
from claudecode_debugger.core.training_data_generator import TrainingDataGenerator


def demo_basic_detection():
    """Demonstrate basic error detection."""
    print("=== Basic Error Detection Demo ===\n")
    
    detector = AdvancedErrorDetector()
    
    # Example 1: TypeScript Error
    typescript_error = """
    src/components/UserProfile.tsx:23:5 - error TS2322: Type 'string' is not assignable to type 'number'.
    
    23     const userId: number = getUserId(); // getUserId() returns string
           ~~~~~~
    
    Found 1 error in src/components/UserProfile.tsx:23
    """
    
    print("TypeScript Error Example:")
    print("-" * 50)
    matches = detector.detect_multi_label(typescript_error)
    
    for match in matches:
        print(f"Category: {match.category.value}")
        print(f"Confidence: {match.confidence:.2%}")
        print(f"Severity: {match.severity}")
        if match.extracted_info:
            print(f"Extracted Info: {match.extracted_info}")
    print()
    
    # Example 2: Python Traceback
    python_error = """
    Traceback (most recent call last):
      File "/app/main.py", line 42, in process_request
        user_data = json.loads(request_body)
      File "/usr/lib/python3.9/json/__init__.py", line 346, in loads
        return _default_decoder.decode(s)
    json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
    """
    
    print("\nPython Error Example:")
    print("-" * 50)
    matches = detector.detect_multi_label(python_error)
    info = detector.extract_comprehensive_info(python_error)
    
    print(f"Detected Categories: {[m.category.value for m in matches]}")
    print(f"Files: {info['files']}")
    print(f"Functions: {info['functions']}")
    print(f"Line Numbers: {info['line_numbers']}")
    print()


def demo_multi_label_detection():
    """Demonstrate multi-label error detection."""
    print("\n=== Multi-Label Detection Demo ===\n")
    
    detector = AdvancedErrorDetector()
    
    # Complex error with multiple issues
    complex_error = """
    [2023-10-20 15:45:23] ERROR: API request failed
    
    Error: connect ECONNREFUSED 127.0.0.1:3000
        at TCPConnectWrap.afterConnect [as oncomplete] (net.js:1146:16)
        at processTicksAndRejections (internal/process/task_queues.js:80:21)
    
    TypeError: Cannot read property 'data' of undefined
        at handleResponse (/app/src/handlers/api.js:25:30)
        at process._tickCallback (internal/process/next_tick.js:68:7)
    
    FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory
    
    Docker container exited with code 137
    """
    
    matches = detector.detect_multi_label(complex_error, confidence_threshold=0.1)
    
    print("Detected Error Categories:")
    print("-" * 50)
    for match in matches:
        print(f"{match.category.value}: {match.confidence:.2%} confidence, {match.severity} severity")
    
    # Extract comprehensive information
    info = detector.extract_comprehensive_info(complex_error)
    
    print("\nExtracted Information:")
    print("-" * 50)
    print(f"Timestamps: {info['timestamps']}")
    print(f"URLs: {info['urls']}")
    print(f"Error Codes: {info['error_codes']}")
    print(f"Suggestions: {info['suggestions']}")


def demo_custom_patterns():
    """Demonstrate custom pattern addition."""
    print("\n=== Custom Pattern Demo ===\n")
    
    detector = AdvancedErrorDetector()
    
    # Add custom patterns for a specific application
    custom_patterns = [
        ErrorPattern(
            r'PAYMENT_ERROR:\s*(\w+)\s*-\s*(.+)',
            ErrorCategory.GENERAL,
            weight=2.5,
            extract_groups=['error_code', 'message']
        ),
        ErrorPattern(
            r'Authentication failed for user\s*["\'](\w+)["\']',
            ErrorCategory.SECURITY,
            weight=2.0,
            extract_groups=['username']
        )
    ]
    
    for pattern in custom_patterns:
        detector.add_custom_pattern(pattern)
    
    # Test with custom error
    custom_error = """
    [2023-10-20 16:00:00] PAYMENT_ERROR: CARD_DECLINED - Insufficient funds
    Authentication failed for user 'john_doe'
    Please check payment details and try again.
    """
    
    matches = detector.detect_multi_label(custom_error)
    
    print("Custom Pattern Detection Results:")
    print("-" * 50)
    for match in matches:
        print(f"Category: {match.category.value}")
        print(f"Confidence: {match.confidence:.2%}")
        if match.extracted_info:
            print(f"Extracted: {match.extracted_info}")
    print()


def demo_ml_training():
    """Demonstrate ML classifier training."""
    print("\n=== ML Classifier Training Demo ===\n")
    
    # Generate training data
    generator = TrainingDataGenerator()
    print("Generating training data...")
    training_data = generator.generate_examples(count=500)
    training_data.extend(generator.generate_real_world_examples())
    
    print(f"Generated {len(training_data)} training examples")
    
    # Train classifier
    classifier = ErrorMLClassifier()
    print("\nTraining ML classifier...")
    classifier.train(training_data, validation_split=0.2)
    
    # Test predictions
    test_errors = [
        "TS2304: Cannot find name 'React'. Did you forget to import it?",
        "MemoryError: Unable to allocate 2.5 GiB for an array",
        "docker: Error response from daemon: pull access denied",
        "CORS policy: No 'Access-Control-Allow-Origin' header is present"
    ]
    
    print("\nML Predictions:")
    print("-" * 50)
    for error in test_errors:
        categories, severity, confidence = classifier.predict(error)
        print(f"Error: {error[:60]}...")
        print(f"  Categories: {[f'{cat}: {conf:.2%}' for cat, conf in categories[:3]]}")
        print(f"  Severity: {severity} (confidence: {confidence:.2%})")
        print()


def demo_streaming_detection():
    """Demonstrate streaming detection for large files."""
    print("\n=== Streaming Detection Demo ===\n")
    
    # Create a sample log file
    from tempfile import NamedTemporaryFile
    
    with NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        log_file = Path(f.name)
        
        # Write a large log with various errors
        for i in range(1000):
            f.write(f"[2023-10-20 12:00:{i%60:02d}] INFO: Processing request {i}\n")
            
            if i % 50 == 0:
                f.write("ERROR TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.\n")
            
            if i % 100 == 0:
                f.write("FATAL ERROR: JavaScript heap out of memory\n")
            
            if i % 75 == 0:
                f.write("Error: ECONNREFUSED connect failed\n")
    
    # Stream detection
    detector = AdvancedErrorDetector()
    print(f"Analyzing log file: {log_file}")
    print("-" * 50)
    
    matches = detector.stream_detect(log_file, chunk_size=4096)
    
    # Summarize findings
    category_counts = {}
    severity_counts = {}
    
    for match in matches:
        cat = match.category.value
        sev = match.severity
        category_counts[cat] = category_counts.get(cat, 0) + 1
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
    
    print("Error Summary:")
    print(f"Total unique error types detected: {len(matches)}")
    print("\nBy Category:")
    for cat, count in sorted(category_counts.items()):
        print(f"  {cat}: {count}")
    print("\nBy Severity:")
    for sev, count in sorted(severity_counts.items()):
        print(f"  {sev}: {count}")
    
    # Clean up
    log_file.unlink()


def demo_comprehensive_analysis():
    """Demonstrate comprehensive error analysis."""
    print("\n=== Comprehensive Analysis Demo ===\n")
    
    # Real-world error scenario
    error_log = """
    2023-10-20 18:30:45.123 [ERROR] Application startup failed
    
    1. Database Connection Error:
    psycopg2.OperationalError: could not connect to server: Connection refused
        Is the server running on host "db.example.com" (192.168.1.100) and accepting
        TCP/IP connections on port 5432?
    
    2. Configuration Error:
    Traceback (most recent call last):
      File "/app/config/loader.py", line 45, in load_config
        with open(config_path, 'r') as f:
    FileNotFoundError: [Errno 2] No such file or directory: '/etc/app/config.yaml'
    
    3. React Application Build Error:
    ERROR in ./src/components/Dashboard.tsx
    Module build failed: Error: TypeScript emitted no output for Dashboard.tsx
    TS2307: Cannot find module '@mui/material/Button' or its corresponding type declarations.
    
    4. Memory Warning:
    Warning: Node.js process is using 1.8GB of 2GB available memory
    Consider increasing --max-old-space-size
    
    Environment: Node v16.14.0, Python 3.9.7, PostgreSQL 13.5
    Running in Docker container (image: app:latest)
    OS: Ubuntu 20.04 LTS
    """
    
    detector = AdvancedErrorDetector()
    
    # Create and train a classifier for this demo
    generator = TrainingDataGenerator()
    classifier = ErrorMLClassifier()
    training_data = generator.generate_examples(count=200)
    classifier.train(training_data, validation_split=0.1)
    
    # Enhance detector with ML
    detector.ml_classifier = classifier
    
    # Perform analysis
    matches = detector.detect_multi_label(error_log)
    info = detector.extract_comprehensive_info(error_log)
    
    print("Comprehensive Error Analysis Report")
    print("=" * 60)
    
    print("\n1. Error Categories Detected:")
    for i, match in enumerate(matches, 1):
        print(f"   {i}. {match.category.value}")
        print(f"      - Confidence: {match.confidence:.2%}")
        print(f"      - Severity: {match.severity}")
    
    print("\n2. Affected Files:")
    for file in info['files']:
        lines = [str(ln) for ln in info['line_numbers'] if ln < 1000]  # Reasonable line numbers
        print(f"   - {file} {f'(lines: {', '.join(lines[:3])})' if lines else ''}")
    
    print("\n3. Environment Information:")
    for key, value in info['environment'].items():
        print(f"   - {key}: {value}")
    
    print("\n4. Recommended Actions:")
    for i, suggestion in enumerate(info['suggestions'], 1):
        print(f"   {i}. {suggestion}")
    
    print("\n5. Stack Traces Found:")
    print(f"   - Total: {len(info['stack_traces'])}")
    for trace in info['stack_traces']:
        print(f"   - Type: {trace['type']}, Frames: {len(trace['frames'])}")
    
    # ML predictions
    print("\n6. ML-Enhanced Analysis:")
    ml_categories, ml_severity, ml_confidence = classifier.predict(error_log)
    print(f"   - Primary categories: {', '.join([cat for cat, _ in ml_categories[:3]])}")
    print(f"   - Overall severity: {ml_severity}")
    print(f"   - Analysis confidence: {ml_confidence:.2%}")


def main():
    """Run all demos."""
    demos = [
        ("Basic Error Detection", demo_basic_detection),
        ("Multi-Label Detection", demo_multi_label_detection),
        ("Custom Patterns", demo_custom_patterns),
        ("ML Classifier Training", demo_ml_training),
        ("Streaming Detection", demo_streaming_detection),
        ("Comprehensive Analysis", demo_comprehensive_analysis)
    ]
    
    print("ClaudeCode-Debugger Advanced Error Detection Demo")
    print("=" * 60)
    print()
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\nError in {name}: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60 + "\n")
    
    print("Demo completed!")


if __name__ == "__main__":
    main()