import gradio as gr
import requests

BACKEND_URL = "http://localhost:8000/chat"

def chat_fn(message, history):
    resp = requests.post(BACKEND_URL, json={"message": message})
    if resp.status_code != 200:
        return "Error: backend not reachable"
    data = resp.json()
    answer = data["answer"]["response"]
    citations = ", ".join([f"{c['name']} (#{c['id']})" for c in data["citations"]])
    return f"{answer}\n\n**Sources:** {citations}"

gr.ChatInterface(fn=chat_fn, title="Pokémon RAG Chat").launch(server_name="0.0.0.0", server_port=7860)
