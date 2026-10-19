import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    print(f"Voice: {voice.name} - ID: {voice.id}")  # check available voices
engine.say("Testing one two three. Can you hear me?")
engine.runAndWait()
