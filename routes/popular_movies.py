from flask import jsonify
from flask import current_app as app
from models.recommendation_model import df
import requests
import os


TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def fetch_tmdb_data(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def setup_popular_movies_routes(app):
    @app.route('/popular-movies', methods=['GET'])
    def get_popular_movies():
        popular_movies = df.sort_values(by='popularity', ascending=False).head(5)
        popular_movies_list = []

        for index, row in popular_movies.iterrows():
            tmdb_id = row['titleId']
            tmdb_data = fetch_tmdb_data(tmdb_id)
            if tmdb_data:
                popular_movies_list.append({
                    'id': tmdb_data['id'],
                    'title': tmdb_data['title'],
                    'backdrop_path': tmdb_data['backdrop_path'],
                    'poster_path': tmdb_data['poster_path']
                })

        return jsonify(popular_movies_list)

    @app.route('/top-movies', methods=['GET'])
    def get_top_movies():
        top = df.sort_values(by='averageRating', ascending=False).head(20)
        return jsonify(top[['titleId', 'averageRating']].to_dict(orient='records'))
    
    
