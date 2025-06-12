
# HireScope AI — AI Interview Assistant

### Overview
HireScope AI is an intelligent interview assistant designed for HR professionals. It listens to live interviews between the interviewer and candidate, transcribes the conversation using speech recognition, and then suggests insightful follow-up questions using an AI language model (LLaMA 3.2). At the end of the interview, it generates a CSV report summarizing the session.

The tool is built using Python and Tkinter for the GUI, with no database dependencies. It leverages local speech recognition and Ollama's LLM API for AI-powered suggestions.

### Features
- 🎤 Real-time audio input from microphone with waveform visualization  
- 🧠 AI-powered follow-up question generation  
- 📄 Transcription of candidate responses using speech recognition  
- ✅ AI-based response rating  
- 🖥️ User-friendly GUI (start/stop interview)  
- 📊 CSV report generation  
- ⚙️ Lightweight — no database required

![alt text][imagePrev]

[imagePrev]: https://github.com/JishnuSetia/HireScopeAI/blob/main/IMAGE-HIRESCOPE.png?raw=true "PREVIEW"

### Getting Started
#### Prerequisites
- Python 3.9 or later (Can be installed from Microsoft Store or ```https://www.python.org/downloads/```)

- Ollama installed and running locally with the llama3.2 model (Can be installed from ```https://ollama.com/download``` and to get the model, run ```ollama pull llama3.2```)

- Microphone on your system for live audio input

- Minimum 16 GB of RAM on your device (Very slow performance on 16 GB. Greater the RAM, Faster the Performance)

#### Python Packages
Create a virtual environment first by running

```
python3 -m venv venv
```

Select the virtual environment by running

```
venv\Scripts\activate
```

Required packages can be installed using 

```
pip install -r requirements.txt
```
### Running the Application
- Ensure Ollama is running on ```localhost:11434``` (put that in your browser and you will see a message saying ```Ollama is running```)

- Make sure virtual environment is active

- Run the main script by running
```
python main.py
```
- Use the GUI buttons to start and stop the interview session.

- Watch live transcription and suggested questions appear in the interface.

- At the end, a CSV report will be generated in the project folder.

### Notes
- This application assumes Ollama is installed locally. Please install Ollama before running this app.

- Internet connection is required for Google's speech recognition API (used by speech_recognition package).

- The app currently supports English language only.

## License

All rights reserved.  
This project is provided for demonstration or evaluation purposes only.  
Use, modification, or redistribution without explicit permission is not allowed.
Please contact me for permission @ ```jishnusetia8@gmail.com```
