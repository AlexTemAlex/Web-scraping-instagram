# 🧠 Instagram Big Five Analyzer

Proyecto de scraping de Instagram + análisis psicológico basado en el modelo Big Five utilizando IA.

El sistema extrae información de perfiles reales y analiza:
- Personalidad del usuario (Big Five)
- Percepción social basada en comentarios de terceros
- Comportamiento temporal (actividad en posts)

Modelo de IA utilizado:
- OpenAI: gpt-5-mini
---

# 📁 Estructura del proyecto

```
📦 root
│
├── ai_models/
│   └── big_five_analizer.py
│
├── content_extractors/
│   ├── location_creation_date.js
│   └── profile.js
│
├── data/
│   └── *_user_persistence.json
│
├── model/
│   └── browser.py
│
├── scrappers/
│   └── instagram_scrapper.py
│
├── services/
│   ├── browser_service.py
│   ├── file_service.py
│   └── scraping_service.py
│
├── ui/
│   ├── menus.py
│   └── selector.py
│
├── .env.example
├── .gitignore
├── README.md
├── config.py
├── main.py
├── requirements.txt
└── resultado_bigfive.json
```

---

# 📂 Descripción de módulos

## 🧠 ai_models/
Contiene los modelos de inteligencia artificial.

- `big_five_analizer.py`  
  Ejecuta el análisis psicológico basado en:
  - Big Five
  - percepción social
  - análisis temporal
  - confianza del modelo

---

## 🔍 scrappers/
Encargado de la extracción de datos desde Instagram.

- `instagram_scrapper.py`  
  Maneja navegación, scraping de perfiles, posts y comentarios.

---

## ⚙️ services/
Servicios reutilizables del sistema.

- `browser_service.py` → gestión del navegador Playwright
- `file_service.py` → lectura/escritura de archivos JSON/Excel
- `scraping_service.py` → lógica principal de scraping y batch processing

---

## 🖥️ ui/
Interfaz de usuario en consola.

- `menus.py` → menú principal del sistema
- `selector.py` → selección de archivos JSON

---

## 🧩 model/
Modelos base del navegador.

- `browser.py` → wrapper del navegador (Playwright)

---

## 🧬 content_extractors/
Extractores específicos de contenido.

- `profile.js` → extracción de datos del perfil
- `location_creation_date.js` → extracción de ubicación y fecha de creación

---

## 💾 data/
Almacena datos persistentes de usuarios scrapeados.

---

## ⚙️ Archivos principales

- `main.py` → punto de entrada del sistema
- `config.py` → configuración global
- `requirements.txt` → dependencias del proyecto
- `.env.example` → variables de entorno
- `resultado_bigfive.json` → resultados del análisis IA

---

# 📥 Datos que se scrapean (INPUT)

```json
{
  "username": "string",
  "bio": "string",
  "num_followers": "integer",
  "num_following": "integer",
  "category": "string | null",
  "posts": [
    {
      "text": "string",
      "date": "datetime (ISO 8601)"
    }
  ],
  "comments": [
    {
      "writer": "string",
      "text": "string"
    }
  ]
}
```

---

# 🧠 SALIDA DEL MODELO (OUTPUT IA)

```json
[
  {
    "username": "",
    "big_five": {
      "openness": 0-100,
      "conscientiousness": 0-100,
      "extraversion": 0-100,
      "agreeableness": 0-100,
      "neuroticism": 0-100
    },
    "analysis": {
      "personality_analysis": {
        "summary": "",
        "strengths": "",
        "risks": ""
      },
      "social_perception_analysis": {
        "summary": "",
        "sentiment": "positivo | neutro | negativo",
        "image_type": ""
      }
    },
    "profile_characteristics": [],
    "global_conclusion": "",
    "confidence": 0-100
  }
]
```

---

# ⚠️ IMPORTANTE

- Bio + posts → personalidad real
- Comments → percepción externa
- No mezclar fuentes
- El análisis depende de calidad del scraping

---

# 🚀 FLUJO DEL SISTEMA

```
Scraping Instagram
      ↓
Estructuración de datos
      ↓
Preprocesamiento
      ↓
Separación de fuentes:
   - Personalidad (bio + posts)
   - Percepción (comments)
      ↓
IA Big Five Analysis
      ↓
Resultados JSON
```

---

# 📦 REQUISITOS

- Python 3.10+
- Playwright

---

# 🔧 INSTALACIÓN

```bash
pip install -r requirements.txt
playwright install
```
