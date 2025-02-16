import pyaudio
import wave
import speech_recognition as sr
from gtts import gTTS
import os

# Step 1: Capture Real-Time Voice
def record_audio(filename, duration=30, sample_rate=16000):  # Default duration set to 30 seconds
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

    # Save the recorded audio to a file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

# Step 2: Transcribe Audio to Text
def transcribe_audio(filename):
    """Convert audio to text using Google Speech Recognition."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        print("Transcribed Text: ", text)
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

# Step 3: Convert Text to US Accent Speech
def text_to_speech(text, output_file="output.mp3"):
    """Convert text to speech with a US accent using gTTS."""
    tts = gTTS(text=text, lang='en', tld='us')  # Use 'us' for US accent
    tts.save(output_file)
    print(f"Speech saved to {output_file}")

# Step 4: Play the Converted Audio
def play_audio(filename):
    """Play the converted audio file."""
    os.system(f"start {filename}")  # For Windows
    # Use `afplay` for macOS or `aplay` for Linux

# Main Function
def main():
    # Step 1: Record audio
    audio_file = "recorded_audio.wav"
    record_audio(audio_file, duration=30)  # Record for 30 seconds

    # Step 2: Transcribe audio
    text = transcribe_audio(audio_file)
    if not text:
        return

    # Step 3: Convert text to US accent speech
    output_audio = "converted_speech.mp3"
    text_to_speech(text, output_audio)

    # Step 4: Play the converted audio
    play_audio(output_audio)

if __name__ == "__main__":
    main()