import gradio as gr
import requests
import time

BACKEND_URL = "http://localhost:8000/chat"

def chat_fn(message, history):
    formatted_history = []
    for pair in history:
        formatted_history.append({"role": "user", "content": pair[0]})
        formatted_history.append({"role": "assistant", "content": pair[1]})
    payload = {
        "message": message,
        "history": formatted_history
    }
    start_time = time.time()
    resp = requests.post(BACKEND_URL, json=payload, timeout=120)
    elapsed_time = time.time() - start_time
    if resp.status_code != 200:
        return "Error: backend not reachable"
    data = resp.json()
    answer = data["answer"]
    citations = ", ".join([f"{c['name']} (#{c['id']})" for c in data["citations"]])
    return f"{answer}\n\n**Źródła:** {citations}\n\n🕓 *Thought for {elapsed_time:.1f}s*"

gr.ChatInterface(fn=chat_fn, title="Pokémon RAG Chat").launch(server_name="0.0.0.0", server_port=7860)
