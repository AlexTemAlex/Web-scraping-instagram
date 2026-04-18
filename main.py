from browser import Browser
import time

def menu():
    print("\n===== SCRAPER MENU =====")
    print("1 Iniciar Navegador")
    print("0 Salir")
    return input("Selecciona una opción: ")

def main():
    while True:
        opcion = menu()
        if opcion == "0":
            print("Saliendo...")
            break
        elif opcion == "1":
            # Iniciar navegador
            browser = Browser(headless=False)
            main_page = browser.start()
            main_page.goto("https://www.instagram.com/")
            time.sleep(10)
            browser.close()
            input("\nPresiona ENTER para volver al menú...")
        else:
            print("❌ Opción inválida")
            input("Presiona ENTER para continuar...")

if __name__ == "__main__":
    main()