import os
import threading
from flask import Flask, request, jsonify
import google.generativeai as genai
import pyttsx3
from dotenv import load_dotenv
from flask import render_template

app = Flask(__name__)
load_dotenv()
# Fetch your Gemini API key from the environment
API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")
if not API_KEY:
    raise ValueError("Missing Google Generative AI API key. Set GOOGLE_GENAI_API_KEY in your environment.")
genai.configure(api_key=API_KEY)

# Initialize a global TTS engine instance
tts_engine = pyttsx3.init()
voices = tts_engine.getProperty('voices')

def set_voice(language):
    """
    Set the TTS engine voice based on language.
    Adjust voice selection logic as needed for your OS.
    """
    selected_voice = None
    for voice in voices:
        if language == "hi" and ("hindi" in voice.name.lower() or "hin" in voice.id.lower()):
            selected_voice = voice
            break
        elif language == "en" and ("english" in voice.name.lower() or "en" in voice.id.lower()):
            selected_voice = voice
            break
    if selected_voice:
        tts_engine.setProperty('voice', selected_voice.id)
    else:
        # Use default voice if no match is found.
        pass

def text_to_speech(text, language):
    """
    Convert text to speech in a separate thread.
    """
    set_voice(language)
    def speak():
        tts_engine.say(text)
        tts_engine.runAndWait()
    threading.Thread(target=speak).start()

def get_gemini_response(user_text):
    """
    Use Google Gemini to generate a response.
    """
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(user_text)
        if response and response.text:
            return response.text.strip()
        else:
            return "Sorry, I couldn't generate a response."
    except Exception as e:
        return f"Error: {e}"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_text = data.get("text")
    language = data.get("language", "en")
    response_text = get_gemini_response(user_text)
    # Speak response in a non-blocking thread
    text_to_speech(response_text, language)
    return jsonify({"response": response_text})

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
