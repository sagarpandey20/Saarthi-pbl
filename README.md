# AI Based Multilingual Voice Communication System

This is a complete Telecom IVR replacement system that uses AI to understand and reply to user voice queries in multiple languages.

## Features
- **Voice-to-Voice Communication**: Speak to the bot, and it replies with voice.
- **Multilingual Support**: Works with English, Hindi, and other languages (auto-detected).
- **Telecom Domain Logic**: Handles queries like "Balance", "Recharge", "Plans".
- **Modern UI**: Clean and responsive web interface.
- **No Complex Setup**: Records standard WAV audio directly in the browser to ensure compatibility.

## Prerequisites
- Python 3.7+
- Internet Connection (for Google Speech API and Translation)

## Installation

1. **Install Dependencies**:
   Open a terminal in this folder and run:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: This installs Flask, SpeechRecognition, gTTS, and deep-translator.*

2. **Run the Application**:
   ```bash
   python app.py
   ```

3. **Open in Browser**:
   Go to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## How to Use
1. Click the **"Tap to Speak"** button.
2. Allow microphone access when prompted.
3. Speak your query. Examples:
   - *English*: "What is my data balance?"
   - *Hindi*: "Mera recharge kab khatam hoga?"
   - *English*: "I want to talk to customer support."
4. The bot will listen, process your request, and reply with both text and audio.

## Project Structure
- `app.py`: Main Flask server.
- `requirements.txt`: List of Python libraries.
- `static/`: Contains CSS, JavaScript, and generated audio files.
- `templates/`: Contains the HTML interface.
- `utils/`:
  - `audio_processing.py`: Handles Speech-to-Text and Text-to-Speech.
  - `chat_logic.py`: Handles translation and response generation.

## Troubleshooting
- **Microphone Error**: Ensure your browser has permission to access the microphone. Works best in Chrome/Edge/Firefox.
- **Audio not playing**: Check your speaker volume.
- **Slow Response**: The system relies on online APIs (Google), so speed depends on your internet connection.

