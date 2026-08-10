from sqlalchemy import Column, Integer, String, Boolean
from database import Base


class Room(Base):
    __tablename__ = "rooms"  # this becomes the SQL table name

    id        = Column(Integer, primary_key=True, index=True)
    name      = Column(String, nullable=False)
    price     = Column(Integer, nullable=False)
    available = Column(Boolean, default=True)
