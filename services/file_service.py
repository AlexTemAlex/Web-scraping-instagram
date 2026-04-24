import json
from pathlib import Path
import pandas as pd

def load_excel(file_path, sheet_name):
    return pd.read_excel(file_path, sheet_name=sheet_name)

def save_batch(path_json, buffer, carpeta="data"):
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)

    path_json = carpeta / path_json

    if path_json.exists():
        try:
            with open(path_json, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = []
    else:
        data = []

    data.extend(buffer)

    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)