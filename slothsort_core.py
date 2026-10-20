"""Core helpers for SlothSort AI.

The first iteration deliberately creates plans only; it never moves files.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import urllib.error
import urllib.request


CATEGORIES = {
    "Documents",
    "Images",
    "Audio",
    "Video",
    "Archives",
    "Spreadsheets",
    "Presentations",
    "Code",
    "Other",
}

EXTENSION_CATEGORIES = {
    ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents",
    ".txt": "Documents", ".rtf": "Documents", ".odt": "Documents",
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images", ".gif": "Images",
    ".webp": "Images", ".svg": "Images", ".heic": "Images",
    ".mp3": "Audio", ".wav": "Audio", ".aac": "Audio", ".flac": "Audio",
    ".mp4": "Video", ".mov": "Video", ".mkv": "Video", ".webm": "Video",
    ".zip": "Archives", ".tar": "Archives", ".gz": "Archives", ".7z": "Archives",
    ".csv": "Spreadsheets", ".xls": "Spreadsheets", ".xlsx": "Spreadsheets",
    ".ppt": "Presentations", ".pptx": "Presentations", ".odp": "Presentations",
    ".py": "Code", ".js": "Code", ".ts": "Code", ".html": "Code", ".css": "Code",
    ".java": "Code", ".cpp": "Code", ".rs": "Code", ".go": "Code",
}


@dataclass(frozen=True)
class FileSuggestion:
    filename: str
    category: str


def classify_filename(filename: str) -> str:
    """Classify by file extension without opening its contents."""
    suffix = Path(filename).suffix.lower()
    return EXTENSION_CATEGORIES.get(suffix, "Other")


def normalize_category(value: str) -> str:
    """Return a known category, or Other for untrusted model output."""
    cleaned = value.strip().strip('"').strip("'")
    for category in CATEGORIES:
        if cleaned.casefold() == category.casefold():
            return category
    return "Other"


def ollama_suggest_category(
    filename: str,
    model: str = "gemma3:1b",
    base_url: str = "http://localhost:11434",
    timeout: float = 12.0,
) -> str:
    """Ask a local Ollama model for a category; only filenames are sent."""
    endpoint = base_url.rstrip("/") + "/api/generate"
    prompt = (
        "Classify this filename into exactly one category from: "
        + ", ".join(sorted(CATEGORIES))
        + ". Output only the category. Filename: "
        + json.dumps(filename)
    )
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(
        endpoint, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            parsed = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not get a response from Ollama at {endpoint}") from exc
    return normalize_category(str(parsed.get("response", "")))


def safe_destination(root: Path, filename: str, category: str) -> Path:
    """Build a safe destination path without allowing path traversal."""
    root = root.expanduser().resolve()
    candidate = Path(filename)
    if candidate.name != filename or filename in {"", ".", ".."}:
        raise ValueError("filename must be a plain file name, not a path")
    safe_category = normalize_category(category)
    destination = (root / safe_category / filename).resolve()
    if root not in destination.parents:
        raise ValueError("destination escaped the selected root")
    return destination


def plan_organization(root: Path, filenames: list[str]) -> list[FileSuggestion]:
    """Return a deterministic organization plan; does not touch the filesystem."""
    return [
        FileSuggestion(filename=filename, category=classify_filename(filename))
        for filename in filenames
    ]
