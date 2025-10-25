from langchain.agents import create_agent
from langchain_ollama.chat_models import ChatOllama
from .models import PokemonFilter

model = ChatOllama(model="llama3.1")
filter_agent = create_agent(
    model=model,
    tools=[],
    response_format=PokemonFilter,
    system_prompt=(
        "You are a Pokémon search assistant. "
        "You will help a user to retrieve Pokémon data based on their question. "
        "You need to create one filter request in JSON format, to filter the Pokémon. "
        "You can search by Pokémon name, type, or abilities, and you can sort by various stats. "
        "Convert the user's question into one query that matches the structure of the Pokémon filter. "
        "You do not need to fill in all fields; only provide the relevant ones based on the user's request. "
        "The database will return all information about the Pokémon. "
        "If you're retrying, do not add any additional explanation or comments, just provide the JSON. "
        "What Pokémon does the user want to retrieve?"
        # "The database will return information about Pokémon names, types, abilities, stats (HP, attack, defense, special-attack, special-defense, and speed), height, weight, moves and flavor text."
        # "Tool call should be only in JSON format as per the specified structure, without any additional comments."
    )
)
