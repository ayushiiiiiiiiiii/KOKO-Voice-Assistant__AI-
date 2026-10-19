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
import os

load_dotenv()
GEMINI = os.getenv("GEMINI_KEY")
api = os.getenv("WEATHER_KEY")

apps={
    'notepad':'C:\\Windows\\System32\\notepad.exe',
    'calculator':'C:\\Windows\\System32\\calc.exe',
    'cmd':'C:\\Windows\\System32\\cmd.exe',
    'paint':'C:\\Windows\\System32\\mspaint.exe',
    'word':r'C:\Program Files\Microsoft Office\Office16\WINWORD.EXE',
    'excel':r'C:\Program Files\Microsoft Office\Office16\EXCEL.EXE',
    'powerpoint':r'C:\Program Files\Microsoft Office\Office16\POWERPNT.EXE',
    'edge':r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
}


speaker = None
try:
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    speaker.Volume = 100
    speaker.Rate = 1
    for v in speaker.GetVoices():
        if "zira" in v.GetDescription().lower():
            speaker.Voice = v
            break
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
    clean = text.replace("*", "").replace("#", "").replace("_", "").strip()
    if gui_log_callback is not None:
        try:
            gui_log_callback(clean)
        except Exception:
            pass
    if speaker is not None:
        try:
            speaker.Speak(clean)
            return
        except Exception:
            pass
    if engine is not None:
        try:
            engine.say(clean)
            engine.runAndWait()
        except Exception:
            pass
    
def gettime():
    now = datetime.datetime.now()
    time = now.strftime("%I:%M %p")
    date = now.strftime("%A, %B %d, %Y")
    bol(f"Today is {date} and the time is {time}.")
    print(f"Today is {date} and the time is {time}.")
    
    

def weather(city):
    if not api or api == "your_openweathermap_api_key_here":
        msg = "Weather API key is not configured in .env file"
        print(msg)
        bol("Weather API key is not configured")
        return
        
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}&units=metric"
    response=requests.get(url)
    if response.status_code==200:
        data=response.json()
        temp=data['main']['temp']
        humidity=data['main']['humidity']
        description=data['weather'][0]['description']
        bol(f"City: {data['name']}")
        bol(f"Temperature: {temp} C")
        print(f"Temperature: {temp} C")
        
        bol(f"Humidity: {humidity} %")
        print(f"Humidity: {humidity} %")
        bol(f"Weather: {description.capitalize()}")
        print(f"Weather: {description.capitalize()}")
    else:
        bol("City Not found")
        print("City Not found")
    

def ai_response(prompt):
    if not GEMINI or GEMINI == "your_gemini_api_key_here":
        msg = "Gemini API key is not configured in .env file"
        print(msg)
        bol("Gemini API key is not configured")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI}"

    headers = {"Content-Type": "application/json"}
    voice_prompt = f"Answer concisely in 1 to 2 simple sentences suitable for speech: {prompt}"
    data = {
        "contents": [{"parts": [{"text": voice_prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 300,
            "thinkingConfig": {
                "thinkingBudget": 0
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            candidates = response.json().get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                text = ""
                for part in parts:
                    if "text" in part:
                        text += part["text"]
                if text:
                    clean_text = text.replace("*", "").replace("#", "").strip()
                    print(clean_text)
                    bol(clean_text)
                    return
            print("Sorry, I could not generate an answer.")
            bol("Sorry, I could not generate an answer.")
        else:
            print("Error:", response.text)
            bol("Sorry, I encountered an error connecting to AI.")
    except Exception as e:
        print("AI connection error:", e)
        bol("Sorry, something went wrong while connecting to AI.")


    
def numberguess():
    guess=0
    num=random.randint(1,101)
    bol("Welcome to the NUmber Guessing Game")
    bol("Please Enter Number between 1 and 100")
    while 1:
        guess+=1
        n=int(input("N:"))
        if(n==num):
            bol("You Guess teh Correct number")
            print("You Win")
            break
        elif n<num:
            bol("Guess Higher")
        elif n>num:
            bol("Guuess Lower\n")
    print(f"\nYou guess in the {guess} guesses ")
    bol(f"You guess in the {guess} guesses ")
    
    
    
def RPS():
    options=['rock','paper','scissor']
    bol("Welcome to the Rock paper scissor game") 
    choice='y'
    comp=0
    you=0
    tie=0
    while choice =='y':
        user=input("Enter your Choice ")
        
        if user.lower() not in options:
            bol("Please type the rock ,paper ,scissor only!")
            continue
        user=user.lower()
        r=random.randint(0,2)
        com=options[r]
    
        print(f"Computer picked: {com}")
        bol(f"My Choice is {com}")
    
        if user==com:
            bol("Its Tie")
            tie=tie+1
        elif user=='rock' and com=='scissor':
            bol("You WIn!")
            you=you+1
        elif user =='paper' and com=='rock':
            bol("You win!")
            you=you+1
        elif user=='scissor' and com=='paper':
            bol("You win !")
            you=you+1
        else:
            bol("You Lose! ")
            comp=comp+1
        bol("Press y if you play again otherwise press n")
        choice=input('(y/n):')
    
    print("\nYour score is : ",you)
    print("\nComputer score is : ",comp)
    print("\n Draw score is : ",tie)
    bol("\nTHanks For PLaying")
    
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
    if "open google" in c.lower():
        webbrowser.open("https://www.google.com")
    elif "open facebook" in c.lower():
        webbrowser.open("https://www.facebook.com")
    elif "open youtube" in c.lower():
        webbrowser.open("https://www.youtube.com")
    elif "open instagram" in c.lower():
        webbrowser.open("https://www.instagram.com")
    elif "open gpt" in c.lower():
        webbrowser.open("https://chatgpt.com")
    elif c.lower().startswith("open "):
        name = c.lower().replace("open ", "").strip()
        if name in apps:
            os.startfile(apps[name])
            bol(f"Opening {name}")
        else:
            try:
                os.system(name)
            except Exception as e:
                bol(f"Sorry, I cannot  open {name} right now.")
            
    elif any(p in c for p in ['play number',"Open Number","guess the number","number guessing game","guess the number","number"]):
        numberguess()
    elif c.lower().startswith("play "):
        song_name = c[5:].strip()
        play_song(song_name)
    elif c.lower().strip() == "play":
        bol("What song would you like to play?")
        
    elif any(p in c for p  in ["weather","mausam","weather report","climate","temperature"]):
        bol("Please Enter the City Name")
        city=input("City Name:")
        weather(city)
    
    elif any(p in c for p in["what time", "tell me the time", "current time", "time now",
        "what's the time", "what is the time", "show time",
        "what date", "tell me the date","tell me the date and time", "today's date", "current date"] ):
        gettime()
    elif any(p in c for p in ['RPS',"rock paper scissor","rockpaperscissor","rock","paper","scissor"]):
        RPS()
        
    elif any(p in c for p in ["tell me a joke","joke","I want a joke","funny","jokes"]):
        joke=pyjokes.get_joke()
        print(f"The Joke is {joke}")
        bol(f"The Joke is {joke}")
    else:
        ai_response(c)
        
        
    
if __name__=='__main__':
    username=input("Enter Your Name: ")
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
                    print(f"Hello {username}! How can I help you today?")
                    bol(f"Koko is Activated. Hello {username}, how can I help you today?")
                    break
                else:
                    print(f"Did not hear 'Koko'. Please try again.")
            except sr.UnknownValueError:
                print("Sorry, could not recognize audio. Please speak again.")
                continue
            except sr.WaitTimeoutError:
                print("Listening timed out. Please speak again.")
                continue
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
                    bol("Thank you, Goodbye Ayushi")
                    print("Thank you! Goodbye!")
                    break 
                processcommand(command)
            except sr.UnknownValueError:
                print("Please repeat your command.")
                continue
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print("Unexpected error while listening for command:", e)
                time.sleep(1)
                        

            
            
            
        
        
    
    
        
