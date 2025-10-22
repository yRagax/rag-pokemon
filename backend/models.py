from typing import List, Optional, Literal, Union
from pydantic import Field, BaseModel

POKEMON_TYPES = {
    "normal", "fire", "water", "electric", "grass", "ice", "fighting", "poison",
    "ground", "flying", "psychic", "bug", "rock", "ghost", "dragon", "dark",
    "steel", "fairy"
}

POKEMON_FIELD = Literal["name", "types", "abilities"]
POKEMON_STATS = Literal["hp", "attack", "defense", "special-attack", "special-defense", "speed"]
SORT_ORDER = Literal["asc", "desc"]

class PokemonFilter(BaseModel):
    field:      Optional[POKEMON_FIELD]         = Field(None, description="The field to filter by. Can be 'name', 'types', or 'abilities' only.")
    value:      Optional[List[Union[str, int]]] = Field(None, description="The values to filter for the specified field. E.g. ['Charmander'] or ['water', 'grass'] or ['levitate'].")
    sort_by:    Optional[POKEMON_STATS]         = Field(None, description="The field to sort the results by. Can be 'hp', 'attack', 'defense', 'special-attack', 'special-defense', or 'speed' only.")
    sort_order: Optional[SORT_ORDER]            = Field(None, description="The order to sort the results in. Can be 'asc' or 'desc' only.")
    limit:      Optional[int]                   = Field(None, description="The maximum number of results to return. E.g. 5, 10, etc.")
