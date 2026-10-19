<div align="center">

# 🎙️ KOKO — AI Voice Assistant

A Python voice assistant that listens, talks, opens apps, checks weather, plays music directly on YouTube, tells jokes, plays games, and uses **Google Gemini AI** to answer anything else.

</div>

---

## 📖 Table of Contents

1. [What is Koko?](#-what-is-koko)
2. [Features](#-features)
3. [How It Works](#️-how-it-works)
4. [Gemini AI Integration](#-gemini-ai-integration)
5. [Setup Guide](#️-setup-guide)
6. [Example Commands](#️-example-commands)
7. [Project Structure](#-project-structure)
8. [Troubleshooting](#-troubleshooting)
9. [Notes](#️-notes)

---

## 🤖 What is Koko?

Koko is a voice-controlled AI assistant you can talk to on your Windows PC. You say the wake word **"Koko"**, it wakes up, and then you speak your commands naturally — like "open YouTube", "play Believer", or "what's the weather in Delhi." 

If it doesn't recognize a built-in command, it automatically forwards your question to **Google Gemini AI**, so you can ask open questions, explanations, and advice and get spoken answers out loud.

Think of it as a friendly AI assistant living inside your PC 🖥️🤖 — listening, thinking, and talking back to you.

---

## ✨ Features

| 🧩 Feature | 📋 Description |
|---|---|
| 🎤 Wake Word | Activates when it hears "Koko" (and phonetic variations like "Kukoo", "Coco") |
| 🗣️ Voice Replies | Speaks every response out loud using Windows Native Speech Synthesis (SAPI) |
| 🎵 Direct Music Playback | Scrapes YouTube and plays the exact song video directly in your browser |
| 🤖 Gemini AI Integration | Unrecognized questions are answered intelligently by Google Gemini 3.8 Flash |
| 🌐 Open Websites | Google, YouTube, Instagram, Facebook, ChatGPT |
| 💻 Open Desktop Apps | Notepad, Calculator, CMD, Paint, Microsoft Office (Word, Excel, PPT), Edge |
| ☁️ Live Weather | Live temperature, humidity & weather conditions for any city via OpenWeatherMap |
| 🕒 Time & Date | Speaks current date and time |
| 😂 Jokes | Random jokes powered by `pyjokes` |
| 🎮 Mini Games | Number Guessing Game & Rock–Paper–Scissors |
| 🛑 Easy Exit | Stops immediately when you say "Stop", "Exit", "Bye", or "Koko stop" |

---

## ⚙️ How It Works

```
🎤 You speak "Koko"
        ↓
✅ Wake word detected → Koko activates & greets you
        ↓
🎤 You speak a command
        ↓
🔍 Koko checks: is this a known command?
        ↓
   ┌────────────┴────────────┐
  YES                         NO
   ↓                           ↓
Run built-in skill      Send to Google Gemini AI
(open app, play song,   for a smart spoken answer
weather, joke, game...)
        ↓
🗣️ Koko speaks the answer out loud
```

Once activated, Koko remains in continuous listening mode until you say **"Stop"** or **"Exit"**.

---

## 🤖 Gemini AI Integration

Koko is powered by **Google Gemini (`gemini-3.8-flash`)**. If you ask something outside the built-in system skills (e.g. general knowledge, school questions, science, or random facts), Koko queries Gemini and speaks back a concise, voice-friendly response.

You can ask things like:
- *"Explain photosynthesis"*
- *"Who is the President of India?"*
- *"Give me a motivational quote"*
- *"What is machine learning?"*

---

## 🛠️ Setup Guide

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/KOKO-Voice-Assistant__AI.git
cd KOKO-Voice-Assistant__AI
```

### 2️⃣ Install the required packages
```powershell
pip install SpeechRecognition pyaudio pyttsx3 requests pyjokes python-dotenv pywin32
```

### 3️⃣ Add your API keys
Create a file named `.env` in the project root folder (you can copy `.env.example`):
```env
GEMINI_KEY=your_gemini_api_key_here
WEATHER_KEY=your_openweathermap_api_key_here
```

🔑 **Get your free keys here:**
- **Gemini API:** https://aistudio.google.com/app/apikey
- **OpenWeatherMap API:** https://openweathermap.org/api

### 4️⃣ Run Koko
```powershell
python neo.py
```

1. Enter your name when prompted.
2. Say **"Koko"** out loud into your microphone.
3. Once greeted, speak your command! 🎙️

---

## 🗣️ Example Commands

| You say | Koko does |
|---|---|
| **"Koko"** | Wakes up and greets you |
| **"Play Drop Dead"** | Finds the video and plays it directly on YouTube |
| **"Open YouTube"** | Opens YouTube in your browser |
| **"Open Notepad"** | Launches Notepad app |
| **"Open Calculator"** | Launches Calculator app |
| **"What's the weather"** | Prompts for a city and reports live weather |
| **"What time is it"** | Tells the current time and date |
| **"Tell me a joke"** | Speaks a random joke |
| **"Guess the number"** | Starts the Number Guessing mini-game |
| **"Rock paper scissors"** | Starts a round of Rock–Paper–Scissors |
| **"Explain photosynthesis"** | Queries Gemini AI and speaks the answer |
| **"Stop" / "Exit" / "Bye"** | Says "Thank you, Goodbye" and terminates cleanly |

---

## 📁 Project Structure

```
📦 koko-voice-assistant
├── 🐍 neo.py              → Main assistant engine (voice input, logic & speech)
├── 🎵 musiclibrary.py     → Shortcut music link mapping
├── 🔒 .env.example        → Template for required API keys
├── 🔒 .env                → Your private API keys (kept secret, ignored by git)
├── 📄 requirements.txt    → List of Python packages needed
└── 🚫 .gitignore          → Keeps .env, venv, and __pycache__ out of GitHub
```

---

## 🩺 Troubleshooting

| Problem | Likely Fix |
|---|---|
| Koko doesn't hear "Koko" | Speak clearly after the 1-second background calibration. Check microphone privacy settings in Windows. |
| No voice / silent | Ensure computer volume is turned up and default output audio device is selected. |
| Weather says "City Not Found" | Check your city spelling or verify your `WEATHER_KEY` in `.env`. |
| Gemini errors out | Verify `GEMINI_KEY` is pasted correctly in `.env` without quotes or spaces. |

---

## ⚠️ Notes

- Requires an active microphone and internet connection (for speech recognition, YouTube scraping, and Gemini AI).
- Designed for Windows (uses native Windows SAPI TTS and Windows application launchers).
- Never share or commit your `.env` file to GitHub.

---

<div align="center">

Made with 🐍 Python, 🎤 Speech Recognition, and ✨ Google Gemini AI.

</div>
