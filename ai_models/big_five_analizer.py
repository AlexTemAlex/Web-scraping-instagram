import json
import os
import time
from openai import OpenAI
from tqdm import tqdm


class BigFiveAnalizer:

    def __init__(
        self,
        api_key: str,
        input_json: str,
        output_json: str,
        checkpoint_file: str = "checkpoint.json",
        batch_size: int = 10,
        max_retries: int = 3,
        model: str = "gpt-5-mini"
    ):
        # Configuración
        self.api_key = api_key
        self.input_json = input_json
        self.output_json = output_json
        self.checkpoint_file = checkpoint_file
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.model = model

        # Cliente OpenAI
        self.client = OpenAI(api_key=self.api_key)

    # ==========================
    # JSON
    # ==========================
    def cargar_json(self, path):
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def guardar_json_seguro(self, path, data):
        temp_path = path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(temp_path, path)

    # ==========================
    # BATCHES
    # ==========================
    def dividir_en_batches(self, lista):
        for i in range(0, len(lista), self.batch_size):
            yield lista[i:i + self.batch_size]

    # ==========================
    # API
    # ==========================
    def procesar_batch(self, batch):

        batch_filtrado = [
            {
                "username": item.get("username"),
                "category": item.get("category"),
                "bio": item.get("bio"),
                "location": item.get("location")
            }
            for item in batch
            if isinstance(item, dict)
        ]

        prompt = f"""
        Analiza cada objeto del siguiente JSON que contiene información de perfiles reales.

        Para cada perfil debes devolver:

        FORMATO DE RESPUESTA — SOLO JSON válido:

        [
        {{
            "id": "",
            "username": ""
        }}
        ]

        JSON:
        {json.dumps(batch_filtrado, ensure_ascii=False)}
        """

        for intento in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Eres un analista experto en perfiles."},
                        {"role": "user", "content": prompt}
                    ]
                )

                contenido = response.choices[0].message.content
                return json.loads(contenido)

            except Exception as e:
                print(f"Error API intento {intento+1}: {e}")
                time.sleep(2)

        return []

    # ==========================
    # CHECKPOINT
    # ==========================
    def cargar_checkpoint(self):
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                return json.load(f).get("ultimo_index", 0)
        return 0

    def guardar_checkpoint(self, index):
        self.guardar_json_seguro(self.checkpoint_file, {
            "ultimo_index": index
        })

    # ==========================
    # GUARDADO SIN DUPLICADOS
    # ==========================
    def guardar_resultado_incremental(self, resultado_batch):

        existente = self.cargar_json(self.output_json)

        usernames_existentes = {
            item.get("username")
            for item in existente
            if isinstance(item, dict) and "username" in item
        }

        nuevos = []

        for item in resultado_batch:
            if not isinstance(item, dict):
                continue

            username = item.get("username")
            if not username:
                continue

            if username not in usernames_existentes:
                nuevos.append(item)

        existente.extend(nuevos)
        self.guardar_json_seguro(self.output_json, existente)

    # ==========================
    # EJECUCIÓN
    # ==========================
    def ejecutar(self):

        datos = self.cargar_json(self.input_json)
        if not datos:
            print("No hay datos.")
            return

        batches = list(self.dividir_en_batches(datos))
        ultimo_index = self.cargar_checkpoint()

        print(f"Reanudando desde batch {ultimo_index}/{len(batches)}")

        for i in tqdm(range(ultimo_index, len(batches))):
            batch = batches[i]

            try:
                resultado = self.procesar_batch(batch)

                if resultado:
                    self.guardar_resultado_incremental(resultado)

                self.guardar_checkpoint(i + 1)

            except KeyboardInterrupt:
                print("\nInterrumpido manualmente.")
                return
            except Exception as e:
                print(f"\nError batch {i}: {e}")
                return

        print("\nProceso completado.")

        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)