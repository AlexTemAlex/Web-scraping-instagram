from services.file_service import save_batch
from config import BATCH_SIZE

def process_profile(ig, user, buffer):
    try:
        ig.abrir_perfil(user["url"])
        data = ig.get_user_info()

        result = {
            "id": user["id"],
            "url": user["url"],
            **(data or {})
        }

        buffer.append(result)

    except Exception as e:
        print(f"❌ Error con {user['url']}: {e}")

def mostrar_funciones(ig):
    print("Datos a extraer:")
    for idx, item in enumerate(ig.dict_functions, start=1):
        if item["enabled"]:
            print(f"    {idx}. {item['name']}")


def ejecutar_scraping(ig, users, output_file):
    buffer = []

    print(f"\nTotal perfiles: {len(users)}")
    mostrar_funciones(ig)

    for idx, user in enumerate(users, start=1):
        print(f"Perfil {idx}/{len(users)}")

        process_profile(ig, user, buffer)

        if len(buffer) >= BATCH_SIZE:
            save_batch(output_file, buffer)
            buffer.clear()

    if buffer:
        save_batch(output_file, buffer)

    print(f"✅ Guardado en {output_file}")