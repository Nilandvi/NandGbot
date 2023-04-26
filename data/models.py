from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from data.config import DB_URL

engine = create_engine(DB_URL)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    chat_id = Column(Integer, unique=True)

    def __repr__(self):
        return f"<User(username='{self.username}', chat_id='{self.chat_id}')>"

class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    note_text = Column(String(4096))

    def __repr__(self):
        return f"<Note for user_id='{self.user_id}' with text='{self.note_text}'>"



Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
