import uuid

from sqlalchemy import *
from sqlalchemy.orm import relationship

from . import Base


class Riddle_Prompting(Base):
    __tablename__ = 'riddle_prompting'

    riddle_prompting_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    riddle_id = Column(String(36), ForeignKey('riddles.riddle_id'))
    user_query = Column(String(255))
    assistant_response = Column(String(255))

    riddle = relationship('Riddle', uselist=False)
