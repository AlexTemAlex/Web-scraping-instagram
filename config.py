from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_PATH = Path(__file__).parent

CONTENT_EXTRACTORS_PATH = BASE_PATH / "content_extractors"

STORAGE_PATH = "storage_instagram.json"

EXCEL_FILE = "cuentas.xlsx"
SHEET_NAME = "Hoja1"

JSON_FILE_USERS_LIST = "user_list_persistence.json"
JSON_FILE_USER = "user_persistence.json"

BATCH_SIZE = 10

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")