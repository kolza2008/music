from sqlalchemy.orm import Mapped
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import PrimaryKeyConstraint


engine = create_engine("sqlite:///db.db", echo=True)

class Model(DeclarativeBase):
    pass

class Song(Model):
    __tablename__ = 'songs'
    id: Mapped[str] = mapped_column(primary_key=True)
    md5hash: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    author: Mapped[str]
    thumbnail: Mapped[str]


Model.metadata.create_all(engine)