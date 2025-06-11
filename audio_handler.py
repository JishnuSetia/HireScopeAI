import numpy as np
import sounddevice as sd
import speech_recognition as sr
import threading

class AudioStreamHandler:
    def __init__(self, audio_levels, transcript_queue):
        self.audio_levels = audio_levels
        self.queue = transcript_queue
        self.audio_stream = None
        self.recognizer = sr.Recognizer()
        self.listening = False

    def audio_callback(self, indata, frames, time, status):
        volume_norm = np.linalg.norm(indata) * 10
        volume_norm = min(volume_norm, 1.0)
        self.audio_levels.append(volume_norm)
        if len(self.audio_levels) > 60:
            self.audio_levels.pop(0)

    def start_audio_stream(self):
        if self.listening:
            return
        self.listening = True
        self.audio_stream = sd.InputStream(callback=self.audio_callback)
        self.audio_stream.start()

    def stop_audio_stream(self):
        if not self.listening:
            return
        self.listening = False
        if self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
            self.audio_stream = None

    def recognize_speech(self, process_callback, keep_listening_flag):
        def listen_loop():
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                while keep_listening_flag:
                    try:
                        print("Listening...")
                        audio = self.recognizer.listen(source, phrase_time_limit=10)
                        print("Recognizing...")
                        transcript = self.recognizer.recognize_google(audio)
                        self.queue.put(transcript)
                        process_callback()
                    except sr.UnknownValueError:
                        self.queue.put("[Could not understand audio]")
                        process_callback()
                    except sr.RequestError as e:
                        self.queue.put(f"[Speech Recognition error: {e}]")
                        process_callback()
        threading.Thread(target=listen_loop, daemon=True).start()
