from pydantic import BaseModel
from typing import Optional

class BlackHoleBase(BaseModel):
    name: str
    distance_ly: Optional[float] = None
    mass_solar: Optional[float] = None
    description: Optional[str] = None

class BlackHoleCreate(BlackHoleBase):
    pass

class BlackHoleRead(BlackHoleBase):
    id: int

    class Config:
        from_attributes = True
