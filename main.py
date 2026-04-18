from browser import Browser
from playwright.sync_api import sync_playwright
import time
import os

storage_path = "storage_instagram.json"


def menu():
    print("\n===== SCRAPER MENU =====")
    print("1 Iniciar Navegador")
    print("0 Salir")
    return input("Selecciona una opción: ")

def ensure_session(p, storage_path):
    browser = Browser(p, headless=False)

    try:
        page = browser.start()
        page.goto("https://www.instagram.com/")

        input("Inicia sesión manualmente y presiona ENTER...")

        # guardar cookies + storage
        browser.context.storage_state(path=storage_path)
        print("✔ Cookies guardadas correctamente")

    finally:
        browser.close()

def main():
    with sync_playwright() as p:

        while True:
            opcion = menu()
            
            if opcion == "0":
                print("Saliendo...")
                break
            
            elif opcion == "1":  
                
                # Valida la existencia de cookies sino las crea mediante iniciar sesion manual
                if not os.path.exists(storage_path):
                    ensure_session(p, storage_path)
                
                # Iniciar navegador
                browser = Browser(p, cookies_path=storage_path, headless=False)
                main_page = browser.start()
                
                main_page.goto("https://www.instagram.com/")
                input("\nPresiona ENTER para volver al menú...")
                
                browser.close()

            else:
                print("❌ Opción inválida")
                input("ENTER...")

if __name__ == "__main__":
    main()