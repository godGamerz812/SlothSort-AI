from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from slothsort_core import (
    FileSuggestion,
    classify_filename,
    ollama_suggest_category,
    plan_organization,
    safe_destination,
)

st.set_page_config(page_title="SlothSort AI", page_icon="🦥", layout="wide")

st.title("🦥 SlothSort AI")
st.caption("A careful, local-first file organizer with optional open-weight AI.")

st.info(
    "Start with a preview. SlothSort never moves files automatically from this page. "
    "Review the suggested destinations before using the plan."
)

with st.sidebar:
    st.header("Settings")
    use_ollama = st.toggle("Use Ollama model (optional)", value=False)
    model = st.text_input("Ollama model", value="gemma3:1b", disabled=not use_ollama)
    ollama_url = st.text_input("Ollama URL", value=os.getenv("OLLAMA_HOST", "http://localhost:11434"), disabled=not use_ollama)
    st.caption("Ollama must be running and reachable from this computer.")

tab1, tab2 = st.tabs(["Plan from a folder", "Try sample filenames"])

with tab1:
    st.write("Enter a folder path on the machine running this app. The starter version only previews a plan.")
    folder_text = st.text_input("Folder path", placeholder="/home/you/Downloads")
    if st.button("Scan folder", type="primary"):
        folder = Path(folder_text).expanduser()
        if not folder_text.strip():
            st.error("Enter a folder path first.")
        elif not folder.is_dir():
            st.error("That directory could not be found on this machine.")
        else:
            files = sorted(p for p in folder.iterdir() if p.is_file())
            st.session_state["scan_root"] = str(folder.resolve())
            st.session_state["scan_files"] = [p.name for p in files]
            st.success(f"Found {len(files)} file(s). Nothing has been moved.")
    root = st.session_state.get("scan_root")
    scanned = st.session_state.get("scan_files", [])
    if root is not None:
        st.subheader("Organization preview")
        rows = []
        for filename in scanned:
            category = None
            if use_ollama:
                try:
                    category = ollama_suggest_category(filename, model=model, base_url=ollama_url)
                except Exception as exc:
                    st.warning(f"Ollama unavailable for {filename!r}; using filename rules. ({exc})")
            category = category or classify_filename(filename)
            dest = safe_destination(Path(root), filename, category)
            rows.append({"File": filename, "Suggested category": category, "Preview destination": str(dest)})
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.caption("This version is preview-only. It does not perform file moves; verify your plan before any real organization.")

with tab2:
    sample_text = st.text_area(
        "One filename per line",
        value="invoice_october.pdf\nfamily_photo.jpg\nmeeting_notes.docx\nbackup.zip\nlecture_recording.mp4",
        height=150,
    )
    if st.button("Categorize samples"):
        names = [line.strip() for line in sample_text.splitlines() if line.strip()]
        suggestions: list[FileSuggestion] = []
        for filename in names:
            category = None
            if use_ollama:
                try:
                    category = ollama_suggest_category(filename, model=model, base_url=ollama_url)
                except Exception as exc:
                    st.warning(f"Ollama unavailable for {filename!r}; using filename rules. ({exc})")
            suggestions.append(FileSuggestion(filename, category or classify_filename(filename)))
        st.dataframe(
            [{"File": item.filename, "Suggested category": item.category} for item in suggestions],
            use_container_width=True,
            hide_index=True,
        )

st.divider()
st.caption("Privacy note: no file contents are uploaded by this starter app. Ollama prompts contain filenames only.")
