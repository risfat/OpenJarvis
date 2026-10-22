"""Voice chat with OpenJarvis using speech recognition and TTS."""
import speech_recognition as sr
import pyttsx3
import requests
import json

JARVIS_API = "http://localhost:8000"
recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio)
        print(f"You: {query}")
        return query
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Recognition error: {e}")
        return None

def ask_jarvis(prompt):
    try:
        response = requests.post(
            f"{JARVIS_API}/v1/chat/completions",
            json={
                "model": "qwen3:0.6b",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            },
            timeout=120
        )
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, I had trouble connecting to the assistant."

def main():
    engine.setProperty('rate', 150)
    engine.setProperty('voice', engine.getProperty('voices')[0].id)
    
    speak("Hello! I am ready. Ask me anything.")
    print("Say 'quit' to exit")
    
    while True:
        query = listen()
        if query is None:
            continue
        if query.lower() in ['quit', 'exit', 'stop']:
            speak("Goodbye!")
            break
        
        response = ask_jarvis(query)
        speak(response)

if __name__ == "__main__":
    main()