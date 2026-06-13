"""Pytest configuration for ResearchForge tests."""
import sys
from pathlib import Path

# Ensure backend/ is importable
_backend = Path(__file__).resolve().parent.parent / "backend"
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))
