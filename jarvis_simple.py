"""Simple JARVIS Voice Assistant."""
import speech_recognition as sr
import requests
import pyttsx3

JARVIS_API = "http://localhost:8000"
wake_word = "jarvis"

JARVIS_PERSONALITY = """You are JARVIS from Iron Man. Be helpful, sophisticated, witty.
Keep responses short. Address user as 'sir'."""

recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)

def speak(text):
    print(f"JARVIS: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=8)
    return recognizer.recognize_google(audio)

def ask_jarvis(prompt):
    resp = requests.post(
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
    return resp.json()["choices"][0]["message"]["content"]

print("="*40)
print("   J A R V I S")
print("="*40)

speak("Systems online.")

while True:
    print(f"Say '{wake_word}'...")
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            query = recognizer.recognize_google(audio).lower()
            if wake_word in query:
                speak("Yes, sir?")
                
                query = listen()
                response = ask_jarvis(query)
                speak(response)
        except:
            pass