import queue
import threading
import speech_recognition as sr

class AudioStreamHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.audio_queue = queue.Queue()
        self.listening = False
        self._stop_event = threading.Event()

    def start_listening(self):
        if self.listening:
            return
        self.listening = True
        self._stop_event.clear()
        threading.Thread(target=self._listen_in_background, daemon=True).start()

    def stop_listening(self):
        self._stop_event.set()
        self.listening = False

    def _listen_in_background(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while not self._stop_event.is_set():
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)
                    transcript = self.recognizer.recognize_google(audio)
                    self.audio_queue.put(transcript)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    # Can't understand audio, skip
                    self.audio_queue.put(None)
                except Exception as e:
                    self.audio_queue.put(f"Error: {e}")
    