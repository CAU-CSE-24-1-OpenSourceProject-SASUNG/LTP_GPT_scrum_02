from sqlalchemy import Column, Integer, String, Float

from app.db.session import Base


class Riddle(Base):
    __tablename__ = 'riddles'

    riddle_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    title = Column(String(255))
    problem = Column(String(255))
    hit_ratio = Column(Float)
