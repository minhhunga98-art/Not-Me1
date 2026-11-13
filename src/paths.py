"""
Centralized path resolver for Hưng Phát Multi-Agent System.
Supports local Windows/Linux development and read-only Serverless environments (Vercel/AWS Lambda).
"""

import os
import tempfile
from pathlib import Path

# Detect root directory dynamically
BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"


def get_artifacts_dir() -> Path:
    """Returns a writable directory for workflow artifacts."""
    target = BASE_DIR / "artifacts"
    try:
        target.mkdir(parents=True, exist_ok=True)
        test_file = target / ".write_test"
        test_file.touch()
        test_file.unlink()
        return target
    except (OSError, PermissionError):
        tmp_target = Path(tempfile.gettempdir()) / "hungphat_artifacts"
        tmp_target.mkdir(parents=True, exist_ok=True)
        return tmp_target


def get_reports_dir() -> Path:
    """Returns a writable directory for executive reports."""
    target = BASE_DIR / "reports"
    try:
        target.mkdir(parents=True, exist_ok=True)
        test_file = target / ".write_test"
        test_file.touch()
        test_file.unlink()
        return target
    except (OSError, PermissionError):
        tmp_target = Path(tempfile.gettempdir()) / "hungphat_reports"
        tmp_target.mkdir(parents=True, exist_ok=True)
        return tmp_target

