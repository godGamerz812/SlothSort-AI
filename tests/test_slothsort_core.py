from pathlib import Path
import pytest
from slothsort_core import classify_filename, normalize_category, safe_destination
@pytest.mark.parametrize(("name","category"),[("x.pdf","Documents"),("x.PNG","Images"),("x.mp3","Audio"),("x.mp4","Video"),("x.zip","Archives"),("x.csv","Spreadsheets"),("x.pptx","Presentations"),("x.py","Code"),("x.unknown","Other")])
def test_extension_categories(name,category): assert classify_filename(name)==category
def test_model_output_is_allowlisted():
    assert normalize_category("documents")=="Documents"
    assert normalize_category("do something unsafe")=="Other"
def test_safe_path(tmp_path:Path):
    assert safe_destination(tmp_path,"x.pdf","Documents")==tmp_path.resolve()/"Documents"/"x.pdf"
@pytest.mark.parametrize("name",["../x.txt","a/b.txt","..",""])
def test_reject_paths(tmp_path:Path,name):
    with pytest.raises(ValueError): safe_destination(tmp_path,name,"Documents")
