import tkinter as tk
import threading
import queue
from audio_handler import AudioStreamHandler
from ai_service import get_interview_questions

class InterviewAssistant(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Interview Assistant")
        self.geometry("350x400")
        self.resizable(False, False)

        self.is_listening = False
        self.audio_levels = [0]*60

        self.text_area = tk.Text(self, height=10, width=50, wrap=tk.WORD)
        self.text_area.pack(pady=10)

        self.audio_level_bar = tk.Canvas(self, width=380, height=60, bg="black")
        self.audio_level_bar.pack(pady=5)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)

        self.start_button = tk.Button(self.button_frame, text="Start Interview", command=self.start_listening)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(self.button_frame, text="Stop Interview", command=self.stop_listening, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.queue = queue.Queue()

        self.audio_handler = AudioStreamHandler(self.audio_levels, self.queue)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_listening(self):
        if self.is_listening:
            return
        self.is_listening = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, "\n--- Interview Started ---\n")
        self.text_area.see(tk.END)
        self.audio_levels[:] = [0]*60
        self.update_audio_level_bar()

        self.audio_handler.start_audio_stream()
        threading.Thread(target=self.listen_and_process, daemon=True).start()

    def stop_listening(self):
        if not self.is_listening:
            return
        self.is_listening = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.text_area.insert(tk.END, "\n--- Interview Stopped ---\n")
        self.text_area.see(tk.END)
        self.audio_handler.stop_audio_stream()

    def update_audio_level_bar(self):
        self.audio_level_bar.delete("all")
        w = 6
        spacing = 1
        height = 60
        for i, level in enumerate(self.audio_levels):
            x0 = i * (w + spacing)
            bar_height = level * height
            y0 = height - bar_height
            x1 = x0 + w
            y1 = height
            self.audio_level_bar.create_rectangle(x0, y0, x1, y1, fill="lime", width=0)
        if self.is_listening:
            self.after(50, self.update_audio_level_bar)

    def listen_and_process(self):
        self.audio_handler.recognize_speech(self.process_transcript, self.is_listening)

    def process_transcript(self):
        while not self.queue.empty():
            transcript = self.queue.get()
            self.text_area.insert(tk.END, f"\nCandidate said: {transcript}\n")
            self.text_area.see(tk.END)

            questions = get_interview_questions(transcript)
            self.text_area.insert(tk.END, f"\nSuggested questions:\n{questions}\n")
            self.text_area.see(tk.END)

    def on_closing(self):
        self.stop_listening()
        self.destroy()
