from browser import Browser
from playwright.sync_api import sync_playwright
import pandas as pd
import time
import os
from instagram_scrapper import InstagramScrapper
import json

STORAGE_PATH_INSTAGRAM = "storage_instagram.json"
STORAGE_PATH = STORAGE_PATH_INSTAGRAM

EXCEL_FILE = "cuentas.xlsx"
SHEET_NAME = "Hoja1"

ARCHIVO_JSON = "persistencia.json"

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

def process_profile(ig, users, user_id, url):
    print(f"   ID: {user_id}\n   URL: {url}")

    try:
        ig.abrir_perfil(url)
        data = ig.get_user_info()  
        if data:
            users[user_id] = users.get(user_id, {}) | data
        else:
            users[user_id] = users.get(user_id, {})      
                    
        print("   Datos Extraidos:")
        print(f"{json.dumps(users[user_id], indent=4, ensure_ascii=False)}\n")
        
        # guardar_json_incremental(ARCHIVO_JSON, info)
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

                users = df.set_index("id")[["url"]].to_dict(orient="index")     # Estructura {id: {"url": "valor"},}
                valid_urls = users.items()
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

                print("")
                for idx, (user_id, info) in enumerate(users.items(), start=1):
                    url = info["url"]
                    
                    print(f"---------- Perfil {idx}/{total} ----------")
                    try:
                        process_profile(ig, users, user_id, url)
                    except Exception as e:
                        print(f"❌ Error procesando {url}: {e}")

                browser.close()
                print("\n✅ Proceso finalizado")
                print(f"Archivo JSON: {ARCHIVO_JSON}")

            else:
                print("❌ Opción inválida")
                input("ENTER...")

if __name__ == "__main__":
    main()