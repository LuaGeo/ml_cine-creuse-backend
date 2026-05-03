import os
import requests
from flask import current_app as app
from flask import jsonify, request
from models.recommendation_model import df, get_similar_movies

api_key = os.getenv("TMDB_API_KEY")


def get_movie_details_from_df(row):
    return {
        "titleId": row['titleId'],
        "averageRating": row['averageRating'],
        "runtimeMinutes": row['runtimeMinutes'],
        "startYear": row['startYear']
    }

def get_splash_movies():
    splash_movies = df.sample(5)
    movies = [get_movie_details_from_df(row) for _, row in splash_movies.iterrows()]
    return jsonify(movies)

def get_recommendations(title_id, api_key, items=20):
    try:
        similar_title_ids = get_similar_movies(title_id, n=items)

        if not similar_title_ids:
            return None

        recommendations = []
        for idx in similar_title_ids:
            movie_details_df = df.loc[df['titleId'] == idx]
            if not movie_details_df.empty:
                basic_details = get_movie_details_from_df(movie_details_df.iloc[0])
                additional_details = get_movie_details_from_api(idx, api_key)
                if additional_details:
                    basic_details.update(additional_details)
                recommendations.append(basic_details)

        return recommendations

    except KeyError:
        return None

def get_movie_details_from_api(titleId, api_key):
    url = f"https://api.themoviedb.org/3/movie/{titleId}?api_key={api_key}&language=fr&append_to_response=credits"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        movie_details = {
            "title": data.get("title"),
            "overview": data.get("overview"),
            "main_genre": data.get("genres")[0]['name'] if data.get("genres") else None,
            "poster_path": f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}" if data.get('poster_path') else None,
            "backdrop_path": f"https://image.tmdb.org/t/p/w500{data.get('backdrop_path')}" if data.get('backdrop_path') else None
        }
        return movie_details
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def get_movies_by_genre(genre, df):
    genre_movies = df[df['main_genre'].str.contains(genre, case=False, na=False)]
    movies = [get_movie_details_from_df(row) for _, row in genre_movies.iterrows()]
    return movies

def setup_recommendations_routes(app):
    @app.route('/recommendations/<title_id>', methods=['GET'])
    def recommendations(title_id):
        if not api_key:
            return jsonify({'error': 'TMDB API key not available'}), 500

        app.logger.debug(f'Recommendations endpoint accessed with title_id: {title_id}')
        # ← plus de sim_matrix_df passé en paramètre
        recommended_movies = get_recommendations(title_id, api_key, 20)
        if recommended_movies is None or not recommended_movies:
            return jsonify({'error': 'Movie title not found or no recommendations available'}), 404

        return jsonify(recommended_movies)

    @app.route('/splash-movies', methods=['GET'])
    def splash_movies():
        return get_splash_movies()

    @app.route('/movie-details/<titleId>', methods=['GET'])
    def movie_details(titleId):
        if not api_key:
            return jsonify({'error': 'TMDB API key not available'}), 500

        movie = get_movie_details_from_api(titleId, api_key)
        if movie is None:
            return jsonify({'error': 'Movie not found'}), 404
        return jsonify(movie)

    @app.route('/movies-by-genre/<genre>', methods=['GET'])
    def movies_by_genre(genre):
        movies = get_movies_by_genre(genre, df)
        return jsonify(movies)

    @app.route('/genres', methods=['GET'])
    def genres():
        genres = df['main_genre'].unique().tolist()
        return jsonify(genres)

    @app.route('/search', methods=['GET'])
    def search_movies():
        query = request.args.get('query', '')
        if not query:
            return jsonify([])

        search_results = df[df['title'].str.contains(query, case=False, na=False)]
        results = search_results.head(10).to_dict(orient='records')
        return jsonify(results)