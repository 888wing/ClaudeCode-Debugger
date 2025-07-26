"""Performance optimization utilities for error detection."""

import logging
import mmap
import multiprocessing as mp
import queue
import re
import threading
import time
from collections import deque
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class CompiledPatternCache:
    """Thread-safe cache for compiled regex patterns."""

    def __init__(self, max_size: int = 1000):
        """Initialize the pattern cache."""
        self._cache = {}
        self._access_order = deque(maxlen=max_size)
        self._lock = threading.RLock()
        self.max_size = max_size

    @lru_cache(maxsize=1000)
    def compile_pattern(self, pattern: str, flags: int = 0) -> re.Pattern:
        """Compile and cache a regex pattern."""
        return re.compile(pattern, flags)

    def get(self, pattern: str, flags: int = 0) -> re.Pattern:
        """Get a compiled pattern from cache."""
        key = (pattern, flags)

        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._access_order.remove(key)
                self._access_order.append(key)
                return self._cache[key]

            # Compile new pattern
            compiled = self.compile_pattern(pattern, flags)

            # Add to cache
            if len(self._cache) >= self.max_size:
                # Remove least recently used
                oldest = self._access_order.popleft()
                del self._cache[oldest]

            self._cache[key] = compiled
            self._access_order.append(key)

            return compiled


class StreamProcessor:
    """Efficient stream processing for large files."""

    def __init__(self, chunk_size: int = 8192, overlap: int = 1024):
        """Initialize the stream processor."""
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.pattern_cache = CompiledPatternCache()

    def process_file_mmap(
        self, file_path: Path, patterns: List[Tuple[str, Any]]
    ) -> Iterator[Dict[str, Any]]:
        """
        Process file using memory mapping for efficiency.

        Args:
            file_path: Path to the file.
            patterns: List of (pattern, metadata) tuples.

        Yields:
            Matches with metadata.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as f:
            # Use memory mapping for large files
            if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped:
                    yield from self._process_mmap(mmapped, patterns)
            else:
                # Read smaller files normally
                content = f.read().decode("utf-8", errors="ignore")
                yield from self._process_string(content, patterns)

    def _process_mmap(
        self, mmapped: mmap.mmap, patterns: List[Tuple[str, Any]]
    ) -> Iterator[Dict[str, Any]]:
        """Process memory-mapped file."""
        position = 0
        file_size = len(mmapped)

        while position < file_size:
            # Read chunk
            chunk_end = min(position + self.chunk_size, file_size)
            chunk = mmapped[position:chunk_end].decode("utf-8", errors="ignore")

            # Add overlap from previous chunk if not at start
            if position > 0:
                overlap_start = max(0, position - self.overlap)
                overlap_chunk = mmapped[overlap_start:position].decode(
                    "utf-8", errors="ignore"
                )
                chunk = overlap_chunk + chunk

            # Process chunk
            for match in self._process_string(chunk, patterns):
                # Adjust positions for actual file position
                if position > 0:
                    match["position"] += position - len(overlap_chunk)
                yield match

            position = chunk_end

    def _process_string(
        self, content: str, patterns: List[Tuple[str, Any]]
    ) -> Iterator[Dict[str, Any]]:
        """Process string content with patterns."""
        for pattern_str, metadata in patterns:
            pattern = self.pattern_cache.get(pattern_str, re.MULTILINE | re.IGNORECASE)

            for match in pattern.finditer(content):
                yield {
                    "match": match,
                    "pattern": pattern_str,
                    "metadata": metadata,
                    "position": match.start(),
                    "text": match.group(0),
                    "groups": match.groups(),
                }


class ParallelErrorDetector:
    """Parallel error detection for maximum performance."""

    def __init__(self, num_workers: Optional[int] = None):
        """Initialize parallel detector."""
        self.num_workers = num_workers or mp.cpu_count()
        self.chunk_queue = queue.Queue(maxsize=100)
        self.result_queue = queue.Queue()
        self.pattern_cache = CompiledPatternCache()

    def process_file_parallel(
        self,
        file_path: Path,
        patterns: List[Tuple[str, Any]],
        chunk_size: int = 1024 * 1024,
    ) -> List[Dict[str, Any]]:
        """
        Process file in parallel chunks.

        Args:
            file_path: Path to the file.
            patterns: List of (pattern, metadata) tuples.
            chunk_size: Size of chunks to process.

        Returns:
            List of all matches.
        """
        file_path = Path(file_path)
        file_size = file_path.stat().st_size

        # For small files, use single-threaded processing
        if file_size < 5 * 1024 * 1024:  # 5MB
            processor = StreamProcessor(chunk_size)
            return list(processor.process_file_mmap(file_path, patterns))

        # Prepare chunks
        chunks = self._prepare_chunks(file_path, chunk_size)

        # Process in parallel
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            futures = []

            for chunk_info in chunks:
                future = executor.submit(
                    self._process_chunk, file_path, chunk_info, patterns
                )
                futures.append((future, chunk_info))

            # Collect results
            all_matches = []
            for future, chunk_info in futures:
                try:
                    matches = future.result(timeout=30)
                    all_matches.extend(matches)
                except Exception as e:
                    logger.error(f"Error processing chunk {chunk_info}: {e}")

        # Sort by position
        all_matches.sort(key=lambda x: x["position"])

        # Deduplicate overlapping matches
        return self._deduplicate_matches(all_matches)

    def _prepare_chunks(self, file_path: Path, chunk_size: int) -> List[Dict[str, int]]:
        """Prepare chunk information for parallel processing."""
        file_size = file_path.stat().st_size
        chunks = []
        position = 0
        overlap = min(1024, chunk_size // 10)  # 10% overlap

        while position < file_size:
            chunk_end = min(position + chunk_size, file_size)
            chunks.append(
                {
                    "start": position,
                    "end": chunk_end,
                    "overlap_start": max(0, position - overlap) if position > 0 else 0,
                }
            )
            position = chunk_end

        return chunks

    @staticmethod
    def _process_chunk(
        file_path: Path, chunk_info: Dict[str, int], patterns: List[Tuple[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process a single chunk (runs in separate process)."""
        matches = []

        with open(file_path, "rb") as f:
            # Read chunk with overlap
            f.seek(chunk_info["overlap_start"])
            chunk_data = f.read(chunk_info["end"] - chunk_info["overlap_start"])

            try:
                chunk_text = chunk_data.decode("utf-8", errors="ignore")
            except Exception:
                return matches

            # Process patterns
            for pattern_str, metadata in patterns:
                pattern = re.compile(pattern_str, re.MULTILINE | re.IGNORECASE)

                for match in pattern.finditer(chunk_text):
                    # Only include if match starts within actual chunk range
                    match_pos = chunk_info["overlap_start"] + match.start()
                    if chunk_info["start"] <= match_pos < chunk_info["end"]:
                        matches.append(
                            {
                                "pattern": pattern_str,
                                "metadata": metadata,
                                "position": match_pos,
                                "text": match.group(0),
                                "groups": match.groups(),
                            }
                        )

        return matches

    def _deduplicate_matches(
        self, matches: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate matches from overlapping chunks."""
        if not matches:
            return matches

        deduped = []
        seen_positions = set()

        for match in matches:
            # Create unique key
            key = (match["position"], match["pattern"], match["text"])

            if key not in seen_positions:
                seen_positions.add(key)
                deduped.append(match)

        return deduped


class OptimizedErrorAggregator:
    """Aggregate and summarize errors efficiently."""

    def __init__(self):
        """Initialize the aggregator."""
        self.error_counts = {}
        self.error_samples = {}
        self.severity_distribution = {}
        self.time_series = []

    def add_error(
        self,
        category: str,
        severity: str,
        timestamp: Optional[str] = None,
        sample_text: Optional[str] = None,
    ):
        """Add an error to the aggregation."""
        # Update counts
        self.error_counts[category] = self.error_counts.get(category, 0) + 1

        # Update severity distribution
        if category not in self.severity_distribution:
            self.severity_distribution[category] = {}
        self.severity_distribution[category][severity] = (
            self.severity_distribution[category].get(severity, 0) + 1
        )

        # Keep samples (max 5 per category)
        if sample_text and category not in self.error_samples:
            self.error_samples[category] = []
        if sample_text and len(self.error_samples.get(category, [])) < 5:
            self.error_samples[category].append(sample_text[:200])

        # Time series
        if timestamp:
            self.time_series.append((timestamp, category, severity))

    def get_summary(self) -> Dict[str, Any]:
        """Get aggregated summary."""
        # Calculate statistics
        total_errors = sum(self.error_counts.values())

        # Top categories
        top_categories = sorted(
            self.error_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # Severity breakdown
        severity_totals = {}
        for cat_severities in self.severity_distribution.values():
            for severity, count in cat_severities.items():
                severity_totals[severity] = severity_totals.get(severity, 0) + count

        # Time series analysis (if available)
        time_analysis = self._analyze_time_series() if self.time_series else None

        return {
            "total_errors": total_errors,
            "unique_categories": len(self.error_counts),
            "top_categories": top_categories,
            "severity_breakdown": severity_totals,
            "error_samples": self.error_samples,
            "time_analysis": time_analysis,
        }

    def _analyze_time_series(self) -> Dict[str, Any]:
        """Analyze time series data."""
        if not self.time_series:
            return {}

        # Sort by timestamp
        self.time_series.sort(key=lambda x: x[0])

        # Find peak error times
        time_buckets = {}
        for timestamp, category, severity in self.time_series:
            # Extract hour (simple bucketing)
            try:
                hour = timestamp.split()[1].split(":")[0]
                time_buckets[hour] = time_buckets.get(hour, 0) + 1
            except:
                continue

        peak_hour = (
            max(time_buckets.items(), key=lambda x: x[1])[0] if time_buckets else None
        )

        return {
            "total_events": len(self.time_series),
            "peak_hour": peak_hour,
            "hourly_distribution": time_buckets,
        }


class BatchProcessor:
    """Process multiple files in batch with optimizations."""

    def __init__(self, num_workers: Optional[int] = None):
        """Initialize batch processor."""
        self.num_workers = num_workers or mp.cpu_count()
        self.parallel_detector = ParallelErrorDetector(num_workers)

    def process_directory(
        self,
        directory: Path,
        patterns: List[Tuple[str, Any]],
        file_pattern: str = "*.log",
    ) -> Dict[str, Any]:
        """
        Process all matching files in a directory.

        Args:
            directory: Directory path.
            patterns: Error patterns to search for.
            file_pattern: Glob pattern for files.

        Returns:
            Aggregated results.
        """
        directory = Path(directory)
        aggregator = OptimizedErrorAggregator()

        # Find all matching files
        files = list(directory.glob(file_pattern))
        logger.info(f"Found {len(files)} files to process")

        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = []

            for file_path in files:
                future = executor.submit(
                    self._process_single_file, file_path, patterns, aggregator
                )
                futures.append((future, file_path))

            # Wait for completion
            for future, file_path in futures:
                try:
                    future.result(timeout=60)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")

        return aggregator.get_summary()

    def _process_single_file(
        self,
        file_path: Path,
        patterns: List[Tuple[str, Any]],
        aggregator: OptimizedErrorAggregator,
    ):
        """Process a single file and update aggregator."""
        try:
            matches = self.parallel_detector.process_file_parallel(file_path, patterns)

            # Add matches to aggregator
            for match in matches:
                metadata = match.get("metadata", {})
                aggregator.add_error(
                    category=metadata.get("category", "unknown"),
                    severity=metadata.get("severity", "medium"),
                    sample_text=match.get("text"),
                )

            logger.info(f"Processed {file_path.name}: {len(matches)} errors found")

        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
