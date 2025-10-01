"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Character, Species, Planet, favorite_species, favorite_characters, favorite_planets
from api.utils import generate_sitemap, APIException
from flask_cors import CORS

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200

@api.route('/users/sign-up', methods=['POST'])
def add_new_user():
    body = request.json
    if body is None:
        return jsonify({"msg": "information is required"}), 400
    if body["email"] is None:
        return jsonify({"msg": "email is required"}), 400
    if body["password"] is None:
        return jsonify({"msg": "password is required"}), 400
    new_user = User()
    new_user.email = body["email"]
    new_user.password = body["password"]
    new_user.is_active = True

    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.serialize()), 201

@api.route('/users/log-in', methods=['POST'])
def log_in_user():
    body = request.json
    if body is None:
        return jsonify({"msg": "information is required"}), 400
    if body["email"] is None:
        return jsonify({"msg": "email is required"}), 400
    if body["password"] is None:
        return jsonify({"msg": "password is required"}), 400

    user = User.query.filter_by(email=body["email"], password=body["password"]).first()
    if user is None:
        return jsonify({"msg": "Invalid credentials"}), 401

    return jsonify(user.serialize()), 200

@api.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    users_serialized = [user.serialize() for user in users]
    return jsonify(users_serialized), 200

@api.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": "User not found"}), 404
    favorites = {
        "species": [species.serialize() for species in user.favorite_species],
        "characters": [character.serialize() for character in user.favorite_characters],
        "planets": [planet.serialize() for planet in user.favorite_planets]
    }
    return jsonify(favorites), 200

@api.route('/characters', methods=['POST'])
def add_new_character():
    body = request.json
    if body is None:
        return jsonify({"msg": "information is required"}), 400
    if body["name"] is None:
        return jsonify({"msg": "name is required"}), 400
    if body["homeworld_id"] is None:
        return jsonify({"msg": "homeworld id is required"}), 400
    if body["species_id"] is None:
        return jsonify({"msg": "species id is required"}), 400
    new_character = Character()
    new_character.name = body["name"]
    new_character.hair_color = body["hair_color"]
    new_character.eye_color = body["eye_color"]
    new_character.homeworld_id = body["homeworld_id"]
    new_character.species_id = body["species_id"]

    db.session.add(new_character)
    db.session.commit()

    return jsonify(new_character.serialize())

@api.route('/characters', methods=['GET'])
def get_all_characters():
    characters = Character.query.all()
    characters_serialized = [character.serialize() for character in characters]
    return jsonify(characters_serialized), 200

@api.route('/characters/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({"msg": "Character not found"}), 404
    return jsonify(character.serialize()), 200

@api.route('/planets', methods=['POST'])
def add_new_planet():
    body = request.json
    if body is None:
        return jsonify({"msg": "information is required"}), 400
    if body["name"] is None:
        return jsonify({"msg": "name is required"}), 400
    if body["population"] is None:
        return jsonify({"msg": "population is required"}), 400
    new_planet = Planet()
    new_planet.name = body["name"]
    new_planet.population = body["population"]

    db.session.add(new_planet)
    db.session.commit()

    return jsonify(new_planet.serialize())

@api.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    planets_serialized = [planet.serialize() for planet in planets]
    return jsonify(planets_serialized), 200

@api.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

@api.route('/species', methods=['POST'])
def add_new_species():
    body = request.json
    if body is None:
        return jsonify({"msg": "information is required"}), 400
    if body["name"] is None:
        return jsonify({"msg": "name is required"}), 400
    if body["average_height"] is None:
        return jsonify({"msg": "average height is required"}), 400
    if body["average_lifespan"] is None:
        return jsonify({"msg": "average lifespan is required"}), 400
    if body["language"] is None:
        return jsonify({"msg": "language is required"}), 400
    new_species = Species()
    new_species.name = body["name"]
    new_species.average_height = body["average_height"]
    new_species.average_lifespan = body["average_lifespan"]
    new_species.language = body["language"]

    db.session.add(new_species)
    db.session.commit()

    return jsonify(new_species.serialize()), 201

@api.route('/species', methods=['GET'])
def get_all_species():
    species = Species.query.all()
    species_serialized = [species.serialize() for species in species]
    return jsonify(species_serialized), 200

@api.route('/species/<int:species_id>', methods=['GET'])
def get_species(species_id):
    species = Species.query.get(species_id)
    if species is None:
        return jsonify({"msg": "Species not found"}), 404
    return jsonify(species.serialize()), 200

@api.route('/users/<int:user_id>/favorites/characters/<int:character_id>', methods=['POST'])
def add_favorite_character(user_id, character_id):
    user = User.query.get(user_id)
    character = Character.query.get(character_id)

    if user is None or character is None:
        return jsonify({"msg": "User or Character not found"}), 404

    if character in user.favorite_characters:
        return jsonify({"msg": "Character already in favorites"}), 400

    user.favorite_characters.append(character)
    db.session.commit()

    return jsonify(user.serialize()), 200

@api.route('/users/<int:user_id>/favorites/characters/<int:character_id>', methods=['DELETE'])
def remove_favorite_character(user_id, character_id):
    user = User.query.get(user_id)
    character = Character.query.get(character_id)

    if user is None or character is None:
        return jsonify({"msg": "User or Character not found"}), 404

    if character not in user.favorite_characters:
        return jsonify({"msg": "Character not in favorites"}), 400

    user.favorite_characters.remove(character)
    db.session.commit()

    return jsonify(user.serialize()), 200

@api.route('/users/<int:user_id>/favorites/planets/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)

    if user is None or planet is None:
        return jsonify({"msg": "User or Planet not found"}), 404

    if planet in user.favorite_planets:
        return jsonify({"msg": "Planet already in favorites"}), 400

    user.favorite_planets.append(planet)
    db.session.commit()

    return jsonify(user.serialize()), 200

@api.route('/users/<int:user_id>/favorites/planets/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(user_id, planet_id):
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)

    if user is None or planet is None:
        return jsonify({"msg": "User or Planet not found"}), 404

    if planet not in user.favorite_planets:
        return jsonify({"msg": "Planet not in favorites"}), 400

    user.favorite_planets.remove(planet)
    db.session.commit()

    return jsonify(user.serialize()), 200

@api.route('/users/<int:user_id>/favorites/species/<int:species_id>', methods=['POST'])
def add_favorite_species(user_id, species_id):
    user = User.query.get(user_id)
    species = Species.query.get(species_id)

    if user is None or species is None:
        return jsonify({"msg": "User or Species not found"}), 404

    if species in user.favorite_species:
        return jsonify({"msg": "Species already in favorites"}), 400

    user.favorite_species.append(species)
    db.session.commit()

    return jsonify(user.serialize()), 200

@api.route('/users/<int:user_id>/favorites/species/<int:species_id>', methods=['DELETE'])
def remove_favorite_species(user_id, species_id):
    user = User.query.get(user_id)
    species = Species.query.get(species_id)

    if user is None or species is None:
        return jsonify({"msg": "User or Species not found"}), 404

    if species not in user.favorite_species:
        return jsonify({"msg": "Species not in favorites"}), 400

    user.favorite_species.remove(species)
    db.session.commit()

    return jsonify(user.serialize()), 200