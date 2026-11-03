import win32com.client
import os

print("--- Testing Windows SAPI Voices ---")
try:
    cat = win32com.client.Dispatch("SAPI.SpObjectTokenCategory")
    cat.SetId(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices", False)
    tokens = cat.EnumerateTokens()
    print(f"Total SAPI voices found: {tokens.Count}")
    for i in range(tokens.Count):
        token = tokens.Item(i)
        print(f"  [{i}] {token.GetDescription()} (ID: {token.Id})")

    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    if tokens.Count > 0:
        speaker.Voice = tokens.Item(0)
    print(f"Using voice: {speaker.Voice.GetDescription()}")
    speaker.Speak("Testing one two three. Can you hear me?")
    print("SAPI test completed successfully.")
except Exception as e:
    print(f"SAPI test error: {e}")

print("\n--- Testing pyttsx3 (if supported) ---")
try:
    import pyttsx3
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print(f"Voice: {voice.name} - ID: {voice.id}")
    engine.say("Testing pyttsx3. Voice is working!")
    engine.runAndWait()
    print("pyttsx3 test completed successfully.")
except Exception as e:
    print(f"pyttsx3 is not available on this system configuration ({e}). Using native SAPI.")
