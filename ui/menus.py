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
        print("\n⚙️  CONFIGURACIÓN\n")

        # Estado del navegador
        estado_browser = "🕶️  Oculto" if browserHeadless else "🖥️  Visible"
        print(f"A. ({estado_browser}) Navegador")

        # Funciones del scrapper
        for i, f in enumerate(scrapper.dict_functions, start=1):
            estado = "🟢 Activo" if f["enabled"] else "🔴 Inactivo"
            
            print(f"{i}. ({estado}) {f['name']}")
            
            if f["args"]:
                for k, v in f["args"].items():
                    print(f"      {k}: {v}")

        print("0. Volver")

        op = input("Selecciona opción: ").strip().lower()

        # 👇 salir devolviendo estado actual
        if op == "0":
            return browserHeadless

        # 👇 cambiar estado del navegador
        if op == "a":
            browserHeadless = not browserHeadless
            continue

        try:
            idx = int(op) - 1
            func = scrapper.dict_functions[idx]

            print(f"\nEditando: {func['name']}")
            print("1. Activar/Desactivar")

            if func["args"]:
                print("2. Modificar args")

            print("0. Volver")

            sub = input("Opción: ").strip()

            if sub == "0":
                continue

            elif sub == "1":
                func["enabled"] = not func["enabled"]

            elif sub == "2" and func["args"]:
                for key in func["args"]:
                    actual = func["args"][key]
                    nuevo = input(f"{key} (actual={actual}): ")

                    if nuevo.strip():
                        try:
                            func["args"][key] = int(nuevo)
                        except ValueError:
                            print(f"⚠️ Valor inválido para {key}, se mantiene {actual}")

            else:
                print("❌ Opción inválida")

        except Exception as e:
            print("❌ Error:", e)