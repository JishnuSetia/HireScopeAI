import requests

OLLAMA_MODEL = "llama3.2"

def query_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json().get("response", "No response from Ollama")
    except Exception as e:
        return f"Error calling Ollama API: {e}"

def get_interview_questions(transcript):
    prompt = f"""
You are an AI interview assistant. Given the candidate's answer below, generate 3 insightful follow-up interview questions the interviewer should ask next. Please note, the input might also be the interviewer's question. If that is the case, ignore or do not respond. Rate the Candidate's answer too.

Candidate's response:
\"\"\"{transcript}\"\"\"

Response Rating:

Interviewer questions:
"""
    return query_ollama(prompt)

def check_ollama_running():
    try:
        r = requests.get("http://localhost:11434")
        return r.status_code == 200
    except:
        return False
