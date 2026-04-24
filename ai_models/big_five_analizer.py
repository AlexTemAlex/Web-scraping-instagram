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
        batch_filtrado = []

        print("\n📤 PREPARANDO BATCH PARA IA:")

        for item in batch:

            if not isinstance(item, dict):
                continue
                        
            user_data = {
                "username": item.get("username"),
                "bio": item.get("bio"),
                "num_followers": item.get("num_followers"),
                "num_following": item.get("num_following"),
                "category": item.get("category"),
                "posts": item.get("posts"),
                "comments": item.get("comments")
            }

            print("\n--------------------------------")
            print(f"USERNAME: {user_data.get('username')}")

            print("DATA ENVIADA COMPLETA:")

            print(json.dumps(user_data, indent=2, ensure_ascii=False))

            print("--------------------------------\n")

            if user_data:
                batch_filtrado.append(user_data)

        prompt = f"""
        Eres un psicólogo experto en análisis de personalidad Big Five y comportamiento social digital.

        IMPORTANTE:
        Los datos provienen de Instagram con estructura:

        - bio → texto del usuario (personalidad base)
        - posts → publicaciones del usuario (text + date)
        - comments → comentarios de otras personas (writer + text)

        REGLA CRÍTICA:
        NO mezclar fuentes:
        - BIO + POSTS = personalidad real
        - COMMENTS = percepción social externa

        -----------------------------------------
        TAREA 1: PERSONALIDAD REAL (BIG FIVE)
        -----------------------------------------
        Analiza usando:

        - bio
        - posts[].text
        - num_followers
        - num_following
        - category

        IMPORTANTE:
        Bio puede represnetar personalidad directa tambien
        Los demas campos ayudan a inferir contexto social.

        INTERPRETACIÓN:

        - num_followers → nivel de visibilidad social / popularidad
        - num_following → nivel de interacción social activa
        - category → identidad o rol social declarado

        Evalúa:
        - openness
        - conscientiousness
        - extraversion
        - agreeableness
        - neuroticism

        -----------------------------------------
        TAREA 2: ANÁLISIS TEMPORAL (MUY IMPORTANTE)
        -----------------------------------------
        Usa posts[].date para analizar comportamiento en el tiempo:

        Debes detectar:

        - frecuencia de publicación
        - cambios de actividad (periodos activos vs inactivos)
        - consistencia temporal
        - posibles picos emocionales o sociales
        - evolución del comportamiento en el tiempo

        Devuelve un resumen claro.

        -----------------------------------------
        TAREA 3: PERCEPCIÓN SOCIAL
        -----------------------------------------
        Analiza SOLO comments[]:

        - sentiment: positivo | neutro | negativo
        - image_type: (ej: líder, gracioso, reservado, conflictivo, admirado, criticado)
        - summary: resumen de percepción social

        -----------------------------------------
        TAREA 4: ANÁLISIS PSICOLÓGICO
        -----------------------------------------
        Genera dos análisis:

        - personality_analysis (Big Five + interpretación)
        - social_perception_analysis (comentarios + percepción externa)

        -----------------------------------------
        TAREA 5: CARACTERÍSTICAS DEL PERFIL
        -----------------------------------------
        Genera un array con las principales características del usuario:

        - rasgos dominantes
        - estilo social
        - comportamiento digital
        - tipo de interacción
        - nivel de actividad
        - tipo de personalidad percibida

        Ejemplo:
        "profile_characteristics": [
        "activo en redes",
        "alto nivel social",
        "comunicación abierta"
        ]

        -----------------------------------------
        TAREA 6: CONCLUSIÓN GENERAL
        -----------------------------------------
        Genera una conclusión global del perfil:

        - resumen integral del usuario
        - coherencia entre personalidad y percepción social
        - interpretación final psicológica

        -----------------------------------------
        TAREA 7: NIVEL DE CONFIANZA
        -----------------------------------------
        confidence (0-100):
        - cantidad de datos
        - calidad del contenido
        - coherencia temporal
        - consistencia general

        -----------------------------------------
        FORMATO DE RESPUESTA (SOLO JSON)
        -----------------------------------------

        [
        {{
            "username": "",
            "big_five": {{
                "openness": 0-100,
                "conscientiousness": 0-100,
                "extraversion": 0-100,
                "agreeableness": 0-100,
                "neuroticism": 0-100
            }},
            "temporal_analysis": {{
                "posting_frequency": "",
                "activity_pattern": "",
                "consistency": "",
                "summary": ""
            }},
            "analysis": {{
                "personality_analysis": {{
                    "summary": "",
                    "strengths": "",
                    "risks": ""
                }},
                "social_perception_analysis": {{
                    "summary": "",
                    "sentiment": "positivo | neutro | negativo",
                    "image_type": ""
                }}
            }},
            "profile_characteristics": [],
            "global_conclusion": "",
            "confidence": 0-100
        }}
        -----------------------------------------
        DATOS:
        {json.dumps(batch_filtrado, ensure_ascii=False)}
        """

        for intento in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Eres un psicólogo experto en Big Five."},
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

    def transformar_lista_usuarios(self, lista_usuarios: list) -> list:
        resultado_final = []

        for user in lista_usuarios:
            if not isinstance(user, dict):
                continue

            resultado = {}

            username = user.get("username")
            if username:
                resultado["username"] = username

            # ======================
            # CAMPOS BASE
            # ======================
            if user.get("num_followers") is not None:
                resultado["num_followers"] = user["num_followers"]

            if user.get("num_following") is not None:
                resultado["num_following"] = user["num_following"]

            if user.get("category"):
                resultado["category"] = user["category"]

            # ======================
            # BIO
            # ======================
            bio_textos = []
            for b in user.get("bio", []):
                if isinstance(b, dict):
                    bio_textos.extend([t for t in b.get("text", []) if t])

            if bio_textos:
                resultado["bio"] = " ".join(bio_textos)

            # ======================
            # POSTS
            # ======================
            posts = []

            # ======================
            # COMMENTS
            # ======================
            comments = []

            for key, value in user.items():
                if key.startswith("post_") and isinstance(value, dict):

                    post_text = value.get("text")
                    post_date = value.get("datetime_utc")

                    if post_text:
                        posts.append({
                            "text": post_text,
                            "date": post_date
                        })

                    for c in value.get("comments", []):
                        if isinstance(c, dict):

                            comment_text = c.get("text")
                            comment_writer = c.get("writer")

                            if comment_text:
                                comments.append({
                                    "writer": comment_writer,
                                    "text": comment_text
                                })

            if posts:
                resultado["posts"] = posts

            if comments:
                resultado["comments"] = comments

            resultado_final.append(resultado)

        return resultado_final
    # ==========================
    # EJECUCIÓN
    # ==========================
    def ejecutar(self):

        datos = self.cargar_json(self.input_json)
        if not datos:
            print("No hay datos.")
            return

        datos_limpios = self.transformar_lista_usuarios(datos)

        if not datos_limpios:
            print("No hay datos útiles para analizar.")
            return

        print(f"Usuarios originales: {len(datos)}")
        print(f"Usuarios útiles: {len(datos_limpios)}")

        batches = list(self.dividir_en_batches(datos_limpios))
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