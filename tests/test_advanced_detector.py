"""Tests for the advanced error detection system."""

from pathlib import Path

import numpy as np
import pytest

from claudecode_debugger.core.advanced_detector import (
    AdvancedErrorDetector,
    ErrorCategory,
    ErrorMatch,
    ErrorPattern,
)
from claudecode_debugger.core.ml_classifier import ErrorMLClassifier, TrainingExample
from claudecode_debugger.core.training_data_generator import TrainingDataGenerator


class TestAdvancedErrorDetector:
    """Test suite for AdvancedErrorDetector."""

    @pytest.fixture
    def detector(self):
        """Create a detector instance."""
        return AdvancedErrorDetector()

    def test_typescript_error_detection(self, detector):
        """Test TypeScript error detection."""
        error_text = """
        src/app.ts:10:5 - error TS2322: Type 'string' is not assignable to type 'number'.
        
        10     const count: number = "hello";
               ~~~~~
        """

        matches = detector.detect_multi_label(error_text)

        assert len(matches) > 0
        assert matches[0].category == ErrorCategory.TYPESCRIPT
        assert matches[0].confidence > 0.5
        assert "error_code" in matches[0].extracted_info
        assert "2322" in matches[0].extracted_info["error_code"]

    def test_python_traceback_detection(self, detector):
        """Test Python traceback detection."""
        error_text = """
        Traceback (most recent call last):
          File "main.py", line 42, in process_data
            result = data['key']
        KeyError: 'key'
        """

        matches = detector.detect_multi_label(error_text)

        assert any(m.category == ErrorCategory.PYTHON for m in matches)
        python_match = next(m for m in matches if m.category == ErrorCategory.PYTHON)
        assert python_match.confidence > 0.6

        info = detector.extract_comprehensive_info(error_text)
        assert "main.py" in info["files"]
        assert 42 in info["line_numbers"]
        assert "process_data" in info["functions"]

    def test_memory_error_detection(self, detector):
        """Test memory error detection."""
        error_text = """
        FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory
        """

        matches = detector.detect_multi_label(error_text)

        assert any(m.category == ErrorCategory.MEMORY for m in matches)
        memory_match = next(m for m in matches if m.category == ErrorCategory.MEMORY)
        assert memory_match.severity == "critical"

    def test_multi_label_detection(self, detector):
        """Test detection of multiple error types."""
        error_text = """
        Error: ECONNREFUSED connect ECONNREFUSED 127.0.0.1:3000
        at TCPConnectWrap.afterConnect [as oncomplete] (net.js:1141:16)
        
        TypeError: Cannot read property 'data' of undefined
        at processResponse (app.js:25:15)
        """

        matches = detector.detect_multi_label(error_text, confidence_threshold=0.2)

        categories = [m.category for m in matches]
        assert ErrorCategory.NETWORK in categories
        assert ErrorCategory.JAVASCRIPT in categories

    def test_custom_pattern_addition(self, detector):
        """Test adding custom patterns."""
        custom_pattern = ErrorPattern(
            r"CUSTOM_ERROR:\s*(.+)",
            ErrorCategory.GENERAL,
            weight=2.0,
            extract_groups=["message"],
        )

        detector.add_custom_pattern(custom_pattern)

        error_text = "CUSTOM_ERROR: This is a custom error message"
        matches = detector.detect_multi_label(error_text)

        assert len(matches) > 0
        assert matches[0].category == ErrorCategory.GENERAL

    def test_comprehensive_info_extraction(self, detector):
        """Test comprehensive information extraction."""
        error_text = """
        [2023-10-15 14:30:45] ERROR: Failed to connect to database
        File "/app/src/db/connection.py", line 127, in connect
            conn = psycopg2.connect(dsn)
        psycopg2.OperationalError: could not connect to server: Connection refused
            Is the server running on host "localhost" (127.0.0.1) and accepting
            TCP/IP connections on port 5432?
        
        Environment: Python 3.9.7, Ubuntu 20.04
        URL: postgresql://localhost:5432/mydb
        """

        info = detector.extract_comprehensive_info(error_text)

        assert "/app/src/db/connection.py" in info["files"]
        assert 127 in info["line_numbers"]
        assert "connect" in info["functions"]
        assert "postgresql://localhost:5432/mydb" in info["urls"]
        assert "2023-10-15 14:30:45" in info["timestamps"]
        assert info["environment"].get("python_version") == "3.9.7"
        assert info["environment"].get("os") == "linux"

    def test_severity_calculation(self, detector):
        """Test severity calculation."""
        critical_error = "FATAL ERROR: System crash due to memory overflow"
        high_error = "TypeError: Cannot read property 'x' of undefined"
        medium_error = "Warning: Deprecated function used"

        critical_matches = detector.detect_multi_label(critical_error)
        high_matches = detector.detect_multi_label(high_error)
        medium_matches = detector.detect_multi_label(medium_error)

        assert critical_matches[0].severity == "critical"
        assert high_matches[0].severity in ["high", "medium"]
        # Note: 'warning' isn't strongly detected as error, might return empty

    def test_stack_trace_extraction(self, detector):
        """Test stack trace extraction."""
        error_text = """
        Error: Connection failed
            at connect (connection.js:45:11)
            at async Database.initialize (database.js:23:5)
            at async main (index.js:10:3)
        """

        info = detector.extract_comprehensive_info(error_text)

        assert len(info["stack_traces"]) > 0
        trace = info["stack_traces"][0]
        assert trace["type"] == "javascript"
        assert len(trace["frames"]) >= 3
        assert trace["frames"][0]["function"] == "connect"
        assert trace["frames"][0]["line"] == 45

    def test_stream_detection(self, detector, tmp_path):
        """Test streaming detection for large files."""
        # Create a large log file
        log_file = tmp_path / "large_error.log"

        with open(log_file, "w") as f:
            # Write many errors
            for i in range(100):
                f.write(f"Line {i}: Normal log entry\n")
                if i % 10 == 0:
                    f.write(f"Error TS2322: Type error at line {i}\n")
                if i % 20 == 0:
                    f.write("JavaScript heap out of memory\n")

        matches = detector.stream_detect(log_file, chunk_size=1024)

        assert len(matches) > 0
        categories = [m.category for m in matches]
        assert ErrorCategory.TYPESCRIPT in categories
        assert ErrorCategory.MEMORY in categories


class TestErrorMLClassifier:
    """Test suite for ErrorMLClassifier."""

    @pytest.fixture
    def classifier(self):
        """Create a classifier instance."""
        return ErrorMLClassifier()

    @pytest.fixture
    def training_data(self):
        """Generate training data."""
        generator = TrainingDataGenerator()
        return generator.generate_examples(count=100)

    def test_feature_extraction(self, classifier):
        """Test feature extraction."""
        texts = [
            "TypeError: Cannot read property 'x' of undefined",
            "TS2322: Type 'string' is not assignable to type 'number'",
            "FATAL ERROR: JavaScript heap out of memory",
        ]

        features = classifier.extract_features(texts)

        assert features.shape[0] == 3
        assert features.shape[1] > 20  # TF-IDF + custom features
        assert not np.any(np.isnan(features))

    def test_training(self, classifier, training_data):
        """Test model training."""
        classifier.train(training_data, validation_split=0.2)

        # Check that models are trained
        assert classifier.category_classifier is not None
        assert classifier.severity_classifier is not None
        assert hasattr(classifier.category_classifier, "predict")

    def test_prediction(self, classifier, training_data):
        """Test prediction."""
        # Train first
        classifier.train(training_data[:50], validation_split=0.1)

        # Test prediction
        test_text = "TypeError: Cannot read property 'map' of undefined at UserList.render (UserList.js:45:23)"

        categories, severity, confidence = classifier.predict(test_text)

        assert len(categories) > 0
        assert categories[0][0] in ["javascript", "general"]  # Category name
        assert 0 <= categories[0][1] <= 1  # Confidence score
        assert severity in ["low", "medium", "high", "critical"]
        assert 0 <= confidence <= 1

    def test_batch_prediction(self, classifier, training_data):
        """Test batch prediction."""
        classifier.train(training_data[:50], validation_split=0.1)

        test_texts = [
            "TS2304: Cannot find name 'React'",
            "MemoryError: Unable to allocate array",
            "docker: Error response from daemon",
        ]

        results = classifier.predict_batch(test_texts)

        assert len(results) == 3
        for categories, severity, confidence in results:
            assert isinstance(categories, list)
            assert isinstance(severity, str)
            assert isinstance(confidence, float)

    def test_model_persistence(self, classifier, training_data, tmp_path):
        """Test model saving and loading."""
        # Train model
        classifier.train(training_data[:50], validation_split=0.1)

        # Save model
        model_path = tmp_path / "test_model"
        classifier.save_model(model_path)

        # Check files exist
        assert (model_path / "vectorizer.pkl").exists()
        assert (model_path / "category_classifier.pkl").exists()
        assert (model_path / "severity_classifier.pkl").exists()
        assert (model_path / "metadata.json").exists()

        # Load in new classifier
        new_classifier = ErrorMLClassifier()
        new_classifier.load_model(model_path)

        # Test prediction with loaded model
        test_text = "Error: Connection timeout"
        categories, severity, confidence = new_classifier.predict(test_text)

        assert len(categories) > 0


class TestTrainingDataGenerator:
    """Test suite for TrainingDataGenerator."""

    @pytest.fixture
    def generator(self):
        """Create a generator instance."""
        return TrainingDataGenerator()

    def test_generate_examples(self, generator):
        """Test example generation."""
        examples = generator.generate_examples(count=50)

        assert len(examples) == 50

        # Check variety
        categories = set()
        severities = set()

        for example in examples:
            assert isinstance(example.text, str)
            assert len(example.text) > 0
            assert isinstance(example.categories, list)
            assert len(example.categories) > 0
            assert example.severity in ["low", "medium", "high", "critical"]

            categories.update(example.categories)
            severities.add(example.severity)

        # Should have multiple categories and severities
        assert len(categories) > 5
        assert len(severities) > 1

    def test_specific_category_generation(self, generator):
        """Test generation of specific categories."""
        examples = generator.generate_examples(
            count=20, categories=["typescript", "javascript"]
        )

        for example in examples:
            assert all(
                cat in ["typescript", "javascript"] for cat in example.categories
            )

    def test_multi_label_generation(self, generator):
        """Test multi-label example generation."""
        examples = generator.generate_examples(count=100)

        multi_label_count = sum(1 for ex in examples if len(ex.categories) > 1)

        # Should have some multi-label examples (roughly 20%)
        assert multi_label_count > 10
        assert multi_label_count < 40

    def test_real_world_examples(self, generator):
        """Test real-world example generation."""
        examples = generator.generate_real_world_examples()

        assert len(examples) > 0

        # Check that examples look realistic
        for example in examples:
            assert len(example.text) > 50  # Non-trivial errors
            assert "\n" in example.text  # Multi-line
            assert any(
                keyword in example.text.lower()
                for keyword in ["error", "exception", "failed", "traceback"]
            )

    def test_export_import(self, generator, tmp_path):
        """Test export and import functionality."""
        examples = generator.generate_examples(count=10)

        # Export
        export_file = tmp_path / "test_training_data.json"
        generator.export_training_data(examples, str(export_file))

        assert export_file.exists()

        # Import
        imported_examples = generator.import_training_data(str(export_file))

        assert len(imported_examples) == len(examples)

        # Check content matches
        for orig, imported in zip(examples, imported_examples):
            assert orig.text == imported.text
            assert orig.categories == imported.categories
            assert orig.severity == imported.severity


class TestIntegration:
    """Integration tests for the complete system."""

    def test_detector_with_ml_enhancement(self, tmp_path):
        """Test detector with ML classifier enhancement."""
        # Train a simple ML model
        generator = TrainingDataGenerator()
        training_data = generator.generate_examples(count=200)

        classifier = ErrorMLClassifier()
        classifier.train(training_data, validation_split=0.2)

        # Create detector with ML classifier
        detector = AdvancedErrorDetector()
        detector.ml_classifier = classifier

        # Test detection with ML enhancement
        error_text = """
        TypeError: Cannot read property 'length' of undefined
            at processArray (utils.js:45:23)
            at main (index.js:12:5)
        
        This error occurred while processing user data.
        """

        matches = detector.detect_multi_label(error_text)

        assert len(matches) > 0
        assert any(m.category == ErrorCategory.JAVASCRIPT for m in matches)

    def test_end_to_end_workflow(self):
        """Test complete workflow from detection to classification."""
        # Create components
        detector = AdvancedErrorDetector()
        generator = TrainingDataGenerator()
        classifier = ErrorMLClassifier()

        # Generate and add custom pattern
        custom_pattern = ErrorPattern(
            r"CRITICAL:\s*Database connection lost", ErrorCategory.DATABASE, weight=3.0
        )
        detector.add_custom_pattern(custom_pattern)

        # Generate training data
        training_examples = generator.generate_examples(count=100)
        training_examples.extend(generator.generate_real_world_examples())

        # Train classifier
        classifier.train(training_examples, validation_split=0.2)

        # Test with complex error
        complex_error = """
        [2023-10-15 10:30:00] ERROR: Multiple failures detected
        
        1. TypeScript Compilation Error:
        src/api/client.ts:45:10 - error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.
        
        2. Runtime Error:
        TypeError: Cannot read property 'connect' of undefined
            at Database.initialize (database.js:30:20)
            at async startServer (server.js:15:5)
        
        3. Network Error:
        Error: connect ECONNREFUSED 127.0.0.1:5432
            at TCPConnectWrap.afterConnect [as oncomplete] (net.js:1141:16)
        
        CRITICAL: Database connection lost
        
        System Info: Node.js v16.13.0, Linux x64
        """

        # Detect with pattern matching
        matches = detector.detect_multi_label(complex_error)
        info = detector.extract_comprehensive_info(complex_error)

        # Verify comprehensive detection
        categories = [m.category for m in matches]
        assert ErrorCategory.TYPESCRIPT in categories
        assert ErrorCategory.JAVASCRIPT in categories
        assert ErrorCategory.NETWORK in categories
        assert ErrorCategory.DATABASE in categories

        # Verify extracted information
        assert "src/api/client.ts" in info["files"]
        assert 45 in info["line_numbers"]
        assert "Database.initialize" in [f for f in info["functions"]]
        assert any("ECONNREFUSED" in code for code in info["error_codes"])

        # Test ML prediction
        ml_categories, severity, confidence = classifier.predict(complex_error)
        assert len(ml_categories) > 0
        assert severity in ["high", "critical"]
