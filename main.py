from browser import Browser
from playwright.sync_api import sync_playwright
import pandas as pd
import time
import os
from instagram_scrapper import InstagramScrapper
import json
from pathlib import Path

BASE_PATH = Path(__file__).parent

STORAGE_PATH_INSTAGRAM = "storage_instagram.json"
STORAGE_PATH = STORAGE_PATH_INSTAGRAM

EXCEL_FILE = "cuentas.xlsx"
SHEET_NAME = "Hoja1"

JSON_FILE = "persistencia.json"

BATCH_SIZE = 10  # guardar cada N registros

def menu():
    print("\n===== SCRAPER MENU =====")
    print("1 Iniciar Navegador")
    print("0 Salir")
    return input("Selecciona una opción: ")

def ensure_session_instagram(p, STORAGE_PATH):
    """
    Abre el navegador y crea un archivo de cookies 
    al iniciar sesión manualmente en Instagram
    """
    browser = Browser(p, headless=False)

    try:
        page = browser.start()
        page.goto("https://www.instagram.com/")

        input("Inicia sesión manualmente y presiona ENTER...")

        # guardar cookies + storage
        browser.context.storage_state(path=STORAGE_PATH)
        print("✔ Cookies guardadas correctamente")

    finally:
        browser.close()

def load_excel(file_path, sheet_name=0):
    """
    Carga un archivo Excel y devuelve un DataFrame
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df

def save_batch(path_json, buffer):
    path_json = Path(path_json)

    if path_json.exists():
        try:
            with open(path_json, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = []
    else:
        data = []

    data.extend(buffer)

    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def process_profile(ig, users, user, buffer):
    user_id = user["id"]
    url = user["url"]
    print(f"   ID: {user_id}\n   URL: {url}")

    try:
        ig.abrir_perfil(url)
        data = ig.get_user_info()
    
        result = {
            "id": user_id,
            "url": url,
            **(data or {})
        }
        
        print("   Datos Extraidos:")
        print(f"{json.dumps(result, indent=4, ensure_ascii=False)}\n")
        
        buffer.append(result)   # Guardar en datos en buffer
    except Exception as e:
        print(f"❌ Error con {url}: {e}")

def main():
    with sync_playwright() as p:
        while True:
            opcion = menu()
            
            if opcion == "0":
                print("Saliendo...")
                break
            
            elif opcion == "1":                  
                if not os.path.exists(EXCEL_FILE):
                    print(f"❌ No existe Excel: {EXCEL_FILE}")
                    return
                
                df = load_excel(EXCEL_FILE, SHEET_NAME)
                
                df = df[df["url"].fillna("").str.strip() != ""]

                users = df[["id", "url"]].to_dict(orient="records")     # Lista de diccionarios [{"id": "valor","url": "valor"},]
                valid_urls = users
                total = len(valid_urls)
                
                # Valida la existencia de cookies sino las crea mediante sesión manual
                if not os.path.exists(STORAGE_PATH):
                    ensure_session_instagram(p, STORAGE_PATH)
                
                # Iniciar navegador
                browser = Browser(p, cookies_path=STORAGE_PATH, headless=False)
                browser.start_browser()
                page = browser.new_page()
                
                page.goto("https://www.instagram.com/")
                time.sleep(5)
                
                # Iniciar objeto IntagramScrapper
                ig = InstagramScrapper(page)
                
                print(f"\n#################### Iniciando Scrapeo - Total de perfiles {total} ####################")

                print("Datos a extraer:")
                
                for idx, func in enumerate(ig.list_functions, start=1):
                    print(f"    {idx}. {func.__name__}")

                buffer = []
                
                for idx, user in enumerate(users, start=1):
                    print(f"---------- Perfil {idx}/{total} ----------")

                    try:
                        process_profile(ig, users, user, buffer)
                        
                        if len(buffer) >= BATCH_SIZE:       # cuando llegue al tamaño, guarda y limpia
                            save_batch(JSON_FILE, buffer)
                            buffer.clear()
                            
                    except Exception as e:
                        print(f"❌ Error procesando {user["url"]}: {e}")
                
                if buffer:      # Guarda lo que quede al final
                    save_batch(JSON_FILE, buffer)
                
                browser.close()
                print("\n✅ Proceso finalizado")
                print(f"Archivo JSON: {JSON_FILE}")

            else:
                print("❌ Opción inválida")
                input("ENTER...")

if __name__ == "__main__":
    main()