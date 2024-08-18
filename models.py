from typing import List
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import PrimaryKeyConstraint


engine = create_engine("sqlite:///db.db") #, echo=True

class Model(DeclarativeBase):
    pass

class Artist(Model):
    __tablename__ = "artists"
    id: Mapped[str] = mapped_column(primary_key=True)
    mbid: Mapped[str]
    name: Mapped[str]

    albums: Mapped[List["Album"]] = relationship(back_populates="artist")

class Album(Model):
    __tablename__ = "albums"
    id: Mapped[str] = mapped_column(primary_key=True)
    md5: Mapped[str] = mapped_column(unique=True)
    mbid: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    released_at: Mapped[str] = mapped_column(nullable=True)
    thumbnail: Mapped[str] = mapped_column(nullable=True)
    artistID: Mapped[str] = mapped_column(ForeignKey("artists.id"), nullable=True)

    songs: Mapped[List["Song"]] = relationship(back_populates="album")
    artist: Mapped[Artist] = relationship(back_populates="albums")

class Song(Model):
    __tablename__ = 'songs'
    id: Mapped[str] = mapped_column(primary_key=True)
    md5: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    author: Mapped[str]
    thumbnail: Mapped[str]
    thumbnail1000: Mapped[str]
    albumID: Mapped[str] = mapped_column(ForeignKey("albums.id"))
    album: Mapped["Album"] = relationship(back_populates="songs")


Model.metadata.create_all(engine)