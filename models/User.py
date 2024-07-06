# Data models

from db import mongo
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from bson import ObjectId


def register_user(data):
    # Validate data here (ensure username, email, and password are provided)
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return {"error": "Missing information"}

    # Check if the user already exists
    if mongo.db.users.find_one({"username": data['username']}):
        return {"error": "Username already exists"}
    if mongo.db.users.find_one({"email": data['email']}):
        return {"error": "Email already exists"}

    # Generate a unique token for the user
    token = str(uuid.uuid4())

    # Hash the password
    hashed_password = generate_password_hash(data['password'])

    # Create the user document to store in MongoDB
    user_document = {
        "username": data['username'],
        "email": data['email'],
        "password": hashed_password,
        "token": token,
        "favorite_movies": []
    }

    # Insert the user document into the database
    mongo.db.users.insert_one(user_document)
    
    return {"message": "User registered successfully", "username": data['username']}

def authenticate_user(data):
    if 'username' not in data or 'password' not in data:
        return {"error": "Missing username or password", "status": 400}

    user = mongo.db.users.find_one({"username": data['username']})
    if user and check_password_hash(user['password'], data['password']):
        user_id = str(user['_id'])
        return {"message": "Login successful", "username": user['username'], "token": user['token'], "userId": user_id}
    else:
        return {"error": "Invalid credentials", "status": 401}

def user_exists(user_id):
    try:
        user_id_obj = ObjectId(user_id)
        return mongo.db.users.count_documents({"_id": user_id_obj}) > 0
    except:
        return False

def add_favorite_movie(data):
    if 'userId' not in data or 'movieId' not in data:
        return {"error": "Missing userId or movieId"}, 400
    
    # Check if the user exists
    if not user_exists(data['userId']):
        return {"error": "Invalid userId"}, 404

    user_id_obj = ObjectId(data['userId'])
    
    # Check if the movie already exists in the user's favorites
    if mongo.db.users.count_documents({
        "_id": user_id_obj,
        "favorite_movies": data['movieId']
    }) > 0:
        return {"error": "Movie already added to favorites"}, 409

    # Add the movie ID to the user's favorite movies list
    mongo.db.users.update_one(
        {"_id": user_id_obj},
        {"$push": {"favorite_movies": data['movieId']}}
    )
    
    return {"message": "Favorite movie added"}, 201

def get_favorite_movies(data):
    if 'userId' not in data:
        return {"error": "Missing userId"}, 400

    user_id_obj = ObjectId(data['userId'])

    user = mongo.db.users.find_one({"_id": user_id_obj}, {"favorite_movies": 1})
    if user and "favorite_movies" in user:
        favorite_movies = user["favorite_movies"]
        return {"favoriteMovies": favorite_movies}, 200
    else:
        return {"favoriteMovies": []}, 200

def delete_favorite_movie(data):
    if 'userId' not in data or 'movieId' not in data:
        return {"error": "Missing userId or movieId"}, 400

    user_id_obj = ObjectId(data['userId'])

    result = mongo.db.users.update_one(
        {"_id": user_id_obj},
        {"$pull": {"favorite_movies": data['movieId']}}
    )
    
    if result.modified_count:
        return {"message": "Favorite movie deleted"}, 200
    else:
        return {"error": "Favorite movie not found"}, 404
    

def check_favorite_status(data):
    if 'userId' not in data or 'movieId' not in data:
        return {"error": "Missing userId or movieId"}, 400

    user_id_obj = ObjectId(data['userId'])

    is_favorite = mongo.db.users.count_documents({
        "_id": user_id_obj,
        "favorite_movies": data['movieId']
    }) > 0

    return {"isFavorite": is_favorite}, 200
