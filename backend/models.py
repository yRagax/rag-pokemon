from typing import List, Optional, Literal, Union
from pydantic import Field, BaseModel, model_validator

POKEMON_TYPES = {
    "normal", "fire", "water", "electric", "grass", "ice", "fighting", "poison",
    "ground", "flying", "psychic", "bug", "rock", "ghost", "dragon", "dark",
    "steel", "fairy"
}

POKEMON_FIELD = Literal["name", "types", "abilities"]
POKEMON_STATS = Literal["hp", "attack", "defense", "special-attack", "special-defense", "speed"]
SORT_ORDER = Literal["asc", "desc"]

class PokemonFilter(BaseModel):
    field:      Optional[POKEMON_FIELD]         = Field(None, description="The field to filter by. Must be one of 'name', 'types', 'abilities', or null only. Must be specified with the value.")
    value:      Optional[List[Union[str, int]]] = Field(None, description="The values to filter for the specified field. E.g. ['Charmander', 'Charmeleon'] or ['water', 'grass'] or ['levitate'], etc. Must be specified with the field.")
    sort_by:    Optional[POKEMON_STATS]         = Field(None, description="The field to sort the results by. Must be one of 'hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed' or null only.")
    sort_order: Optional[SORT_ORDER]            = Field(None, description="The order to sort the results in. Must be one of 'asc', 'desc' or null only.")
    limit:      Optional[int]                   = Field(None, description="The maximum number of results to return. E.g. 5, 10, etc.")

    @model_validator(mode="after")
    def check_field_with_value(self):
        if self.value is not None and self.field is None:
            raise ValueError("For what field are these values? It must be either 'name', 'types' or 'abilities'.")
        return self
