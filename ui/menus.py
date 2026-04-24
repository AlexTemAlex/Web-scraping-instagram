def menu():
    print("\n===== INSTAGRAM SCRAPER MENU =====")
    print("1 Configuración")
    print("2 Scrapear Lista")
    print("3 Scrapear Usuario")
    print("4 Analizador BigFive")
    print("0 Salir")
    return input("Selecciona: ")

def config_menu(scrapper, browserHeadless):
    while True:
        print("\n⚙️ CONFIGURACIÓN\n")

        estado_browser = "🕶️ Oculto" if browserHeadless else "🖥️ Visible"
        print(f"A. ({estado_browser}) Navegador")

        for i, f in enumerate(scrapper.dict_functions, start=1):
            estado = "🟢 Activo" if f["enabled"] else "🔴 Inactivo"
            print(f"{i}. ({estado}) {f['name']}")

        print("0. Volver")

        op = input("Selecciona: ").strip().lower()

        if op == "0":
            return browserHeadless

        if op == "a":
            browserHeadless = not browserHeadless
            continue