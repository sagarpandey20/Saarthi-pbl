
from flask import Flask, render_template, request, jsonify
import os
import time
from utils.audio_processing import speech_to_text, text_to_speech
from utils.chat_logic import get_bot_response

app = Flask(__name__)

# Ensure static folder exists for saving audio
if not os.path.exists('static'):
    os.makedirs('static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio_data' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio_data']
    
    # Save temporary file
    # We save as wav directly because we will configure frontend to send wav/webm
    # Note: SpeechRecognition prefers WAV.
    # If the browser sends WebM (Chrome default), we might need conversion if SR doesn't support it directly.
    # However, modern SR libraries often use ffmpeg under the hood or we can try to save as .wav if the blob is correct.
    # Save to file
    filename = f"temp_{int(time.time())}.wav"
    filepath = os.path.join('static', filename)
    audio_file.save(filepath)
    
    print(f"Received audio file: {filename}, Size: {os.path.getsize(filepath)} bytes")

    try:
        # 1. Speech to Text
        print("Attempting Speech Recognition...")
        user_text, detected_lang = speech_to_text(filepath)
        print(f"Speech Recognition Result: {user_text}, Lang: {detected_lang}")
        
        # Cleanup input file
        # os.remove(filepath) # Keep it for debugging for now

        if not user_text:
            print("Speech recognition returned empty text.")
            return jsonify({'error': 'Could not understand audio. Please try again.'}), 200

        # 2. Get Bot Response
        bot_reply = get_bot_response(user_text, detected_lang)

        # 3. Text to Speech
        audio_response_file = text_to_speech(bot_reply, detected_lang if detected_lang else 'en')

        return jsonify({
            'user_text': user_text,
            'bot_reply': bot_reply,
            'audio_url': f"/static/{audio_response_file}" if audio_response_file else None,
            'detected_lang': detected_lang
        })

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({'error': 'Internal server error processing audio'}), 500

if __name__ == '__main__':
    app.run(debug=True)
