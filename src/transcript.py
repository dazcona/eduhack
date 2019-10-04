import speech_recognition as sr

r = sr.Recognizer()

harvard = sr.AudioFile('/code/data/harvard.wav')
with harvard as source:
    audio = r.record(source)
out=r.recognize_google(audio)
print(out)