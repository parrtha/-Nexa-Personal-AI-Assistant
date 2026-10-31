# Nexa — Personal AI Voice Assistant

Nexa is a local AI-powered, voice-controlled personal assistant for Windows. It combines AI conversations, speech recognition, multilingual responses, text-to-speech, and desktop automation in a React-based interface with a Python FastAPI backend.

## Features

### 1. Voice Interaction
- Interact with Nexa using your microphone.
- Speech recognition for English and Kannada.
- English and Kannada AI responses.
- English and Kannada text-to-speech support.

### 2. Wake-Word Activation
- Activate the assistant using the wake phrase **"Hey Nexa"**.
- English wake-word detection.

### 3. AI-Powered Conversations
- Local AI inference using Qwen3 through Ollama.
- Private, locally processed AI conversations.
- Chat history with saved conversations.
- Reopen and delete saved conversations.

### 4. Desktop Automation
Open supported Windows applications and locations:
- Google Chrome
- Visual Studio Code
- Calculator
- Downloads
- Windows Settings
- Task Manager

### 5. Desktop Tools
- **System Monitor:** View CPU, RAM, disk, battery, and operating system information.
- **File Search:** Search for files and open supported search results.
- **Reminders:** Create, view, complete, undo, refresh, and delete reminders.
- **Chat History:** Save and reopen previous conversations.

### 6. Web Search
- Search Google.
- Search YouTube.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI |
| AI Model | Qwen3 via Ollama |
| Speech Recognition | Browser Speech Recognition API |
| English Text-to-Speech | Web Speech API |
| Kannada Text-to-Speech | Sarvam AI |
| System Monitoring | psutil |
| API Communication | HTTP |
| Styling | CSS |

## Requirements

- Windows 10 or Windows 11
- Node.js and npm
- Python 3.11
- Ollama
- Qwen3 model used by the project
- Sarvam AI API key for Kannada text-to-speech

## Installation and Setup

### 1. Clone or Download the Project

Open a terminal in the project directory.

### 2. Install Frontend Dependencies

From the project root:

```bash
npm install
```

### 3. Configure Backend Dependencies

Open a terminal in the `backend` directory.

If `requirements.txt` exists, install the dependencies:

```bash
py -3.11 -m pip install -r requirements.txt
```

If the project does not contain `requirements.txt`, install the dependencies listed in its backend imports and project configuration.

### 4. Configure Environment Variables

Create or update the backend `.env` file with the Sarvam AI API key if Kannada TTS is enabled.

**Important:** Never publish API keys, passwords, or `.env` files in a public repository.

### 5. Start Ollama

Make sure Ollama is installed and running.

Check the installed models:

```bash
ollama list
```

If the project uses `qwen3:1.7b`, download it using:

```bash
ollama pull qwen3:1.7b
```

### 6. Start the Backend

Open a terminal in the `backend` directory:

```bash
py -3.11 -m uvicorn main:app --host 127.0.0.1 --port 8010 --reload
```

Backend API:

```text
http://127.0.0.1:8010
```

FastAPI Swagger documentation:

```text
http://127.0.0.1:8010/docs
```

### 7. Start the Frontend

Open another terminal in the project root:

```bash
npm run dev
```

Open the Vite development URL:

```text
http://localhost:5173
```

## Testing and Project Status

Nexa's main features have been tested locally.

| Feature | Testing Status |
|---|---|
| Frontend and backend | Tested |
| Local AI with Ollama | Tested |
| English voice interaction | Tested |
| Kannada voice interaction | Tested |
| English and Kannada TTS | Tested |
| Hey Nexa wake word | Tested |
| Windows application commands | Tested |
| Google and YouTube search | Tested |
| System Monitor | Tested |
| File Search | Tested |
| Reminders CRUD operations | Tested |
| Chat History and reopening conversations | Tested |

Nexa currently runs locally through its React frontend, FastAPI backend, and Ollama service.

**Note:** Kannada text-to-speech requires a valid Sarvam AI API key. The application is designed for local use and is not packaged as a Windows installer.

## Security

- Keep API keys and secrets in environment variables.
- Do not commit `.env` files.
- Keep the backend bound to localhost when using it as a personal desktop assistant.
- Review command execution and file access permissions before exposing the backend externally.

## Author

**Partha R**
**Lava S V**
Personal AI Voice Assistant Project

Built using React, FastAPI, Python, Ollama, Qwen3, and speech technologies.