import speech_recognition as sr

r = sr.Recognizer()
def listen_and_recognize():
        with sr.Microphone() as source:
            print("Listening...")
            audio = r.listen(source,timeout=5)

        try:
            print("Recognizing...")
            text = r.recognize_google(audio)
            return "You said:", text
        except sr.UnknownValueError:
            print("Sorry, I could not understand your speech.")
        except sr.RequestError as e:
            print("Sorry, an error occurred. {0}".format(e))