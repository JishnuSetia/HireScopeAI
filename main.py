from ui import InterviewAssistant
from ai_service import check_ollama_running

if __name__ == "__main__":
    if not check_ollama_running():
        print("Ollama not running. Please start it before launching the app.")
    else:
        app = InterviewAssistant()
        app.mainloop()
