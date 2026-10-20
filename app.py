from pathlib import Path
import os
import streamlit as st

from slothsort_core import classify_filename, ollama_suggest_category, safe_destination

st.set_page_config(page_title="SlothSort AI", page_icon="🦥", layout="wide")
st.title("🦥 SlothSort AI")
st.caption("A careful, local-first file organizer with optional open-weight AI.")
st.info("Review the proposed organization first. This starter version never moves or deletes files.")

with st.sidebar:
    st.header("AI settings")
    use_ollama = st.toggle("Use local Ollama model (recommended)", value=True)
    model = st.text_input("Model", "gemma3:1b", disabled=not use_ollama)
    ollama_url = st.text_input("Ollama URL", os.getenv("OLLAMA_HOST", "http://localhost:11434"), disabled=not use_ollama)
    st.caption("The Ollama endpoint must be reachable from the machine running Streamlit.")

tab_folder, tab_samples = st.tabs(["Scan a folder", "Try sample filenames"])

with tab_folder:
    st.write("Enter a folder path on the machine running this app.")
    folder_text = st.text_input("Folder path", placeholder="/home/you/Downloads")
    if st.button("Preview organization", type="primary"):
        folder = Path(folder_text).expanduser()
        if not folder_text.strip():
            st.error("Enter a folder path first.")
        elif not folder.is_dir():
            st.error("Folder not found on the machine running Streamlit.")
        else:
            st.session_state["scan_root"] = str(folder.resolve())
            st.session_state["scan_files"] = sorted(
                item.name for item in folder.iterdir() if item.is_file()
            )
            st.success(f"Found {len(st.session_state['scan_files'])} files. Nothing was moved.")

    root = st.session_state.get("scan_root")
    scanned = st.session_state.get("scan_files", [])
    if root:
        rows = []
        for filename in scanned:
            category = None
            if use_ollama:
                try:
                    category = ollama_suggest_category(filename, model=model, base_url=ollama_url)
                except Exception as exc:
                    st.warning(f"Ollama unavailable for {filename!r}; using extension rules. {exc}")
            category = category or classify_filename(filename)
            rows.append({
                "File": filename,
                "Suggested category": category,
                "Preview destination": str(safe_destination(Path(root), filename, category)),
            })
        st.subheader("Preview")
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.caption("No file moves or deletes are implemented in this version.")

with tab_samples:
    samples = st.text_area(
        "One filename per line",
        "invoice_october.pdf\nfamily_photo.jpg\nmeeting_notes.docx\nbackup.zip\nlecture_recording.mp4",
        height=150,
    )
    if st.button("Categorize sample names"):
        rows = []
        for filename in (line.strip() for line in samples.splitlines() if line.strip()):
            category = None
            if use_ollama:
                try:
                    category = ollama_suggest_category(filename, model=model, base_url=ollama_url)
                except Exception as exc:
                    st.warning(f"Ollama unavailable for {filename!r}; using extension rules. {exc}")
            rows.append({"File": filename, "Suggested category": category or classify_filename(filename)})
        st.dataframe(rows, use_container_width=True, hide_index=True)

st.divider()
st.caption("Privacy: files are not opened or uploaded. Optional Ollama prompts contain filenames only.")
