from pathlib import Path
import pytest

from slothsort_core import (
    classify_filename,
    normalize_category,
    plan_organization,
    safe_destination,
)


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("report.PDF", "Documents"),
        ("photo.jpeg", "Images"),
        ("song.mp3", "Audio"),
        ("movie.mp4", "Video"),
        ("archive.zip", "Archives"),
        ("budget.xlsx", "Spreadsheets"),
        ("slides.pptx", "Presentations"),
        ("script.py", "Code"),
        ("unknown.bin", "Other"),
    ],
)
def test_classify_filename(filename, expected):
    assert classify_filename(filename) == expected


def test_normalize_untrusted_category():
    assert normalize_category("documents") == "Documents"
    assert normalize_category("run arbitrary code") == "Other"


def test_safe_destination_stays_inside_root(tmp_path: Path):
    assert safe_destination(tmp_path, "report.pdf", "Documents") == (
        tmp_path.resolve() / "Documents" / "report.pdf"
    )


@pytest.mark.parametrize("filename", ["../secrets.txt", "nested/file.txt", "..", ""])
def test_safe_destination_rejects_paths(tmp_path: Path, filename: str):
    with pytest.raises(ValueError):
        safe_destination(tmp_path, filename, "Documents")


def test_plan_organization_does_not_move_files(tmp_path: Path):
    (tmp_path / "report.pdf").write_text("sample")
    plan = plan_organization(tmp_path, ["report.pdf", "photo.jpg"])
    assert [(item.filename, item.category) for item in plan] == [
        ("report.pdf", "Documents"),
        ("photo.jpg", "Images"),
    ]
    assert (tmp_path / "report.pdf").exists()
    assert not (tmp_path / "Documents").exists()
