from langchain.agents import create_agent
from langchain_ollama.chat_models import ChatOllama
from .models import PokemonFilter

model = ChatOllama(model="llama3.1")
filter_agent = create_agent(
    model=model,
    tools=[],
    response_format=PokemonFilter,
    system_prompt=(
        "You are a Pokémon search assistant. Convert the user's query into one structured search request. "
        "Focus on one specific field to be the filter. "
        "You do not need to fill all fields. "
        "If usage of some fields is ambiguous, leave them null."
        "Respond only in JSON format as per the specified structure, without any additional comments."
    )
)
