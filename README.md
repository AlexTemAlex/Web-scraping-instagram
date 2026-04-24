# 🧠 Instagram Big Five Analyzer

Proyecto de scraping de Instagram + análisis psicológico basado en el modelo Big Five utilizando IA.

El sistema extrae información de perfiles reales y analiza:
- Personalidad del usuario (Big Five)
- Percepción social basada en comentarios de terceros
- Comportamiento temporal (actividad en posts)

---

# 📁 Estructura del proyecto

```
Pendiente
```

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
    "confidence": 0-100
  }
]
```

---

# 📊 QUÉ ANALIZA EL SISTEMA

## 🧠 Personalidad (Big Five)
- Bio del usuario
- Posts del usuario

## 👥 Percepción social
- Comentarios de otras personas
- Opiniones externas sobre el usuario

## ⏱️ Análisis temporal
- Fechas de posts
- Frecuencia de publicaciones
- Diferencias de tiempo entre posts

## 📊 Variables contextuales
- Número de seguidores
- Número de seguidos
- Categoría del perfil

---

# ⚠️ IMPORTANTE

- Los comentarios NO representan la personalidad del usuario.
- Solo representan percepción externa.
- La personalidad se infiere desde bio + posts.

---

# 🚀 FLUJO DEL SISTEMA

```
Scraping Instagram
      ↓
Estructuración de datos
      ↓
Preprocesamiento
      ↓
Separación:
   - Personalidad (bio + posts)
   - Percepción (comments)
      ↓
IA Big Five
      ↓
JSON estructurado
```

---

## 📦 REQUISITOS

- Python 3.10+
- Playwright

---

## 🔧 INSTALACIÓN

```bash
pip install -r requirements.txt
playwright install
```
