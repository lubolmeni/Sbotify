# Sbotify 🎵🤖

Sbotify es un bot de Telegram inteligente que combina el poder de **Google Gemini** y **Spotify** para ofrecerte una experiencia musical personalizada.

## 🚀 Características

El bot cuenta con varios comandos para ayudarte a descubrir música y crear playlists:

### 1. `/situacion [descripción]`
Crea una playlist automática basada en una situación específica.
- **Ejemplo:** `/situacion música para estudiar concentrado y tranquilo`
- **Cómo funciona:** Gemini analiza tu descripción, sugiere canciones adecuadas y el bot crea una playlist en tu cuenta de Spotify con esas canciones.

### 2. `/animo [estado]`
Te recomienda una canción perfecta para tu estado de ánimo actual.
- **Ejemplo:** `/animo me siento un poco nostálgico pero feliz`
- **Cómo funciona:** Gemini interpreta tu emoción y busca una canción ("track") específica en Spotify que resuene con lo que sientes, acompañándola de un mensaje de aliento.

### 3. `/recomendar [tema/artista]`
Te sugiere música, artistas o podcasts basados en tus gustos.
- **Ejemplo:** `/recomendar artistas similares a The Cure`
- **Cómo funciona:** Busca recomendaciones precisas en Spotify (canciones, artistas, álbumes o podcasts) y te devuelve el enlace junto con un comentario personalizado.

### 4. `/playlist [canciones]`
Crea una playlist a partir de una lista de canciones que le pases en el mensaje.
- **Ejemplo:** `/playlist Bohemian Rhapsody, Hotel California, Stairway to Heaven`
- **Cómo funciona:** Identifica las canciones en tu mensaje, las busca en Spotify y genera una nueva playlist con ellas.

---

## 🛠️ Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

- **`main.py`**: El archivo principal que ejecuta el bot de Telegram. Maneja los comandos (`/situacion`, `/animo`, `/recomendar`, `/playlist`) y coordina la lógica entre los adaptadores.
- **`adapters/`**: Carpeta que contiene los módulos de integración con servicios externos.
    - **`spotify_adapter.py`**: Maneja la comunicación con la API de Spotify.
        - `buscar_en_spotify(query, search_type)`: Busca contenido en Spotify.
        - `crear_playlist(nombre, canciones)`: Crea una playlist y agrega canciones.
    - **`gemini_adapter.py`**: Maneja la comunicación con la API de Google Gemini.
        - `preguntar_gemini(pregunta, instrucciones, estructura_salida)`: Envía prompts a Gemini y procesa las respuestas (incluyendo formato JSON).

---

## ⚙️ Configuración e Instalación

### Prerrequisitos
- Python 3.8+
- Una cuenta de Spotify y una aplicación creada en el [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
- Una API Key de Google Gemini (Google AI Studio).
- Un Token de Bot de Telegram (obtenido con @BotFather).

### Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd Sbotify
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar variables de entorno:**
    Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

    ```env
    TELEGRAM_BOT_TOKEN=tu_token_de_telegram
    GEMINI_API_KEY=tu_api_key_de_gemini
    SPOTIPY_CLIENT_ID=tu_client_id_de_spotify
    SPOTIPY_CLIENT_SECRET=tu_client_secret_de_spotify
    SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
    ```

    > **Nota:** Asegúrate de agregar `http://localhost:8888/callback` (o la URI que elijas) en la configuración de tu app en el Spotify Developer Dashboard.

### Ejecución

Para iniciar el bot:

```bash
python main.py
```

Al ejecutarlo por primera vez, se abrirá una ventana del navegador para que inicies sesión en Spotify y autorices a la aplicación.

---

## 📦 Dependencias Principales

- `pyTelegramBotAPI`: Para interactuar con la API de Telegram.
- `google-genai`: Para acceder a los modelos de Gemini.
- `spotipy`: Para interactuar con la API de Spotify.
- `python-dotenv`: Para manejar variables de entorno.