from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Country(Base):
    __tablename__ = 'countries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    movies = relationship("Movie", back_populates="country")

class Genre(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    movies = relationship("Movie", secondary='movie_genre', back_populates='genres')

class Actor(Base):
    __tablename__ = 'actors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    movies = relationship("Movie", secondary='movie_actor', back_populates='actors')

class Movie(Base):
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    release_year = Column(String(20))
    score = Column(Float)
    summary = Column(Text)
    image_url = Column(String(255))
    country_id = Column(Integer, ForeignKey('countries.id'))
    country = relationship('Country', back_populates='movies')
    genres = relationship("Genre", secondary='movie_genre', back_populates='movies')
    actors = relationship("Actor", secondary='movie_actor', back_populates='movies')

class MovieGenre(Base):
    __tablename__ = 'movie_genre'
    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    genre_id = Column(Integer, ForeignKey('genres.id'), primary_key=True)

class MovieActor(Base):
    __tablename__ = 'movie_actor'
    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    actor_id = Column(Integer, ForeignKey('actors.id'), primary_key=True)

class Ranking(Base):
    __tablename__ = 'rankings'
    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey('countries.id', ondelete='CASCADE'))
    movie_id = Column(Integer, ForeignKey('movies.id', ondelete='CASCADE'))
    rank = Column(Integer)

    country = relationship('Country')
    movie = relationship('Movie')

    def __str__(self):
        return f'{self.country.name} - {self.rank} - {self.movie.title}'