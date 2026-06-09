"""Reusable template demonstration package."""

from .sanitize import sanitize_for_llm
from .verdicts import Verdict, canonical_json, derive_verdict

__all__ = ["Verdict", "canonical_json", "derive_verdict", "sanitize_for_llm"]

