from pathlib import Path
import json, urllib.request, urllib.error

CATEGORIES={"Documents","Images","Audio","Video","Archives","Spreadsheets","Presentations","Code","Other"}
EXTENSIONS={".pdf":"Documents",".doc":"Documents",".docx":"Documents",".txt":"Documents",".rtf":"Documents",".jpg":"Images",".jpeg":"Images",".png":"Images",".gif":"Images",".webp":"Images",".mp3":"Audio",".wav":"Audio",".mp4":"Video",".mov":"Video",".zip":"Archives",".tar":"Archives",".gz":"Archives",".csv":"Spreadsheets",".xls":"Spreadsheets",".xlsx":"Spreadsheets",".ppt":"Presentations",".pptx":"Presentations",".py":"Code",".js":"Code",".ts":"Code",".html":"Code",".css":"Code",".java":"Code",".cpp":"Code"}
def classify_filename(filename:str)->str:
    """Classify by extension without reading file content."""
    return EXTENSIONS.get(Path(filename).suffix.lower(),"Other")
def normalize_category(value:str)->str:
    for category in CATEGORIES:
        if value.strip().strip('"').strip("'").casefold()==category.casefold(): return category
    return "Other"
def safe_destination(root:Path,filename:str,category:str)->Path:
    """Create a destination preview; reject path traversal and nested paths."""
    root=root.expanduser().resolve()
    if Path(filename).name!=filename or filename in {"",".",".."}: raise ValueError("Use a plain filename, not a path")
    dest=(root/normalize_category(category)/filename).resolve()
    if root not in dest.parents: raise ValueError("Destination escapes root")
    return dest
def ollama_suggest_category(filename:str,model:str="gemma3:1b",base_url:str="http://localhost:11434",timeout:float=12)->str:
    """Send filename only to Ollama and validate its category response."""
    prompt="Classify this filename into exactly one of: "+", ".join(sorted(CATEGORIES))+". Output only the category. Filename: "+json.dumps(filename)
    payload=json.dumps({"model":model,"prompt":prompt,"stream":False}).encode()
    req=urllib.request.Request(base_url.rstrip("/")+"/api/generate",data=payload,headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=timeout) as response: data=json.loads(response.read().decode())
    except (urllib.error.URLError,TimeoutError,json.JSONDecodeError) as exc:
        raise RuntimeError("Ollama request failed; check server URL and model.") from exc
    return normalize_category(str(data.get("response","")))
