# Flask user routes

from flask import request, jsonify
from models.User import register_user, authenticate_user, add_favorite_movie, get_favorite_movies, delete_favorite_movie, check_favorite_status


def setup_user_routes(app):
    @app.route('/register', methods=['POST'])
    def register():
        data = request.json
        response = register_user(data)
        return jsonify(response)


    @app.route('/login', methods=['POST'])
    def login():
        data = request.json
        response = authenticate_user(data)
        if response.get("status") == 401 or response.get("status") == 400:
            return jsonify({"error": response["error"]}), response["status"]
        return jsonify(response)
    
def setup_favorite_movies_routes(app):
    @app.route('/favorites', methods=['POST'])
    def add_favorite():
        data = request.json
        print(f"Received data: {data}")
        if 'movieId' not in data or 'userId' not in data:
            return {"error": "Missing userId or movieId"}, 400
        response, status = add_favorite_movie(data)
        return jsonify(response), status

    @app.route('/favorites/list/<userId>', methods=['GET'])
    def get_favorites(userId):
        if not userId:
            return jsonify({"error": "Missing userId"}), 400
        
        response, status = get_favorite_movies({"userId": userId})
        return jsonify(response), status

    @app.route('/favorites', methods=['DELETE'])
    def delete_favorite():
        data = request.json
        print(f"Received data: {data}")
        response, status = delete_favorite_movie(data)
        return jsonify(response), status
    
    @app.route('/favorites', methods=['GET'])
    def get_favorite_status():
        data = {
            "userId": request.args.get('userId'),
            "movieId": request.args.get('movieId')
        }
        response, status = check_favorite_status(data)
        return jsonify(response), status
