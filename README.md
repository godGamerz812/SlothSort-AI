# 🦥 SlothSort AI

SlothSort AI helps people preview how to sort a messy folder. It categorizes filenames by extension and optionally asks an open-weight model served by [Ollama](https://ollama.com/) for a suggestion.

## Features
- Streamlit UI for scanning a folder on the machine running the app.
- Preview destinations by category.
- Extension-based fallback if AI is turned off or unavailable.
- Optional Ollama integration (default model: `gemma3:1b`).
- Category allowlist and path checks.
- Tests and GitHub Actions workflow.

## Safety and limitations
**This build is preview-only. It does not move, rename, or delete files.** It reads filenames and extensions only; it does not read file contents. If enabled, Ollama receives the filename to classify. The folder path refers to the computer running Streamlit, not automatically the device viewing the web page. A deployed cloud app cannot directly browse visitors' local folders, and a local Ollama service is not automatically reachable from the cloud.

## Run locally
Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

## Optional Ollama
1. Install and start Ollama from [ollama.com](https://ollama.com/).
2. Run `ollama pull gemma3:1b`.
3. Enable “Use local Ollama model” in the app sidebar.

If needed, set `OLLAMA_HOST` or change the URL in the app. Only use an Ollama endpoint you trust. The model receives filenames, not file contents.

## Tests
```bash
pytest -q
```

## Roadmap
- Optional, user-confirmed file moves with dry-run, collision handling, and an undo manifest.
- Broader categorization tests and accessibility improvements.

## License
MIT; see [LICENSE](LICENSE).
