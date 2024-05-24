import uuid

from sqlalchemy import *
from sqlalchemy.dialects.mysql import LONGTEXT

from . import Base


class Riddle(Base):
    __tablename__ = 'riddles'

    riddle_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    creator = Column(String(255))
    title = Column(String(255))
    problem = Column(String(255))
    situation = Column(String(3000))
    answer = Column(String(255))
    progress_sentences = Column(String(3000))
    hit_ratio = Column(Float)
    point_1 = Column(Integer)
    point_2 = Column(Integer)
    point_3 = Column(Integer)
    point_4 = Column(Integer)
    point_5 = Column(Integer)
    problem_embedding_str = Column(LONGTEXT)
    situation_embedding_str = Column(LONGTEXT)
    answer_embedding_str = Column(LONGTEXT)
