
import speech_recognition as sr
from gtts import gTTS
import os
import time

def speech_to_text(audio_file_path):
    """
    Converts audio file to text using Google Speech Recognition.
    """
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file_path) as source:
            print(f"Reading audio file: {audio_file_path}")
            audio_data = recognizer.record(source)
            # Detect language automatically or default to English/Hindi
            # For accurate detection, we might need a two-pass approach or just use 'en-IN' as a broad catch-all for Indian context which often works for Hindi/English mix.
            # Let's try recognizing in 'hi-IN' which often captures both, or just 'en-US'.
            # A better approach for a "multilingual" bot is to try to recognize in a few key languages or just English if not specified.
            # For this smart bot, let's look for Hindi or English.
            try:
                # Try English first
                text = recognizer.recognize_google(audio_data, language='en-IN')
                return text, 'en'
            except sr.UnknownValueError:
                # If english fails, try Hindi
                try:
                    text = recognizer.recognize_google(audio_data, language='hi-IN')
                    return text, 'hi'
                except sr.UnknownValueError:
                    return None, None
            except sr.RequestError as e:
                print(f"Could not request results from Google SR service; {e}")
                return None, None

    except Exception as e:
        print(f"Error in speech_to_text: {e}")
        return None, None

def text_to_speech(text, lang='en'):
    """
    Converts text to speech using gTTS and saves it to a file.
    Returns the filename of the generated audio.
    """
    try:
        if not text:
            return None
        
        # Mapping common codes if needed, gTTS uses ISO 639-1
        tts = gTTS(text=text, lang=lang, slow=False)
        filename = f"response_{int(time.time())}.mp3"
        filepath = os.path.join('static', filename)
        tts.save(filepath)
        return filename
    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        return None
