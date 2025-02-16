import os
import wave
import flask
from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse
from google.cloud import texttospeech
import sounddevice as sd
import numpy as np

try:
    import openai
    openai_available = True
except ModuleNotFoundError:
    openai_available = False

# Initialize Flask App
app = Flask(__name__)

# OpenAI API Key (Check if OpenAI module is available)
if openai_available:
    openai.api_key = "your_openai_api_key"

# Google Cloud TTS Client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "your_google_credentials.json"
tts_client = texttospeech.TextToSpeechClient()

# Route for Twilio Call Handling
@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    response.say("This call is being processed for accent conversion.")
    response.stream(url="wss://yourserver.com/audio-stream")  # WebSocket for live audio
    return str(response)

# Speech-to-Text Function (Whisper API, if available)
def speech_to_text(audio_file):
    if not openai_available:
        return "OpenAI module not found. Speech-to-text functionality is unavailable."
    
    with open(audio_file, "rb") as audio:
        transcript = openai.Audio.transcribe("whisper-1", audio)
    return transcript["text"]

# Text-to-Speech Function (Google TTS)
def text_to_speech(text):
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)
    response = tts_client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    with open("output.wav", "wb") as out:
        out.write(response.audio_content)
    return "output.wav"

# API Endpoint to Process Audio
@app.route("/process_audio", methods=["POST"])
def process_audio():
    audio_file = request.files["file"]
    audio_path = "input.wav"
    audio_file.save(audio_path)
    
    text = speech_to_text(audio_path)
    if text.startswith("OpenAI module not found"):
        return jsonify({"error": text})
    
    output_audio = text_to_speech(text)
    return jsonify({"text": text, "audio_file": output_audio})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
