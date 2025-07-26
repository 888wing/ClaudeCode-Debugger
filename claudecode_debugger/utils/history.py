"""History management for ClaudeCode-Debugger."""

import json
import sqlite3
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


class HistoryManager:
    """Manages command history with SQLite backend."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """Initialize history manager with database."""
        if db_path is None:
            db_path = Path.home() / ".ccdebug" / "history.db"

        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    error_content TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    agent TEXT,
                    output_format TEXT,
                    metadata TEXT
                )
            """
            )

            # Create indexes for better performance
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON history(timestamp)
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_error_type
                ON history(error_type)
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_severity
                ON history(severity)
            """
            )

    def add_entry(self, entry: Dict[str, Any]):
        """Add a new history entry."""
        metadata = {
            k: v
            for k, v in entry.items()
            if k
            not in [
                "timestamp",
                "error_content",
                "error_type",
                "severity",
                "agent",
                "output_format",
            ]
        }

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO history
                (timestamp, error_content, error_type, severity, agent, output_format,
    metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    entry["timestamp"],
                    entry["error_content"],
                    entry["error_type"],
                    entry["severity"],
                    entry.get("agent"),
                    entry.get("output_format", "text"),
                    json.dumps(metadata) if metadata else None,
                ),
            )

    def get_entries(
        self,
        limit: int = 10,
        filter_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get history entries with optional filtering."""
        query = "SELECT * FROM history WHERE 1=1"
        params = []

        if filter_type:
            query += " AND error_type = ?"
            params.append(filter_type)

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)

            entries = []
            for row in cursor:
                entry = dict(row)
                if entry.get("metadata"):
                    entry.update(json.loads(entry["metadata"]))
                    del entry["metadata"]
                entries.append(entry)

        return entries

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search history entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM history
                WHERE error_content LIKE ?
                   OR error_type LIKE ?
                   OR agent LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (f"%{query}%", f"%{query}%", f"%{query}%", limit),
            )

            entries = []
            for row in cursor:
                entry = dict(row)
                if entry.get("metadata"):
                    entry.update(json.loads(entry["metadata"]))
                    del entry["metadata"]
                entries.append(entry)

        return entries

    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics."""
        with sqlite3.connect(self.db_path) as conn:
            # Total count
            total = conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]

            # Error type distribution
            cursor = conn.execute(
                """
                SELECT error_type, COUNT(*) as count
                FROM history
                GROUP BY error_type
            """
            )
            types = {row[0]: row[1] for row in cursor}

            # Severity distribution
            cursor = conn.execute(
                """
                SELECT severity, COUNT(*) as count
                FROM history
                GROUP BY severity
            """
            )
            severities = {row[0]: row[1] for row in cursor}

            # Time-based statistics
            now = datetime.now()
            last_24h = conn.execute(
                """
                SELECT COUNT(*) FROM history
                WHERE timestamp >= ?
            """,
                ((now - timedelta(hours=24)).isoformat(),),
            ).fetchone()[0]

            last_7d = conn.execute(
                """
                SELECT COUNT(*) FROM history
                WHERE timestamp >= ?
            """,
                ((now - timedelta(days=7)).isoformat(),),
            ).fetchone()[0]

            # Critical error count
            critical_count = conn.execute(
                """
                SELECT COUNT(*) FROM history
                WHERE severity = 'critical'
            """
            ).fetchone()[0]

            # Most common errors
            cursor = conn.execute(
                """
                SELECT error_type, COUNT(*) as count
                FROM history
                GROUP BY error_type
                ORDER BY count DESC
                LIMIT 5
            """
            )
            top_errors = [(row[0], row[1]) for row in cursor]

        return {
            "total": total,
            "types": types,
            "severities": severities,
            "last_24h": last_24h,
            "last_7d": last_7d,
            "critical_count": critical_count,
            "top_errors": top_errors,
            "success_rate": (
                ((total - critical_count) / total * 100) if total > 0 else 0
            ),
        }

    def clear(self):
        """Clear all history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM history")

    def export(self, format: str = "json") -> str:
        """Export history in specified format."""
        entries = self.get_entries(limit=1000)  # Get last 1000 entries

        if format == "json":
            return json.dumps(entries, indent=2)
        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            if entries:
                writer = csv.DictWriter(output, fieldnames=entries[0].keys())
                writer.writeheader()
                writer.writerows(entries)
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def import_data(self, data: str, format: str = "json"):
        """Import history from data."""
        if format == "json":
            entries = json.loads(data)
            for entry in entries:
                self.add_entry(entry)
        else:
            raise ValueError(f"Unsupported import format: {format}")
