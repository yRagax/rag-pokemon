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
    try:
        resp = requests.post(BACKEND_URL, json=payload, timeout=20)
    except requests.exceptions.RequestException:
        return "❌ Error: backend not reachable."
    elapsed = time.time() - start_time
    if resp.status_code != 200:
        return f"❌ Backend error: {resp.status_code} (⏱ {elapsed:.1f}s)"

    data = resp.json()
    answer = data["answer"]
    citations = ", ".join([f"{c['name']} (#{c['id']})" for c in data["citations"]])

    return f"{answer}\n\n**Źródła:** {citations}\n\n🕓 *Thought for {elapsed:.1f}s*"

gr.ChatInterface(fn=chat_fn, title="Pokémon RAG Chat").launch(server_name="0.0.0.0", server_port=7860)
