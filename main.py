from playwright.sync_api import sync_playwright
import os

from scrappers.instagram_scrapper import InstagramScrapper
from ai_models.big_five_analizer import BigFiveAnalizer
from ui.menus import menu, config_menu
from ui.selector import seleccionar_json
from services.browser_service import iniciar_browser
from services.file_service import load_excel
from services.scraping_service import ejecutar_scraping
from config import *

def main():
    with sync_playwright() as p:
        ig = InstagramScrapper()
        browserHeadless = False
        
        while True:
            opcion = menu()
            
            if opcion == "0":
                break
            
            elif opcion == "1":
                browserHeadless = config_menu(ig, browserHeadless)
            
            elif opcion == "2":
                if not os.path.exists(EXCEL_FILE):
                    print(f"❌ No existe Excel: {EXCEL_FILE}")
                    continue

                df = load_excel(EXCEL_FILE, SHEET_NAME)
                df = df[df["url"].fillna("").str.strip() != ""]

                users = df[["id", "url"]].to_dict(orient="records")

                browser, page = iniciar_browser(p, browserHeadless)
                ig.page = page

                ejecutar_scraping(ig, users, JSON_FILE_USERS_LIST)

                browser.close()
                
            elif opcion == "3":
                username = input("Ingresa el usuario de Instagram: ").strip().replace("@", "")

                if not username:
                    print("❌ Usuario inválido")
                    continue

                user = {
                    "id": username,
                    "url": f"https://www.instagram.com/{username}/"
                }

                users = [user]
                JSON_FILE = f"{username}_{JSON_FILE_USER}"

                browser, page = iniciar_browser(p, browserHeadless)
                ig.page = page

                ejecutar_scraping(ig, users, JSON_FILE)

                browser.close()
                        
            elif opcion == "4":
                print("\nSelecciona el archivo JSON...")

                archivo_seleccionado = seleccionar_json()

                if not archivo_seleccionado:
                    print("❌ No seleccionaste ningún archivo")
                    continue

                print(f"Archivo seleccionado: {archivo_seleccionado}")

                analizer = BigFiveAnalizer(
                    api_key="TU_API_KEY",
                    input_json=archivo_seleccionado,
                    output_json="resultado_bigfive.json",
                    batch_size=10,
                    max_retries=3
                )

                analizer.ejecutar()

                print("\nAnálisis Big Five completado")
            
            else:
                print("❌ Opción inválida")
                input("ENTER...")

if __name__ == "__main__":
    main()