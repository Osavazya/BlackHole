from sqlalchemy import Column, Integer, String, Float
from .db import Base

class BlackHole(Base):
    __tablename__ = "blackholes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    distance_ly = Column(Float, nullable=True)  # light years
    mass_solar = Column(Float, nullable=True)
    description = Column(String(2000), nullable=True)
