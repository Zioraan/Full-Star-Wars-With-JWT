from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    favorite_characters = relationship(
        "Character",
        secondary="favorite_characters",
        backref="favorited_by_users"
    )
    favorite_planets = relationship(
        "Planet",
        secondary="favorite_planets",
        backref="favorited_by_users"
    )
    favorite_species = relationship(
        "Species",
        secondary="favorite_species",
        backref="favorited_by_users"
    )

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "favorite_characters": [character.serialize() for character in self.favorite_characters],
            "favorite_planets": [planet.serialize() for planet in self.favorite_planets],
            "favorite_species": [species.serialize() for species in self.favorite_species]
        }


favorite_characters = db.Table('favorite_characters',
                               db.Column('user_id', db.Integer,
                                         db.ForeignKey('user.id')),
                               db.Column('character_id', db.Integer,
                                         db.ForeignKey('character.id'))
                               )

favorite_planets = db.Table('favorite_planets',
                            db.Column('user_id', db.Integer,
                                      db.ForeignKey('user.id')),
                            db.Column('planet_id', db.Integer,
                                      db.ForeignKey('planet.id'))
                            )

favorite_species = db.Table('favorite_species',
                            db.Column('user_id', db.Integer,
                                      db.ForeignKey('user.id')),
                            db.Column('species_id', db.Integer,
                                      db.ForeignKey('species.id'))
                            )


class Character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    hair_color: Mapped[str] = mapped_column(String(50), nullable=True)
    eye_color: Mapped[str] = mapped_column(String(50), nullable=True)
    homeworld: Mapped["Planet"] = relationship(back_populates="characters")
    homeworld_id: Mapped[int] = mapped_column(
        ForeignKey("planet.id"), nullable=True)
    species: Mapped["Species"] = relationship(back_populates="characters")
    species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id"), nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "homeworld": self.homeworld.name if self.homeworld else None,
            "species": self.species.name if self.species else None
        }


class Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    population: Mapped[int] = mapped_column(nullable=False)
    characters: Mapped[List["Character"]] = relationship(
        back_populates="homeworld")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "characters": [character.name for character in self.characters]
        }


class Species(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    average_height: Mapped[int] = mapped_column(nullable=False)
    average_lifespan: Mapped[int] = mapped_column(nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    characters: Mapped[List["Character"]] = relationship(
        back_populates="species")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "average_height": self.average_height,
            "average_lifespan": self.average_lifespan,
            "language": self.language,
            "characters": [character.name for character in self.characters]
        }
