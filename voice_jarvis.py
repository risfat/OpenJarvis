"""Enhanced JARVIS-style Voice Assistant using OpenJarvis."""
import speech_recognition as sr
import pyttsx3
import requests
import threading
import time

JARVIS_API = "http://localhost:8000"
recognizer = sr.Recognizer()
engine = pyttsx3.init()

JARVIS_PERSONALITY = """You are JARVIS from Iron Man. Be helpful, slightly witty, and sophisticated. 
Keep responses concise as they will be spoken aloud."""

is_listening = False
wake_word = "jarvis"

def init_jarvis_voice():
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'david' in voice.name.lower() or 'mark' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

def speak(text):
    def _speak():
        print(f"JARVIS: {text}")
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=_speak, daemon=True).start()

def listen_for_wake_word():
    global is_listening
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        while True:
            try:
                print(f"Say '{wake_word}' to activate...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                query = recognizer.recognize_google(audio).lower()
                if wake_word in query:
                    speak("Yes, sir?")
                    return True
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception:
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
    except sr.UnknownValueError:
        speak("I didn't catch that, sir.")
        return None
    except sr.RequestError as e:
        speak(f"Speech service error: {e}")
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
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection error: {e}"

def continuous_mode():
    global is_listening
    speak("Continuous mode activated. Say 'stop' to exit.")
    
    while True:
        query = listen()
        if not query:
            continue
        if 'stop' in query.lower() or 'exit' in query.lower() or 'quit' in query.lower():
            speak("Continuous mode deactivated, sir.")
            break
        
        response = ask_jarvis(query)
        speak(response)

def single_mode():
    speak("Ready for your command, sir.")
    query = listen()
    if query:
        response = ask_jarvis(query)
        speak(response)

def main():
    init_jarvis_voice()
    
    speak("Initializing JARVIS systems. Online and ready.")
    print("\n" + "="*50)
    print("       J A R V I S  - Voice Assistant")
    print("="*50)
    print(f"Wake word: '{wake_word}'")
    print("Commands: 'continuous' for ongoing mode, 'single' for one command")
    print("="*50 + "\n")
    
    mode = input("Mode [single/continuous]: ").strip().lower()
    
    if mode == 'continuous':
        while True:
            if listen_for_wake_word():
                continuous_mode()
    else:
        if listen_for_wake_word():
            single_mode()

if __name__ == "__main__":
    main()