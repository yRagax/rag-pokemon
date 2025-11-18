from string import Template
import gradio as gr
import requests
import time
import re

BACKEND_URL = "http://localhost:8000/chat"
with open("frontend/assets/html/inline_source_button.html", 'r') as f:
    CITATION_TEMPLATE = Template(f.read())
with open("frontend/assets/css/typing_dots.css", 'r') as f:
    TYPING_DOTS_STYLE = f.read()

def format_inline_citations(text):
    pattern = r"\(ID:\s*(\d+)\)"
    def repl(m):
        poke_id = m.group(1)
        url = f"https://www.pokemon.com/us/pokedex/{poke_id}"
        return CITATION_TEMPLATE.substitute(poke_id=poke_id, url=url)
    return re.sub(pattern, repl, text)

def chat_fn(message, history):

    history = history + [[message, '<i class="typing-dots">⏳ Thinking</i>']]
    yield "", history

    formatted_history = []
    for user_msg, assistant_msg in history[:-1]:
        formatted_history.append({"role": "user", "content": user_msg})
        formatted_history.append({"role": "assistant", "content": assistant_msg})

    payload = {"message": message, "history": formatted_history}

    start_time = time.time()
    try:
        resp = requests.post(BACKEND_URL, json=payload, timeout=120)
    except requests.exceptions.RequestException:
        history[-1][1] = "❌ Error: backend not reachable."
        yield "", history
        return

    elapsed = time.time() - start_time
    if resp.status_code != 200:
        history[-1][1] = f"❌ Backend error: {resp.status_code} (⏱ {elapsed:.1f}s)"
        yield "", history
        return

    data = resp.json()
    answer = data["answer"]

    answer = format_inline_citations(answer)
    answer = answer.replace('\n', '<br>')

    answer_html = (
        f"{answer}"
        # f"<hr><b>Sources:</b> "
        # f"{', '.join([f'{c['name']} (#{c['id']})' for c in data['citations']])}"
        f"<br><br><i>🕓 Thought for {elapsed:.1f}s</i>"
    )

    history[-1][1] = answer_html
    yield "", history

with gr.Blocks(title="Pokémon RAG Chat", css=TYPING_DOTS_STYLE) as demo:
    chatbot = gr.Chatbot(label="Pokémon RAG Chat", type='tuples', height=600)
    textbox = gr.Textbox(label="Ask something")

    textbox.submit(chat_fn, [textbox, chatbot], [textbox, chatbot])

demo.launch(server_name="0.0.0.0", server_port=7860)
