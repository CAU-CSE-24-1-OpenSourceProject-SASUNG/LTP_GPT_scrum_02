from sqlalchemy import Column, Integer, String, Float

from app.db.session import Base

class Riddle(Base):
    __tablename__ = 'riddles'

    riddle_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255))
    problem = Column(String(255))
    title = Column(String(255))
    hit_ratio = Column(Float)
