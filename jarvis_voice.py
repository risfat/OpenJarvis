"""Enhanced JARVIS Voice Assistant with better TTS."""
import speech_recognition as sr
import requests
import threading
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

JARVIS_API = "http://localhost:8000"
wake_word = "jarvis"

JARVIS_PERSONALITY = """You are JARVIS from Iron Man. Be helpful, sophisticated, slightly witty.
Keep responses concise as they will be spoken. Address the user as 'sir'."""

recognizer = sr.Recognizer()

def get_tts_engine():
    try:
        from kokoro import KPipeline
        return KPipeline(lang_code="en")
    except ImportError:
        return None

def speak(text, pipeline=None):
    print(f"JARVIS: {text}")
    
    if pipeline:
        try:
            import numpy as np
            import soundfile as sf
            import io
            import subprocess
            
            samples = []
            for _, _, audio in pipeline(text, voice="af_heart", speed=1.0):
                samples.append(audio)
            
            if samples:
                combined = np.concatenate(samples)
                temp_wav = "temp_jarvis.wav"
                sf.write(temp_wav, combined, 24000)
                
                subprocess.run([
                    'powershell', '-Command', 
                    f'(New-Object System.Media.SoundPlayer "{temp_wav}").PlaySync(); Remove-Item "{temp_wav}"'
                ], check=False)
        except Exception as e:
            print(f"Kokoro failed: {e}, using pyttsx3")
            speak_pyttsx3(text)
    else:
        speak_pyttsx3(text)

def speak_pyttsx3(text):
    import pyttsx3
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    for voice in engine.getProperty('voices'):
        if 'david' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    engine.say(text)
    engine.runAndWait()

def listen_for_wake():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print(f"Say '{wake_word}' to activate...")
        while True:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                query = recognizer.recognize_google(audio).lower()
                if wake_word in query:
                    return True
            except:
                continue

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
    try:
        query = recognizer.recognize_google(audio)
        print(f"You: {query}")
        return query
    except:
        return None

def ask_jarvis(prompt):
    try:
        response = requests.post(
            f"{JARVIS_API}/v1/chat/completions",
            json={
                "model": "qwen3:0.6b",
                "messages": [
                    {"role": "system", "content": JARVIS_PERSONALITY},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            },
            timeout=120
        )
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

def main():
    print("="*50)
    print("    J A R V I S  - Voice Assistant")
    print("="*50)
    
    pipeline = get_tts_engine()
    if pipeline:
        print("Using Kokoro TTS (high quality)")
    else:
        print("Using pyttsx3 TTS")
    
    speak("Initializing. Systems online.", pipeline)
    speak(f"Say {wake_word} to begin.", pipeline)
    
    while True:
        if listen_for_wake():
            speak("Yes, sir?", pipeline)
            
            while True:
                query = listen()
                if not query:
                    continue
                if any(w in query.lower() for w in ['stop', 'exit', 'goodbye', 'sleep']):
                    speak("Standing by.", pipeline)
                    break
                
                response = ask_jarvis(query)
                speak(response, pipeline)

if __name__ == "__main__":
    main()