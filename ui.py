import tkinter as tk
from tkinter import scrolledtext, filedialog
import threading
import queue
from audio_handler import AudioStreamHandler
from ai_service import get_interview_questions, getReportForInterview

class AccentButton(tk.Button):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.default_bg = "#222222"
        self.default_fg = "#ff6600"
        self.hover_bg = "#ff6600"
        self.hover_fg = "#222222"
        self.config(
            bg=self.default_bg,
            fg=self.default_fg,
            activeforeground=self.hover_fg,
            activebackground=self.hover_bg,
            bd=0,
            relief=tk.FLAT,
            font=("Segoe UI Semibold", 14),
            cursor="hand2",
            padx=20,
            pady=12,
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.config(bg=self.hover_bg, fg=self.hover_fg)

    def on_leave(self, event):
        self.config(bg=self.default_bg, fg=self.default_fg)


class InterviewAssistant(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("HireScope AI - Interview Assistant")
        self.geometry("850x720")
        self.configure(bg="#121212")
        self.resizable(False, False)

        # Colors
        self.bg_color = "#121212"
        self.text_color = "#ffffff"
        self.accent_color = "#ff6600"
        self.panel_bg = "#1e1e1e"
        self.status_bg = "#1a1a1a"

        # Fonts
        self.font_header = ("Segoe UI Black", 32, "bold")
        self.font_subtitle = ("Segoe UI", 18)
        self.font_text = ("Consolas", 15)
        self.font_status = ("Segoe UI Italic", 13)

        self.interview_active = False

        self._setup_header()
        self._setup_controls()
        self._setup_status()
        self._setup_transcript_area()

        self.audio_handler = AudioStreamHandler()
        self.processing_queue = queue.Queue()
        self.ai_response_queue = queue.Queue()

        self.current_transcript = ""

        self.check_ai_response_queue()

    def _setup_header(self):
        header_frame = tk.Frame(self, bg=self.bg_color)
        header_frame.pack(pady=(20, 5), fill=tk.X)

        self.header = tk.Label(
            header_frame,
            text="HireScope AI",
            font=self.font_header,
            bg=self.bg_color,
            fg=self.accent_color,
        )
        self.header.pack()

        subtitle = tk.Label(
            header_frame,
            text="AI Interview Assistant",
            font=self.font_subtitle,
            fg=self.accent_color,
            bg=self.bg_color,
        )
        subtitle.pack(pady=(0, 15))

        # Thin accent underline below header
        underline = tk.Frame(self, height=1, bg=self.accent_color)
        underline.pack(fill=tk.X, padx=100, pady=(0, 20))

    def _setup_controls(self):
        controls_frame = tk.Frame(self, bg=self.bg_color)
        controls_frame.pack(pady=(0, 15))

        # Interview buttons container
        interview_frame = tk.Frame(controls_frame, bg=self.bg_color)
        interview_frame.grid(row=0, column=0, padx=15, pady=8)

        self.btn_start_interview = AccentButton(interview_frame, text="Start Interview", command=self.start_interview)
        self.btn_start_interview.grid(row=0, column=0, sticky="ew", padx=8)

        self.btn_end_interview = AccentButton(interview_frame, text="End Interview", command=self.end_interview, state=tk.DISABLED)
        self.btn_end_interview.grid(row=0, column=1, sticky="ew", padx=8)

        # Question buttons container (under interview buttons)
        question_frame = tk.Frame(controls_frame, bg=self.bg_color)
        question_frame.grid(row=1, column=0, pady=10)

        self.btn_start_question = AccentButton(question_frame, text="Start Question", command=self.start_recording, state=tk.DISABLED)
        self.btn_start_question.grid(row=0, column=0, sticky="ew", padx=8)

        self.btn_end_question = AccentButton(question_frame, text="End Question", command=self.stop_recording, state=tk.DISABLED)
        self.btn_end_question.grid(row=0, column=1, sticky="ew", padx=8)

        # Export buttons container (under question buttons)
        export_frame = tk.Frame(controls_frame, bg=self.bg_color)
        export_frame.grid(row=2, column=0, pady=10)

        self.btn_export_transcript = AccentButton(export_frame, text="Export Transcript", command=self.export_transcript, state=tk.DISABLED)
        self.btn_export_transcript.grid(row=0, column=0, sticky="ew", padx=8)

        self.btn_export_report = AccentButton(export_frame, text="Export Report", command=self.export_report, state=tk.DISABLED)
        self.btn_export_report.grid(row=0, column=1, sticky="ew", padx=8)

    def _setup_status(self):
        self.status_var = tk.StringVar(value="Status: Interview Not Started")
        status_frame = tk.Frame(self, bg=self.status_bg)
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=self.font_status,
            fg=self.accent_color,
            bg=self.status_bg,
            anchor="w",
            padx=15,
            pady=8,
        )
        self.status_label.pack(fill=tk.X)

    def _setup_transcript_area(self):
        transcript_frame = tk.Frame(self, bg=self.panel_bg, bd=2, relief=tk.SUNKEN)
        transcript_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=(0, 20))

        self.text_area = scrolledtext.ScrolledText(
            transcript_frame,
            wrap=tk.WORD,
            font=self.font_text,
            bg="#181818",
            fg=self.accent_color,
            relief=tk.FLAT,
            borderwidth=0,
            insertbackground=self.accent_color,
            undo=True,
            maxundo=-1,
            spacing3=5,
            height=28,
        )
        self.text_area.pack(expand=True, fill=tk.BOTH)

        # Tags styling
        self.text_area.tag_config("user", foreground="#ffa64d", font=("Consolas", 15, "bold"))
        self.text_area.tag_config("ai", foreground="#ff6600", font=("Consolas", 15, "italic"))
        self.text_area.tag_config("system", foreground="#999999", font=("Segoe UI", 12, "italic"))

        self.text_area.configure(state=tk.DISABLED)

    def start_interview(self):
        self.interview_active = True
        self.status_var.set("Status: Interview Active")
        self.btn_start_interview.config(state=tk.DISABLED)
        self.btn_end_interview.config(state=tk.NORMAL)
        self.btn_start_question.config(state=tk.NORMAL)
        self.btn_end_question.config(state=tk.DISABLED)

        self.btn_export_transcript.config(state=tk.DISABLED)
        self.btn_export_report.config(state=tk.DISABLED)

        self._append_text("\n=== Interview Started ===\n", "system")

    def end_interview(self):
        self.interview_active = False
        self.status_var.set("Status: Interview Ended")
        self.btn_start_interview.config(state=tk.NORMAL)
        self.btn_end_interview.config(state=tk.DISABLED)
        self.btn_start_question.config(state=tk.DISABLED)
        self.btn_end_question.config(state=tk.DISABLED)

        self.btn_export_transcript.config(state=tk.NORMAL)
        self.btn_export_report.config(state=tk.NORMAL)

        self._append_text("\n=== Interview Ended ===\n", "system")
        self.audio_handler.stop_listening()
        with self.processing_queue.mutex:
            self.processing_queue.queue.clear()
        with self.ai_response_queue.mutex:
            self.ai_response_queue.queue.clear()

    def start_recording(self):
        if not self.interview_active:
            self._append_text("\n[Start Interview before starting questions]\n", "system")
            return
        self._append_text("\n[Listening... Speak Now]\n", "system")
        self.btn_start_question.config(state=tk.DISABLED)
        self.btn_end_question.config(state=tk.NORMAL)
        self.current_transcript = ""
        self.audio_handler.start_listening()

    def stop_recording(self):
        self.audio_handler.stop_listening()
        self.btn_start_question.config(state=tk.NORMAL)
        self.btn_end_question.config(state=tk.DISABLED)

        collected = []
        while not self.audio_handler.audio_queue.empty():
            phrase = self.audio_handler.audio_queue.get()
            if phrase:
                collected.append(phrase)

        self.current_transcript = " ".join(collected).strip()

        if not self.current_transcript:
            self._append_text("\n[No clear audio detected. Skipping AI processing]\n", "system")
            return

        self._append_text(f"\nCandidate: {self.current_transcript}\n", "user")
        self.processing_queue.put(self.current_transcript)

        if not hasattr(self, 'ai_thread') or not self.ai_thread.is_alive():
            self.ai_thread = threading.Thread(target=self.process_ai_responses, daemon=True)
            self.ai_thread.start()

    def process_ai_responses(self):
        while not self.processing_queue.empty():
            transcript = self.processing_queue.get()
            ai_response = get_interview_questions(transcript)
            self.ai_response_queue.put(ai_response)

    def check_ai_response_queue(self):
        try:
            while True:
                response = self.ai_response_queue.get_nowait()
                self._append_text(f"\nInterviewer AI:\n{response}\n", "ai")
        except queue.Empty:
            pass
        self.after(500, self.check_ai_response_queue)

    def _append_text(self, text, tag=None):
        self.text_area.configure(state=tk.NORMAL)
        self.text_area.insert(tk.END, text, tag)
        self.text_area.see(tk.END)
        self.text_area.configure(state=tk.DISABLED)

    def export_transcript(self):
        if not self.current_transcript:
            self._append_text("\n[No transcript available to export]\n", "system")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Save Transcript As"
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.text_area.get("1.0", tk.END))
            self._append_text(f"\n[Transcript exported to {file_path}]\n", "system")

    def export_report(self):
        if not self.current_transcript:
            self._append_text("\n[No interview data available for report]\n", "system")
            return

        report = getReportForInterview(self.text_area.get("1.0", tk.END))
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Save Report As"
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(report)
            self._append_text(f"\n[Interview report exported to {file_path}]\n", "system")


if __name__ == "__main__":
    app = InterviewAssistant()
    app.mainloop()
