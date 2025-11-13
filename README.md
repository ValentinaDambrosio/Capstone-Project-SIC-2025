### <h1> 🌸 OvulAI — Tu bot de confianza 💬✨
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Telegram Bot API](https://img.shields.io/badge/Telegram_Bot-API-blue?logo=telegram)
![AI & NLP](https://img.shields.io/badge/AI-NLP_Emotion_Analysis-pink)
![Status](https://img.shields.io/badge/Status-Activo-success)
> **OvulAI** es un asistente virtual creado para acompañar emocionalmente a mujeres y personas menstruantes.  
> Podés **charlar, descargar tensión, registrar tu ciclo, o simplemente expresarte libremente.**  
> El bot te escucha, analiza tus emociones y responde con empatía ❤️


## 🌼 Objetivo del proyecto
Crear un **bot de Telegram** que combine **Inteligencia Artificial, Procesamiento de Lenguaje Natural (NLP)** y **análisis emocional**, para ofrecer acompañamiento y educación menstrual desde una perspectiva empática y segura.  


OvulAI busca **romper el tabú sobre la menstruación** y promover el **autoconocimiento corporal y emocional.**




### <h2>🧠 ¿Qué puede hacer OvulAI?




| Función | Descripción |
|----------|-------------|
| 💭 **Hablar de tus emociones** | Analiza el mensaje detectando si el usuario está triste, feliz o ansioso. Da respuestas empáticas y, si percibe emociones negativas, recomienda acudir a un especialista con un mapa interactivo de ayuda cercana. |
| 🔊 **Mensajes de voz** | Transcribe audios con IA (Grok) y analiza su contenido emocional basándose en un dataset propio. |
| 🖼️ **Análisis de imágenes** | Reconoce y describe imágenes relacionadas a la salud menstrual o anticonceptivos. |
| 📅 **Seguimiento del ciclo** | Permite registrar el ciclo menstrual, calcular en qué fase estás y cuándo será el próximo período estimado. También brinda consejos según cada fase. |
| 💬 **Respuestas automáticas** | Responde preguntas frecuentes y temas de ESI basándose en un dataset propio. |
| 📆 **Integración con Google Calendar** | Permite agendar tu próxima menstruación y recibir recordatorios automáticos. |




### <h2> 🚀 Cómo usarlo
1. **Abrí Telegram** y buscá el bot 👉 [@OvulAI_Bot](https://t.me/OvulAI_Bot)
2. Escribí `/start`
3. Elegí entre las opciones del menú principal:


<details>
<summary>🌸 Ver menú principal</summary>


### 🩷 Quiero hablar de cómo me siento
Detecta emociones con *Transformers*, responde con empatía y, si hay malestar, muestra un mapa con especialistas cercanos.


### 🌙 Registrar mi ciclo
Ingresá la fecha de tu última menstruación (`DD/MM/AAAA`).  
El bot valida errores (formato, fecha futura o antigua) y responde con mensajes personalizados.


### 💫 Mi cuerpo y mis síntomas
Muestra:
- Fase actual del ciclo  
- Próxima menstruación estimada  
- Último registro  
Y ofrece consejos adaptados a la fase (folicular, ovulatoria, lútea o menstrual).


### 🎁 Sorprendeme
Devuelve una de tres opciones aleatorias:
- Horóscopo diario (vía API) ♈  
- GIFs de animales tiernos 🐶  
- Frases motivadoras ✨
</details>


## 🗣️ Funciones adicionales


- 🎙️ **Audios:** se transcriben y procesan emocionalmente.  
- 📸 **Imágenes:** se reconocen y describen con IA.  
- 💬 **Conversación libre:** responde a mensajes fuera del menú con base en su dataset.


## ⚙️ Arquitectura y características técnicas


- 🧩 **Diseño modular:** NLP, audio, imagen, sentimientos y ciclo menstrual.  
- 💻 **Arquitectura POO:** analizadores heredados de una clase base (`AnalizadorBase`).  
- 💬 **Normalización de lenguaje informal:** interpreta abreviaturas y expresiones coloquiales.  
- ⚠️ **Manejo robusto de excepciones:** mensajes claros ante errores del usuario.  
- 🔒 **Privacidad por diseño:** no almacena información sensible por defecto.  


## 🪄 Tecnologías utilizadas


| Categoría | Tecnologías |
|------------|--------------|
| 💬 Chatbot | [Telegram Bot API](https://core.telegram.org/bots) |
| 🤖 IA & NLP | Transformers, Grok, análisis de sentimientos |
| 🗣️ Audio | Speech-to-text con modelo IA |
| 🖼️ Imágenes | Clasificación y descripción automática |
| 🗓️ Base de datos | JSON / SQLite para registros simples |
| ⚙️ Backend | Python 3.10+, POO, modular design |








## 🛠️ Instalación y puesta en marcha


```bash
# 1️⃣ Clonar el repositorio
git clone git@github.com:tu-org/ovulai-bot.git
cd ovulai-bot


# 2️⃣ Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows


# 3️⃣ Instalar dependencias
pip install -r requirements.txt


# 4️⃣ Crear archivo .env
# Incluye tus claves de API y token del bot


# 5️⃣ Ejecutar el bot
python main.py
```


## ⚙️ Ejecución


El archivo `main.py` instancia la clase `TelegramBotHandler()`  
(ubicada en `core/bot.py`) y ejecuta `start()`.




## 💖 Equipo y créditos


Desarrollado por:  
- [**Pilar Del Greco**](https://www.linkedin.com/in/pilar-del-greco-3bba85272)  
- [**Valentina Dambrosio**](https://www.linkedin.com/in/valentina-dambrosio-b534362b7)  
- [**Luciana Cuevas Lagos**](https://www.linkedin.com/in/luciana-cuevas-lagos)


📚 *Proyecto Final — Capstone Project SIC 2025*


OvulAI busca ser una herramienta empática y educativa que acompañe a mujeres y personas menstruantes, promoviendo el bienestar emocional y corporal 🌷


## 🧩 Contribuir


¡Las contribuciones son bienvenidas!  
Si querés colaborar:


1. Hacé un fork del repositorio  
2. Creá una rama (`feature/nueva-funcion`)  
3. Hacé tus cambios  
4. Enviá un Pull Request 🌸