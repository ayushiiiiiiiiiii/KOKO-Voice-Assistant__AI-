import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import speech_recognition as sr
import neo

class KokoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KOKO — AI Voice Assistant")
        self.root.geometry("620x720")
        self.root.minsize(520, 620)
        self.root.configure(bg="#181825")

        # State flags
        self.is_running = False
        self.worker_thread = None
        self.user_name = "Ayushi"

        # Register callback with neo so spoken text also appears in chat log
        neo.gui_log_callback = self.log_assistant_message

        self.setup_ui()

    def setup_ui(self):
        # 1. Header Frame (Top)
        header_frame = tk.Frame(self.root, bg="#1e2030", pady=12)
        header_frame.pack(side="top", fill="x")

        title_label = tk.Label(
            header_frame,
            text="🎙️ KOKO AI",
            font=("Segoe UI", 18, "bold"),
            fg="#8aadf4",
            bg="#1e2030"
        )
        title_label.pack()

        subtitle_label = tk.Label(
            header_frame,
            text="Your Personal AI Voice Assistant",
            font=("Segoe UI", 10),
            fg="#a5adcb",
            bg="#1e2030"
        )
        subtitle_label.pack(pady=(2, 6))

        # Status Indicator Badge
        self.status_var = tk.StringVar(value="● Ready — Click 'Start Listening' or type below")
        self.status_label = tk.Label(
            header_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 10, "bold"),
            fg="#eed49f",
            bg="#24273a",
            padx=16,
            pady=5,
            relief="flat"
        )
        self.status_label.pack()

        # 2. Control Buttons (PACKED AT TOP RIGHT UNDER HEADER - ALWAYS VISIBLE!)
        controls_frame = tk.Frame(self.root, bg="#181825", padx=16, pady=10)
        controls_frame.pack(side="top", fill="x")

        self.start_btn = tk.Button(
            controls_frame,
            text="🎙️ Start Listening",
            font=("Segoe UI", 11, "bold"),
            bg="#a6da95",
            fg="#181825",
            activebackground="#8bd5ca",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=8,
            command=self.start_voice_assistant
        )
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.stop_btn = tk.Button(
            controls_frame,
            text="⏹️ Stop Assistant",
            font=("Segoe UI", 11, "bold"),
            bg="#ed8796",
            fg="#181825",
            activebackground="#ee99a0",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=8,
            state="disabled",
            command=self.stop_voice_assistant
        )
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=(6, 6))

        self.clear_btn = tk.Button(
            controls_frame,
            text="🗑️ Clear",
            font=("Segoe UI", 10),
            bg="#363a4f",
            fg="#cad3f5",
            activebackground="#494d64",
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=8,
            command=self.clear_chat
        )
        self.clear_btn.pack(side="right", padx=(6, 0))

        # 3. Bottom Text Input Bar (PACKED AT BOTTOM BEFORE CHAT TO NEVER BE CUT OFF)
        input_frame = tk.Frame(self.root, bg="#181825", padx=16, pady=10)
        input_frame.pack(side="bottom", fill="x")

        self.input_entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 11),
            bg="#24273a",
            fg="#cad3f5",
            insertbackground="#cad3f5",
            relief="flat",
            bd=6
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=4)
        self.input_entry.bind("<Return>", lambda event: self.send_text_command())

        self.send_btn = tk.Button(
            input_frame,
            text="Send 🚀",
            font=("Segoe UI", 10, "bold"),
            bg="#8aadf4",
            fg="#181825",
            activebackground="#7dc4e4",
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=6,
            command=self.send_text_command
        )
        self.send_btn.pack(side="right")

        # 4. Chat Log Display (Fills the remaining center area)
        chat_frame = tk.Frame(self.root, bg="#181825", padx=16, pady=2)
        chat_frame.pack(side="top", fill="both", expand=True)

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap="word",
            font=("Segoe UI", 11),
            bg="#1e2030",
            fg="#cad3f5",
            insertbackground="#cad3f5",
            padx=14,
            pady=14,
            relief="flat",
            state="disabled"
        )
        self.chat_display.pack(fill="both", expand=True)

        # Chat Text Tags for Styling
        self.chat_display.tag_config("user", foreground="#8aadf4", font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_config("koko", foreground="#a6da95", font=("Segoe UI", 11))
        self.chat_display.tag_config("system", foreground="#939ab7", font=("Segoe UI", 10, "italic"))

        # Welcome message
        self.log_system_message("KOKO AI Assistant ready! Click 'Start Listening' to speak or simply type a message below.")

    # --- Logging Methods (Thread-Safe) ---
    def log_message(self, tag, prefix, message):
        def _append():
            self.chat_display.configure(state="normal")
            self.chat_display.insert("end", prefix, tag)
            self.chat_display.insert("end", f" {message}\n\n")
            self.chat_display.see("end")
            self.chat_display.configure(state="disabled")
        self.root.after(0, _append)

    def log_user_message(self, message):
        self.log_message("user", "👤 You:", message)

    def log_assistant_message(self, message):
        self.log_message("koko", "🤖 Koko:", message)

    def log_system_message(self, message):
        self.log_message("system", "ℹ️", message)

    def update_status(self, text, color="#eed49f"):
        def _update():
            self.status_var.set(text)
            self.status_label.configure(fg=color)
        self.root.after(0, _update)

    def clear_chat(self):
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")
        self.log_system_message("Chat cleared.")

    # --- Manual Text Execution (Simply Send Msg!) ---
    def send_text_command(self):
        text = self.input_entry.get().strip()
        if not text:
            return
        self.input_entry.delete(0, "end")
        self.log_user_message(text)

        # Run command directly in thread (no wake word needed!)
        threading.Thread(target=self._execute_command, args=(text,), daemon=True).start()

    def _execute_command(self, cmd):
        self.update_status("● Thinking...", "#8aadf4")
        cmd_clean = cmd.lower().strip()
        stop_words = ['cancel', 'exit', 'stop', 'goodbye', 'good bye', 'quit', 'bye', 'bye bye', 'koko stop']
        if cmd_clean in stop_words:
            neo.bol(f"Thank you, Goodbye {self.user_name}")
            self.stop_voice_assistant()
            return

        neo.processcommand(cmd)
        if self.is_running:
            self.update_status("● Listening for command...", "#a6da95")
        else:
            self.update_status("● Ready", "#eed49f")

    # --- Voice Listening Worker Thread ---
    def start_voice_assistant(self):
        if self.is_running:
            return
        self.is_running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.update_status("● Calibrating microphone...", "#eed49f")

        self.worker_thread = threading.Thread(target=self._voice_loop, daemon=True)
        self.worker_thread.start()

    def stop_voice_assistant(self):
        self.is_running = False
        def _reset_ui():
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.update_status("● Ready — Click 'Start Listening'", "#eed49f")
            self.log_system_message("KOKO assistant stopped.")
        self.root.after(0, _reset_ui)

    def _voice_loop(self):
        try:
            with sr.Microphone() as mic:
                neo.r.adjust_for_ambient_noise(mic, duration=1)
                neo.r.dynamic_energy_threshold = True

                # Direct Activation: Clicking Start button already activates Koko!
                self.log_system_message("Microphone ready! Koko is activated and listening.")
                greeting = f"Hello {self.user_name}, how can I help you today?"
                neo.bol(greeting)

                # Continuous Command Loop (Speak command directly!)
                while self.is_running:
                    try:
                        self.update_status("● Listening for command...", "#a6da95")
                        audi = neo.r.listen(mic, timeout=5, phrase_time_limit=6)
                        self.update_status("● Recognizing...", "#eed49f")
                        command = neo.r.recognize_google(audi, language='en-US')
                        self.log_user_message(command)

                        cmd_clean = command.lower().strip()
                        stop_words = ['cancel', 'exit', 'stop', 'goodbye', 'good bye', 'quit', 'bye', 'bye bye', 'koko stop', 'stop koko', 'please stop']
                        if cmd_clean in stop_words or any(cmd_clean == w for w in ['stop', 'exit', 'quit', 'bye']):
                            neo.bol(f"Thank you, Goodbye {self.user_name}")
                            self.stop_voice_assistant()
                            break

                        # If user just repeats "Koko", acknowledge politely
                        wake_words = ['koko', 'coco', 'cocoa', 'kukoo', 'kuku']
                        if cmd_clean in wake_words:
                            neo.bol(f"Yes {self.user_name}, I am listening!")
                            continue

                        self.update_status("● Processing...", "#8aadf4")
                        neo.processcommand(command)

                    except (sr.UnknownValueError, sr.WaitTimeoutError):
                        continue
                    except Exception as e:
                        time.sleep(0.5)

        except Exception as e:
            self.log_system_message(f"Audio device error: {e}")
            self.stop_voice_assistant()

if __name__ == "__main__":
    root = tk.Tk()
    app = KokoGUI(root)
    root.mainloop()
