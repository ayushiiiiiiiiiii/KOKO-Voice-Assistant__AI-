import speech_recognition as sr
import webbrowser
import pyttsx3
import requests
import time
import datetime
import random
import pyjokes
import os
import urllib.parse
import re
import win32com.client

from dotenv import load_dotenv

load_dotenv()
GEMINI = os.getenv("GEMINI_KEY")
api = os.getenv("WEATHER_KEY")

apps = {
    'notepad': r'C:\Windows\System32\notepad.exe',
    'calculator': r'C:\Windows\System32\calc.exe',
    'cmd': r'C:\Windows\System32\cmd.exe',
    'paint': r'C:\Windows\System32\mspaint.exe',
    'word': r'C:\Program Files\Microsoft Office\Office16\WINWORD.EXE',
    'excel': r'C:\Program Files\Microsoft Office\Office16\EXCEL.EXE',
    'powerpoint': r'C:\Program Files\Microsoft Office\Office16\POWERPNT.EXE',
    'edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
}

office_executables = {
    "word": "WINWORD.EXE",
    "excel": "EXCEL.EXE",
    "powerpoint": "POWERPNT.EXE",
}


def find_app_path(name):
    app_path = apps.get(name)
    if not app_path:
        return name
    if name not in office_executables:
        return app_path

    executable = office_executables[name]
    candidates = [app_path]
    for root in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")):
        if root:
            candidates.extend((
                os.path.join(root, "Microsoft Office", "root", "Office16", executable),
                os.path.join(root, "Microsoft Office", "Office16", executable),
            ))

    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate

    raise FileNotFoundError(
        f"Could not find {name.title()}. Checked common Microsoft Office install locations."
    )


# ------------------- Robust Speech Synthesis (TTS) -------------------
speaker = None
try:
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    speaker.Volume = 100
    speaker.Rate = 1
    # Safely find a valid working voice without triggering broken default token errors
    try:
        cat = win32com.client.Dispatch("SAPI.SpObjectTokenCategory")
        cat.SetId(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices", False)
        tokens = cat.EnumerateTokens()
        for i in range(tokens.Count):
            token = tokens.Item(i)
            desc = token.GetDescription().lower()
            if "zira" in desc:
                speaker.Voice = token
                break
        else:
            if tokens.Count > 0:
                speaker.Voice = tokens.Item(0)
    except Exception:
        pass
except Exception:
    pass

engine = None
try:
    engine = pyttsx3.init()
    engine.setProperty('volume', 1.0)
    engine.setProperty('rate', 175)
except Exception:
    pass

r = sr.Recognizer()
gui_log_callback = None


def bol(text):
    if not text:
        return
    clean = re.sub(r'[*#_`]', '', text).strip()
    if gui_log_callback is not None:
        try:
            gui_log_callback(clean)
        except Exception:
            pass

    # 1. Try SAPI SpVoice
    if speaker is not None:
        try:
            speaker.Speak(clean)
            return
        except Exception:
            pass

    # 2. Try pyttsx3 engine
    if engine is not None:
        try:
            engine.say(clean)
            engine.runAndWait()
            return
        except Exception:
            pass

    # 3. Native Windows fallback via PowerShell System.Speech
    try:
        escaped = clean.replace("'", "''").replace('"', '`"')
        cmd = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{escaped}')"
        os.system(f'powershell -NoProfile -Command "{cmd}" >nul 2>&1')
    except Exception:
        pass


def gettime():
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%A, %B %d, %Y")
    message = f"Today is {date_str} and the time is {time_str}."
    print(message)
    bol(message)


def weather(city):
    if not api or api == "your_openweathermap_api_key_here":
        msg = "Weather API key is not configured in .env file"
        print(msg)
        bol("Weather API key is not configured")
        return

    url = f"http://api.openweathermap.org/data/2.5/weather?q={urllib.parse.quote(city)}&appid={api}&units=metric"
    try:
        response = requests.get(url, timeout=6)
        if response.status_code == 200:
            data = response.json()
            temp = round(data['main']['temp'])
            humidity = data['main']['humidity']
            description = data['weather'][0]['description']
            city_name = data.get('name', city.title())
            report = f"In {city_name}, it is currently {temp} degrees Celsius with {description}. Humidity is {humidity} percent."
            print(report)
            bol(report)
        else:
            bol(f"Sorry, could not find weather details for {city}")
            print(f"City '{city}' not found.")
    except Exception as e:
        print("Weather error:", e)
        bol("Sorry, I could not fetch the weather right now.")


def ai_response(prompt):
    if not GEMINI or GEMINI == "your_gemini_api_key_here":
        msg = "Gemini API key is not configured in .env file"
        print(msg)
        bol("Gemini API key is not configured")
        return

    # List of models to try (prioritizing fast, active 200 OK models)
    models_to_try = [
        "gemini-3-flash-preview",
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash",
        "gemma-4-26b-a4b-it",
    ]

    headers = {"Content-Type": "application/json"}
    voice_prompt = f"Answer concisely in 1 to 2 simple sentences suitable for speech: {prompt}"

    last_error_code = None
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI}"
        gen_config = {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
        }
        if "gemini" in model_name:
            gen_config["thinkingConfig"] = {"thinkingBudget": 0}

        data = {
            "contents": [{"parts": [{"text": voice_prompt}]}],
            "generationConfig": gen_config,
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=7)
            if response.status_code == 400 and "thinkingConfig" in gen_config:
                gen_config.pop("thinkingConfig", None)
                data["generationConfig"] = gen_config
                response = requests.post(url, headers=headers, json=data, timeout=7)

            if response.status_code == 200:
                candidates = response.json().get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    text = "".join(part.get("text", "") for part in parts)
                    if text:
                        clean_text = re.sub(r'[*#_`]', '', text).strip()
                        print(clean_text)
                        bol(clean_text)
                        return
            elif response.status_code in (503, 429):
                last_error_code = response.status_code
                print(f"Model {model_name} busy ({response.status_code}), trying next fallback...")
                continue
            else:
                last_error_code = response.status_code
                print(f"Model {model_name} returned status {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"Model {model_name} timed out, trying fallback...")
            continue
        except Exception as e:
            print(f"Error querying {model_name}:", e)
            continue

    if last_error_code in (503, 429):
        msg = "Google AI service is currently busy under high demand. Please ask again shortly."
    else:
        msg = "Sorry, I encountered an error connecting to AI."
    print(msg)
    bol(msg)


def numberguess():
    guess = 0
    num = random.randint(1, 100)
    bol("Welcome to the Number Guessing Game")
    bol("Please enter a number between 1 and 100")
    print("\n--- Number Guessing Game (Type 'exit' to quit) ---")
    while True:
        try:
            val = input("Guess a number (1-100): ").strip()
            if val.lower() in ['exit', 'quit', 'stop']:
                bol("Exiting game.")
                break
            n = int(val)
        except ValueError:
            print("Please enter a valid number!")
            continue

        guess += 1
        if n == num:
            bol(f"Congratulations! You guessed the correct number in {guess} attempts!")
            print(f"You Win! Guessed in {guess} attempts.\n")
            break
        elif n < num:
            bol("Guess higher")
            print("Higher! ⬆️")
        else:
            bol("Guess lower")
            print("Lower! ⬇️")


def RPS():
    options = ['rock', 'paper', 'scissor']
    bol("Welcome to Rock Paper Scissors")
    print("\n--- Rock Paper Scissors (Type 'q' to quit) ---")
    comp = 0
    you = 0
    tie = 0
    while True:
        try:
            user = input("Enter your choice (rock/paper/scissor) or 'q': ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            break

        if user in ['q', 'quit', 'exit']:
            break

        if user not in options:
            bol("Please enter rock, paper, or scissor only")
            print("Invalid choice! Choose rock, paper, or scissor.")
            continue

        com = random.choice(options)
        print(f"Computer picked: {com}")
        bol(f"My choice is {com}")

        if user == com:
            bol("It's a tie")
            tie += 1
        elif (user == 'rock' and com == 'scissor') or \
             (user == 'paper' and com == 'rock') or \
             (user == 'scissor' and com == 'paper'):
            bol("You win!")
            you += 1
        else:
            bol("You lose!")
            comp += 1

        print(f"Score - You: {you} | Computer: {comp} | Ties: {tie}\n")

    print(f"\nFinal Score - You: {you} | Computer: {comp} | Ties: {tie}")
    bol("Thanks for playing!")


def play_song(song_name):
    bol(f"Playing {song_name}")
    try:
        query = urllib.parse.quote(song_name)
        url = f"https://www.youtube.com/results?search_query={query}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=5)
        video_ids = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", response.text)
        if video_ids:
            first_video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
            print(f"Opening YouTube video: {first_video_url}")
            webbrowser.open(first_video_url)
            return
    except Exception as e:
        print("Could not fetch direct video URL:", e)

    query = urllib.parse.quote(song_name)
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")


def processcommand(c):
    c_clean = c.lower().strip()
    if "open google" in c_clean:
        webbrowser.open("https://www.google.com")
    elif "open facebook" in c_clean:
        webbrowser.open("https://www.facebook.com")
    elif "open youtube" in c_clean:
        webbrowser.open("https://www.youtube.com")
    elif "open instagram" in c_clean:
        webbrowser.open("https://www.instagram.com")
    elif "open gpt" in c_clean or "open chatgpt" in c_clean:
        webbrowser.open("https://chatgpt.com")
    elif c_clean.startswith("open "):
        name = c_clean.replace("open ", "").strip()
        if name in apps:
            try:
                os.startfile(find_app_path(name))
                bol(f"Opening {name}")
            except FileNotFoundError as e:
                print(e)
                bol(str(e))
        else:
            try:
                os.system(name)
            except Exception as e:
                bol(f"Sorry, I cannot open {name} right now.")

    elif any(p in c_clean for p in ['play number', "open number", "guess the number", "number guessing game"]):
        numberguess()
    elif c_clean.startswith("play "):
        song_name = c[5:].strip()
        play_song(song_name)
    elif c_clean == "play":
        bol("What song would you like to play?")

    elif any(p in c_clean for p in ["weather", "mausam", "weather report", "climate", "temperature"]):
        # Extract city if already in command, e.g. "weather in Delhi", "temperature of Mumbai"
        match = re.search(r"(?:weather|mausam|temperature|climate)\s+(?:in|of|for|at)?\s*([a-zA-Z\s]+)", c, re.IGNORECASE)
        city = None
        if match:
            city = match.group(1).strip()
        else:
            match_rev = re.search(r"([a-zA-Z\s]+)\s+(?:weather|mausam)", c, re.IGNORECASE)
            if match_rev:
                city = match_rev.group(1).strip()

        if city and city.lower() not in ["report", "now", "today", "forecast", "please", ""]:
            weather(city)
        else:
            bol("Which city would you like the weather for?")
            city_name = ""
            try:
                with sr.Microphone() as src:
                    print("Listening for city name (speak now, or type below)...")
                    audio = r.listen(src, timeout=4, phrase_time_limit=4)
                    city_name = r.recognize_google(audio, language='en-US').strip()
                    print(f"Heard city: {city_name}")
            except Exception:
                pass
            if not city_name:
                try:
                    city_name = input("City Name: ").strip()
                except Exception:
                    pass
            if city_name:
                weather(city_name)

    elif any(p in c_clean for p in [
        "what time", "tell me the time", "current time", "time now",
        "what's the time", "what is the time", "show time",
        "what date", "tell me the date", "tell me the date and time",
        "today's date", "current date"
    ]):
        gettime()

    elif any(p in c_clean for p in ['rps', "rock paper scissor", "rockpaperscissor", "rock", "paper", "scissor"]):
        RPS()

    elif any(p in c_clean for p in ["tell me a joke", "joke", "i want a joke", "funny", "jokes"]):
        joke = pyjokes.get_joke()
        print(f"The Joke is: {joke}")
        bol(f"The Joke is: {joke}")

    else:
        ai_response(c)


if __name__ == '__main__':
    username = input("Enter Your Name: ").strip() or "User"
    bol("Koko is Activating")

    with sr.Microphone() as mic:
        print("\n[Adjusting for ambient noise... Please stay quiet for 1 second]")
        r.adjust_for_ambient_noise(mic, duration=1)
        r.dynamic_energy_threshold = True
        print("[Microphone ready!]\n")

        while True:
            try:
                print("Please Say 'Koko'...")
                aud = r.listen(mic, timeout=5, phrase_time_limit=4)
                word = r.recognize_google(aud, language='en-US')
                print(f"Heard: '{word}'")

                wake_words = ['koko', 'coco', 'cocoa', 'ko ko', 'co co', 'coko', 'koco', 'cuckoo', 'kukoo', 'kuku', 'kookoo', 'cookoo', 'cucko']
                if any(w in word.lower() for w in wake_words):
                    print("Koko is Activated!")
                    greeting = f"Hello {username}! How can I help you today?"
                    print(greeting)
                    bol(f"Koko is Activated. Hello {username}, how can I help you today?")
                    break
                else:
                    print("Did not hear 'Koko'. Please try again.")
            except sr.UnknownValueError:
                print("Sorry, could not recognize audio. Please speak again.")
                continue
            except sr.WaitTimeoutError:
                print("Listening timed out. Please speak again.")
                continue
            except sr.RequestError as e:
                print(f"Google Speech Recognition service error: {e}")
                time.sleep(1)
            except Exception as e:
                print("Error:", e)
                time.sleep(1)

        while True:
            try:
                print("\nListening for command.....")
                audi = r.listen(mic, timeout=5, phrase_time_limit=6)
                print("Recognizing....")
                command = r.recognize_google(audi, language='en-US')
                print(f"You Said: {command}")
                cmd_clean = command.lower().strip()
                stop_words = ['cancel', 'exit', 'stop', 'goodbye', 'good bye', 'quit', 'bye', 'bye bye', 'koko stop', 'stop koko', 'please stop']
                if cmd_clean in stop_words or any(cmd_clean == w for w in ['stop', 'exit', 'quit', 'bye']):
                    farewell = f"Thank you, Goodbye {username}!"
                    bol(farewell)
                    print(farewell)
                    break
                processcommand(command)
            except sr.UnknownValueError:
                print("Please repeat your command.")
                continue
            except sr.WaitTimeoutError:
                continue
            except sr.RequestError as e:
                print(f"Speech recognition service error: {e}")
                time.sleep(1)
            except Exception as e:
                print("Unexpected error while listening for command:", e)
                time.sleep(1)
