import gradio as gr
import requests
import time
import re

BACKEND_URL = "http://localhost:8000/chat"

def format_inline_citations(text):
    pattern = r"\(ID:\s*(\d+)\)"
    def repl(m):
        poke_id = m.group(1)
        url = f"https://www.pokemon.com/us/pokedex/{poke_id}"
        return (f'<a href="{url}" target="_blank" '
                f'style="display:inline-block; padding:2px 6px; margin-left:4px; '
                f'background:#eef; border:1px solid #99c; border-radius:6px; '
                f'font-size:0.50em; text-decoration:none; color:#004;">'
                f'Source {poke_id}</a>')
    return re.sub(pattern, repl, text)

def chat_fn(message, history):

    formatted_history = []
    for user_msg, assistant_msg in history:
        formatted_history.append({"role": "user", "content": user_msg})
        formatted_history.append({"role": "assistant", "content": assistant_msg.value if isinstance(assistant_msg, gr.HTML) else assistant_msg})

    payload = {"message": message, "history": formatted_history}

    start_time = time.time()
    try:
        resp = requests.post(BACKEND_URL, json=payload, timeout=120)
    except requests.exceptions.RequestException:
        return history + [[message, "❌ Error: backend not reachable."]]

    elapsed = time.time() - start_time
    if resp.status_code != 200:
        return history + [[message, f"❌ Backend error: {resp.status_code} (⏱ {elapsed:.1f}s)"]]

    data = resp.json()
    answer = data["answer"]

    answer = format_inline_citations(answer)
    answer = answer.replace('\n', '<br>')

    answer_html = gr.HTML(
        f"{answer}"
        # f"<hr><b>Sources:</b> "
        # f"{', '.join([f'{c['name']} (#{c['id']})' for c in data['citations']])}"
        f"<br><br><i>🕓 Thought for {elapsed:.1f}s</i>"
    )

    return '', history + [[message, answer_html]]

with gr.Blocks(title="Pokémon RAG Chat") as demo:
    chatbot = gr.Chatbot(label="Pokémon RAG Chat", type='tuples', height=600)
    textbox = gr.Textbox(label="Ask something")

    textbox.submit(chat_fn, [textbox, chatbot], [textbox, chatbot])

demo.launch(server_name="0.0.0.0", server_port=7860)
