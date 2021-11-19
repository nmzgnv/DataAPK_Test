from aiohttp_pydantic.injectors import Group
from pydantic import Field, BaseModel


class ConvertHandlerModel(Group):
    from_: str = Field(alias='from')
    to: str
    amount: float


class DatabaseHandlerModel(BaseModel):
    merge: int = Field(ge=0, le=1)
