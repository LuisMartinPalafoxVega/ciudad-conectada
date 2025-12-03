from pydantic import BaseModel, EmailStr
from datetime import datetime

class LikeResponse(BaseModel):
    id: int
    usuario_id: int
    fecha_like: datetime

    class Config:
        from_attributes = True