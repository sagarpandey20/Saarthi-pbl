
from deep_translator import GoogleTranslator

def detect_and_translate(text, target_lang='en'):
    """
    Detects the language of the input text and translates it to the target language.
    Returns (translated_text, source_language_code)
    """
    if not text:
        return "", "en"
    
    try:
        # deep_translator doesn't have a dedicated detect method in the same way, 
        # but we can try to translate to english.
        # For simplicity in this project, we will assume input is Hindi if it contains devanagari script, else English.
        # Or we can just always translate to english with 'auto' source.
        
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated = translator.translate(text)
        
        # Heuristic for detection since deep_translator simplified API doesn't always return source lang
        # We will assume 'hi' if the original text differs significantly or contains specific chars.
        # For this bot, let's just return 'auto' as detected if we rely on the logic.
        
        return translated, 'auto'
    except Exception as e:
        print(f"Translation Error: {e}")
        return text, 'en'

def get_bot_response(user_text, src_lang='en'):
    """
    Determines the bot's response based on the user's text.
    """
    
    # 1. Translate to English for processing
    text_en = user_text
    detected_source = 'en'
    
    # Simple heuristic to detect Hindi: look for Devanagari range unicode
    # This is more robust than relying on unstable detection APIs
    for char in user_text:
        if '\u0900' <= char <= '\u097f':
            detected_source = 'hi'
            break
            
    if detected_source == 'hi':
        try:
            text_en = GoogleTranslator(source='hi', target='en').translate(user_text)
        except:
            pass
            
    text_en_lower = text_en.lower()
    response_en = ""

    # 2. Logic / Intent Recognition (Rule-based for telecom)
    if "balance" in text_en_lower or "data" in text_en_lower:
        response_en = "Your current data balance is 1.5 GB and talktime is 50 Rupees."
    elif "recharge" in text_en_lower or "top up" in text_en_lower:
        response_en = "To recharge, please visit our website or say '199 plan' to activate the monthly pack."
    elif "plan" in text_en_lower or "offer" in text_en_lower:
        response_en = "The best offer for you is the 199 Rupees unlimited plan for 28 days."
    elif "hello" in text_en_lower or "hi" in text_en_lower:
        response_en = "Hello! Welcome to Telecom AI Support. How can I help you today?"
    elif "support" in text_en_lower or "help" in text_en_lower or "agent" in text_en_lower:
        response_en = "I am connecting you to a customer care executive. Please stay on the line."
    elif "thank" in text_en_lower:
        response_en = "You're welcome! Have a great day."
    else:
        response_en = "I'm sorry, I didn't understand that. You can ask about balance, recharge, or plans."

    # 3. Translate response back to source language
    response_final = response_en
    if detected_source == 'hi':
        try:
            response_final = GoogleTranslator(source='en', target='hi').translate(response_en)
        except Exception as e:
            print(f"Back translation error: {e}")
            
    return response_final
