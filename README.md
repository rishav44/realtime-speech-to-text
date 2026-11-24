# 🎙️ VoiceFlow AI – Real-Time Multilingual Speech-to-Text

A real-time multilingual speech recognition web application that converts spoken audio into text using **FastAPI and Faster-Whisper**. It supports English, Hindi, and Hinglish (Hindi-English mixed speech), with automatic language detection and persistent transcription history.

## 🚀 Live Demo

- **Live Application:** https://realtime-speech-to-text-a8pc.onrender.com
- **GitHub Repository:** https://github.com/rishav44/realtime-speech-to-text

## ✨ Features

- **Real-Time Speech Recognition:** Capture microphone audio and transcribe it in chunks while recording.
- **Multilingual Support:** Supports Hindi, English, and mixed Hindi-English speech.
- **Automatic Language Detection:** Detects the spoken language using Faster-Whisper.
- **Open-Source ASR:** Uses the Faster-Whisper implementation of OpenAI Whisper.
- **Transcription History:** Stores previous transcriptions in a relational database.
- **CRUD Operations:** Create, view, edit, and delete saved transcriptions.
- **Interactive Dashboard:** Displays transcription history, detected language, and recording duration.
- **WebSocket Communication:** Streams audio between the browser and backend in real time.

## 🏗️ Architecture

```text
                 User / Browser
                       |
                       |
              Microphone Audio
                       |
                       v
              Frontend Application
                HTML / CSS / JS
                       |
                       |
              WebSocket Connection
                       |
                       v
                 FastAPI Backend
                       |
                       v
               Audio Processing
                 NumPy / 16 kHz
                       |
                       v
                Faster-Whisper
                 Tiny ASR Model
                       |
                       v
              Transcribed Text
                       |
                       v
                SQLAlchemy ORM
                       |
                       v
              Relational Database
                 SQLite / Neon
                       |
                       v
              Transcription Dashboard
```

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Speech Recognition | Faster-Whisper, Whisper |
| Audio Processing | NumPy |
| Real-Time Communication | WebSockets |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite, PostgreSQL (Neon) |
| ORM | SQLAlchemy |
| Deployment | Render |
| Version Control | Git, GitHub |

## 📂 Project Structure

```text
realtime-speech-to-text/
│
├── app/
│   ├── api/
│   │   ├── speech.py
│   │   └── transcription.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── database/
│   │   └── connection.py
│   │
│   ├── models/
│   │   └── transcription.py
│   │
│   ├── schemas/
│   │   └── transcription.py
│   │
│   ├── services/
│   │   └── speech_service.py
│   │
│   ├── static/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── script.js
│   │
│   └── main.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## ⚙️ Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/rishav44/realtime-speech-to-text.git

cd realtime-speech-to-text
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
WHISPER_MODEL=tiny
DEVICE=cpu
COMPUTE_TYPE=int8

# Optional: Configure PostgreSQL.
# If omitted, the application uses its configured SQLite default.
DATABASE_URL=
```

For PostgreSQL, provide a SQLAlchemy-compatible connection URL:

```env
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST/DATABASE
```

Keep database credentials private. Never commit `.env` to GitHub.

### 5. Run the application

```bash
uvicorn app.main:app --reload
```

Open:

http://127.0.0.1:8000

The Faster-Whisper model will be downloaded when required on its first initialization.

## 🔌 Application Interfaces

| Interface | Method | Purpose |
|---|---|---|
| `/` | GET | Web application |
| `/api/transcriptions/` | GET | Retrieve transcription history |
| `/api/transcriptions/` | POST | Save a transcription |
| `/api/transcriptions/{id}` | PUT | Update a transcription |
| `/api/transcriptions/{id}` | DELETE | Delete a transcription |
| `/ws/transcribe` | WebSocket | Stream audio and receive transcription results |

## 🎤 How It Works

1. The user grants microphone access through the browser.
2. Audio is captured and converted into mono, 16 kHz audio samples.
3. Audio samples are streamed to the backend using WebSockets.
4. FastAPI buffers incoming audio into manageable chunks.
5. Faster-Whisper processes each audio chunk and detects the spoken language.
6. The recognized text is returned to the browser.
7. Completed transcriptions can be saved and managed through the dashboard.
8. SQLAlchemy persists transcription records in the configured relational database.

## ☁️ Deployment

The application is deployed using Render.

- **Hosting:** Render
- **Database:** Neon PostgreSQL
- **ASR Model:** Faster-Whisper Tiny
- **Execution Device:** CPU
- **Compute Type:** INT8

### Render Configuration

**Build Command**

```bash
pip install -r requirements.txt
```

**Start Command**

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Configure the required environment variables in the Render dashboard.

## 🔮 Future Enhancements

- Improved recognition accuracy for Hindi-English code-switching.
- Speaker identification and diarization.
- Download transcriptions in TXT, PDF, and DOCX formats.
- User authentication and individual transcription histories.
- Improved streaming performance and asynchronous audio processing.
- Support for additional languages.
- Advanced analytics and transcription search.

## 👨‍💻 Author

**Rishav Raj**

GitHub: https://github.com/rishav44

---

*VoiceFlow AI demonstrates real-time audio streaming, multilingual automatic speech recognition, backend API development, relational database integration, and cloud deployment using open-source technologies.*