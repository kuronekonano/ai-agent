"""
Storage layer for agent evaluation framework.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class BaseStore:
    """Base storage interface for execution records."""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "data/eval_runs"
        os.makedirs(self.storage_path, exist_ok=True)

    def append(self, record: Dict[str, Any]) -> None:
        """Append a record to storage."""
        raise NotImplementedError

    def query(self, filter_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query records based on filter specification."""
        raise NotImplementedError

    def close(self) -> None:
        """Close storage connection."""
        pass


class JSONLStore(BaseStore):
    """JSONL file-based storage implementation."""

    def __init__(self, storage_path: Optional[str] = None):
        super().__init__(storage_path)
        self.current_file = None
        self.file_handle = None

    def append(self, record: Dict[str, Any]) -> None:
        """Append record to JSONL file."""
        if self.file_handle is None:
            self._open_current_file()

        json_line = json.dumps(record, ensure_ascii=False)
        self.file_handle.write(json_line + "\n")
        self.file_handle.flush()

    def query(self, filter_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query records from all JSONL files in storage directory."""
        records = []

        for filename in os.listdir(self.storage_path):
            if filename.endswith(".jsonl"):
                filepath = os.path.join(self.storage_path, filename)
                records.extend(self._read_file(filepath, filter_spec))

        return records

    def _open_current_file(self) -> None:
        """Open or create current JSONL file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"eval_run_{timestamp}.jsonl"
        filepath = os.path.join(self.storage_path, filename)

        self.current_file = filepath
        self.file_handle = open(filepath, "a", encoding="utf-8")

    def _read_file(
        self, filepath: str, filter_spec: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Read and filter records from a JSONL file."""
        records = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        record = json.loads(line)
                        if self._matches_filter(record, filter_spec):
                            records.append(record)
                    except json.JSONDecodeError:
                        continue  # Skip invalid lines
        except FileNotFoundError:
            pass

        return records

    def _matches_filter(
        self, record: Dict[str, Any], filter_spec: Dict[str, Any]
    ) -> bool:
        """Check if record matches filter criteria."""
        if not filter_spec:
            return True

        for key, value in filter_spec.items():
            if key not in record:
                return False

            record_value = record[key]

            # Handle nested filtering
            if isinstance(value, dict) and isinstance(record_value, dict):
                if not self._matches_filter(record_value, value):
                    return False
            elif record_value != value:
                return False

        return True

    def close(self) -> None:
        """Close the file handle."""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None


def create_store(store_type: str = "jsonl", **kwargs) -> BaseStore:
    """Factory function to create storage instance."""
    if store_type == "jsonl":
        return JSONLStore(**kwargs)
    else:
        raise ValueError(f"Unknown store type: {store_type}")
