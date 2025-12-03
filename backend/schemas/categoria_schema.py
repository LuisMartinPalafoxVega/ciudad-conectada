from pydantic import BaseModel

class CategoriaBase(BaseModel):
    nombre: str
    icono: str | None = None
    color: str | None = None


class CategoriaResponse(CategoriaBase):
    id: int

    class Config:
        from_attributes = True

