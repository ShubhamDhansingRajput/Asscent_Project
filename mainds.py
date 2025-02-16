from flask import Flask, request, jsonify
import pyaudio
import wave
import speech_recognition as sr
from gtts import gTTS
import os

app = Flask(__name__)

def record_audio(filename, duration=30, sample_rate=16000):
    """Record audio from the microphone."""
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1

    p = pyaudio.PyAudio()
    stream = p.open(format=format,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk)

    print("Recording...")
    frames = []
    for _ in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    print("Recording finished.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_audio(filename):
    """Convert audio to text using Google Speech Recognition."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Google Speech Recognition could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

def text_to_speech(text, output_file="output.mp3"):
    """Convert text to speech with a US accent using gTTS."""
    tts = gTTS(text=text, lang='en', tld='us')
    tts.save(output_file)
    return output_file

def play_audio(filename):
    """Play the converted audio file."""
    os.system(f"start {filename}")  # For Windows, use `afplay` for macOS or `aplay` for Linux

@app.route('/indiatous', methods=['POST'])
def india_to_us():
    try:
        audio_file = "recorded_audio.wav"
        record_audio(audio_file, duration=30)
        
        transcribed_text = transcribe_audio(audio_file)
        if not transcribed_text or "could not understand" in transcribed_text:
            return jsonify({"error": "Failed to transcribe audio", "text": transcribed_text})
        
        output_audio = "converted_speech.mp3"
        text_to_speech(transcribed_text, output_audio)
        
        # play_audio(output_audio)
        
        return jsonify({"message": "Success", "transcribed_text": transcribed_text, "output_audio": output_audio})
    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/stop', methods=['POST'])
def stop_recording():
    global is_recording
    is_recording = False
    return jsonify({"message": "Recording stopped"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
