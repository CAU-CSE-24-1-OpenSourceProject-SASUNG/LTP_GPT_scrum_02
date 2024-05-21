from pydantic import BaseModel


class QueryInfoDto(BaseModel):
    game_id: str
    query: str
