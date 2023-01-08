import speech_recognition as sr
import pyttsx3


def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        response = ''
        audio_text = recognizer.listen(source, timeout=5.0)
        try:
            response = recognizer.recognize_google(audio_text)
        except:
            text_to_speech("Sorry, I did not get that")
        return response

