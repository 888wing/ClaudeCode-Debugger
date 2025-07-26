"""Machine Learning classifier for error detection."""

import json
import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import MultiLabelBinarizer

logger = logging.getLogger(__name__)


@dataclass
class TrainingExample:
    """Represents a training example for the classifier."""

    text: str
    categories: List[str]
    severity: str
    metadata: Dict[str, Any] = None


class ErrorMLClassifier:
    """Machine Learning classifier for error detection and classification."""

    def __init__(self, model_path: Optional[Path] = None):
        """Initialize the ML classifier."""
        self.vectorizer = None
        self.category_classifier = None
        self.severity_classifier = None
        self.mlb = None
        self.feature_extractors = []
        self.model_path = model_path

        if model_path and model_path.exists():
            self.load_model(model_path)
        else:
            self._initialize_models()

    def _initialize_models(self):
        """Initialize ML models and feature extractors."""
        # TF-IDF vectorizer with custom parameters
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            stop_words="english",
            lowercase=True,
            token_pattern=r"\b\w+\b|TS\d{4}|ERR_\w+",  # Include error codes
            sublinear_tf=True,
            min_df=2,
        )

        # Multi-label classifier for categories
        base_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1,
        )
        self.category_classifier = MultiOutputClassifier(base_classifier)

        # Classifier for severity
        self.severity_classifier = RandomForestClassifier(
            n_estimators=50, max_depth=10, random_state=42, n_jobs=-1
        )

        # Multi-label binarizer
        self.mlb = MultiLabelBinarizer()

        # Custom feature extractors
        self._setup_feature_extractors()

    def _setup_feature_extractors(self):
        """Setup custom feature extraction functions."""
        self.feature_extractors = [
            self._extract_length_features,
            self._extract_keyword_features,
            self._extract_pattern_features,
            self._extract_structural_features,
        ]

    def _extract_length_features(self, text: str) -> np.ndarray:
        """Extract text length features."""
        return np.array(
            [
                len(text),
                len(text.split("\n")),
                len(text.split()),
                np.mean([len(word) for word in text.split()]) if text.split() else 0,
            ]
        )

    def _extract_keyword_features(self, text: str) -> np.ndarray:
        """Extract keyword-based features."""
        keywords = {
            "error": ["error", "exception", "failed", "failure"],
            "warning": ["warning", "warn", "deprecated"],
            "critical": ["fatal", "critical", "crash", "panic"],
            "network": ["timeout", "connection", "refused", "cors"],
            "memory": ["memory", "heap", "stack", "overflow"],
            "type": ["type", "undefined", "null", "cannot read"],
        }

        features = []
        lower_text = text.lower()

        for category, words in keywords.items():
            count = sum(1 for word in words if word in lower_text)
            features.append(count)

        return np.array(features)

    def _extract_pattern_features(self, text: str) -> np.ndarray:
        """Extract pattern-based features."""
        import re

        patterns = [
            (r"TS\d{4}", "typescript_error"),
            (r"at\s+\w+\s*\(", "stack_trace"),
            (r"line\s+\d+", "line_number"),
            (r"https?://", "url"),
            (r"\w+Error:", "error_type"),
            (r'^\s*File\s+"', "file_reference"),
        ]

        features = []
        for pattern, _ in patterns:
            matches = len(re.findall(pattern, text, re.MULTILINE))
            features.append(matches)

        return np.array(features)

    def _extract_structural_features(self, text: str) -> np.ndarray:
        """Extract structural features from text."""
        lines = text.split("\n")

        features = [
            max(len(line) for line in lines) if lines else 0,  # Max line length
            np.std([len(line) for line in lines]) if len(lines) > 1 else 0,
            # Line length variance
            sum(1 for line in lines if line.strip().startswith("at ")),
            # Stack trace lines
            sum(1 for line in lines if ":" in line),  # Lines with colons
            text.count("(") + text.count("[") + text.count("{"),  # Opening brackets
        ]

        return np.array(features)

    def extract_features(self, texts: List[str]) -> np.ndarray:
        """Extract features from texts."""
        # TF-IDF features
        if hasattr(self.vectorizer, "transform"):
            tfidf_features = self.vectorizer.transform(texts).toarray()
        else:
            tfidf_features = self.vectorizer.fit_transform(texts).toarray()

        # Custom features
        custom_features = []
        for text in texts:
            text_features = []
            for extractor in self.feature_extractors:
                text_features.extend(extractor(text))
            custom_features.append(text_features)

        custom_features = np.array(custom_features)

        # Combine features
        return np.hstack([tfidf_features, custom_features])

    def train(
        self, training_examples: List[TrainingExample], validation_split: float = 0.2
    ):
        """
        Train the classifier on examples.

        Args:
            training_examples: List of training examples.
            validation_split: Fraction of data to use for validation.
        """
        if not training_examples:
            raise ValueError("No training examples provided")

        # Prepare data
        texts = [ex.text for ex in training_examples]
        categories = [ex.categories for ex in training_examples]
        severities = [ex.severity for ex in training_examples]

        # Fit vectorizer and extract features
        logger.info("Extracting features...")
        self.vectorizer.fit(texts)
        X = self.extract_features(texts)

        # Prepare labels
        y_categories = self.mlb.fit_transform(categories)
        y_severity = np.array(severities)

        # Split data
        X_train, X_val, y_cat_train, y_cat_val, y_sev_train, y_sev_val = (
            train_test_split(
                X, y_categories, y_severity, test_size=validation_split, random_state=42
            )
        )

        # Train category classifier
        logger.info("Training category classifier...")
        self.category_classifier.fit(X_train, y_cat_train)

        # Train severity classifier
        logger.info("Training severity classifier...")
        self.severity_classifier.fit(X_train, y_sev_train)

        # Evaluate
        if validation_split > 0:
            self._evaluate(X_val, y_cat_val, y_sev_val)

    def _evaluate(
        self, X_val: np.ndarray, y_cat_val: np.ndarray, y_sev_val: np.ndarray
    ):
        """Evaluate model performance."""
        # Category predictions
        y_cat_pred = self.category_classifier.predict(X_val)
        cat_f1 = f1_score(y_cat_val, y_cat_pred, average="weighted")
        logger.info(f"Category classification F1 score: {cat_f1:.3f}")

        # Severity predictions
        y_sev_pred = self.severity_classifier.predict(X_val)
        sev_report = classification_report(y_sev_val, y_sev_pred)
        logger.info(f"Severity classification report:\n{sev_report}")

    def predict(self, text: str) -> Tuple[List[Tuple[str, float]], str, float]:
        """
        Predict error categories and severity.

        Args:
            text: Error text to classify.

        Returns:
            Tuple of (categories with confidence, severity, overall confidence).
        """
        if not self.category_classifier or not self.severity_classifier:
            raise ValueError("Model not trained or loaded")

        # Extract features
        features = self.extract_features([text])

        # Predict categories with probabilities
        cat_probs = self.category_classifier.predict_proba(features)[0]
        categories = []

        for i, probs in enumerate(cat_probs):
            if hasattr(probs, "shape") and len(probs.shape) > 0:
                # Multi-class probability
                prob = probs[1] if len(probs) > 1 else probs[0]
            else:
                prob = probs

            if prob > 0.3:  # Confidence threshold
                category = self.mlb.classes_[i]
                categories.append((category, float(prob)))

        # Sort by confidence
        categories.sort(key=lambda x: x[1], reverse=True)

        # Predict severity
        severity = self.severity_classifier.predict(features)[0]
        severity_probs = self.severity_classifier.predict_proba(features)[0]
        severity_confidence = max(severity_probs)

        # Overall confidence
        overall_confidence = (
            np.mean([c[1] for c in categories[:3]]) if categories else 0.0
        )

        return categories, severity, overall_confidence

    def predict_batch(
        self, texts: List[str]
    ) -> List[Tuple[List[Tuple[str, float]], str, float]]:
        """Predict for multiple texts efficiently."""
        if not texts:
            return []

        # Extract features for all texts
        features = self.extract_features(texts)

        # Batch predictions
        cat_probs_batch = self.category_classifier.predict_proba(features)
        severities = self.severity_classifier.predict(features)
        severity_probs_batch = self.severity_classifier.predict_proba(features)

        results = []
        for i in range(len(texts)):
            # Process categories
            categories = []
            for j, probs in enumerate(cat_probs_batch[i]):
                if hasattr(probs, "shape") and len(probs.shape) > 0:
                    prob = probs[1] if len(probs) > 1 else probs[0]
                else:
                    prob = probs

                if prob > 0.3:
                    category = self.mlb.classes_[j]
                    categories.append((category, float(prob)))

            categories.sort(key=lambda x: x[1], reverse=True)

            # Severity
            severity = severities[i]
            severity_confidence = max(severity_probs_batch[i])

            # Overall confidence
            overall_confidence = (
                np.mean([c[1] for c in categories[:3]]) if categories else 0.0
            )

            results.append((categories, severity, overall_confidence))

        return results

    def save_model(self, path: Path):
        """Save the trained model."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        # Save components
        joblib.dump(self.vectorizer, path / "vectorizer.pkl")
        joblib.dump(self.category_classifier, path / "category_classifier.pkl")
        joblib.dump(self.severity_classifier, path / "severity_classifier.pkl")
        joblib.dump(self.mlb, path / "mlb.pkl")

        # Save metadata
        metadata = {
            "version": "1.0",
            "features": len(self.feature_extractors),
            "categories": list(self.mlb.classes_) if self.mlb else [],
        }

        with open(path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Model saved to {path}")

    def load_model(self, path: Path):
        """Load a trained model."""
        path = Path(path)

        if not path.exists():
            raise ValueError(f"Model path {path} does not exist")

        # Load components
        self.vectorizer = joblib.load(path / "vectorizer.pkl")
        self.category_classifier = joblib.load(path / "category_classifier.pkl")
        self.severity_classifier = joblib.load(path / "severity_classifier.pkl")
        self.mlb = joblib.load(path / "mlb.pkl")

        # Setup feature extractors
        self._setup_feature_extractors()

        logger.info(f"Model loaded from {path}")

    def update_model(self, new_examples: List[TrainingExample]):
        """Update model with new examples (incremental learning)."""
        if not new_examples:
            return

        # Extract current training data (this is a simplified approach)
        # In production, you'd want to store and manage training data properly

        # For now, just retrain with new examples
        # This is a placeholder for more sophisticated incremental learning
        logger.warning(
            "Incremental learning not fully implemented. Retraining with new examples only."
        )
        self.train(new_examples)

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        if not hasattr(self.category_classifier, "estimators_"):
            return {}

        # Get feature names
        feature_names = []
        if hasattr(self.vectorizer, "get_feature_names_out"):
            feature_names.extend(self.vectorizer.get_feature_names_out())

        # Add custom feature names
        custom_features = [
            "text_length",
            "line_count",
            "word_count",
            "avg_word_length",
            "error_keywords",
            "warning_keywords",
            "critical_keywords",
            "network_keywords",
            "memory_keywords",
            "type_keywords",
            "typescript_patterns",
            "stack_trace_patterns",
            "line_number_patterns",
            "url_patterns",
            "error_type_patterns",
            "file_reference_patterns",
            "max_line_length",
            "line_length_variance",
            "stack_trace_lines",
            "colon_lines",
            "bracket_count",
        ]
        feature_names.extend(custom_features)

        # Calculate average importance across all estimators
        importance_scores = {}

        for i, estimator in enumerate(self.category_classifier.estimators_):
            if hasattr(estimator, "feature_importances_"):
                for j, importance in enumerate(estimator.feature_importances_):
                    if j < len(feature_names):
                        name = feature_names[j]
                        if name not in importance_scores:
                            importance_scores[name] = []
                        importance_scores[name].append(importance)

        # Average the scores
        avg_importance = {
            name: np.mean(scores) for name, scores in importance_scores.items()
        }

        # Sort by importance
        return dict(
            sorted(avg_importance.items(), key=lambda x: x[1], reverse=True)[:50]
        )  # Top 50 features
