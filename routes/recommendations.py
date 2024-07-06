import os
import requests
from flask import current_app as app
from flask import jsonify, request
from models.recommendation_model import df, sim_matrix_df

def get_movie_details_from_df(row):
    return {
        "titleId": row['titleId'],
        "title": row['title'],  # French title
        "averageRating": row['averageRating'],
        "runtimeMinutes": row['runtimeMinutes'],
        "startYear": row['startYear'],
        "overview": row['original_overview'],
        "main_genre": row['main_genre'],
        "poster_path": row.get('poster_path'),
        "backdrop_path": row.get('backdrop_path')
    }

def get_splash_movies():
    splash_movies = df.sample(5)
    movies = [get_movie_details_from_df(row) for _, row in splash_movies.iterrows()]
    return jsonify(movies)

def get_recommendations(movie_title, sim_matrix, df, items=20):
    try:
        sim_scores = sim_matrix[movie_title]  # Get similarity scores for the given movie with all movies
        sorted_sim_scores = sim_scores.sort_values(ascending=False)  # Sort the movies based on the similarity scores
        top_items = sorted_sim_scores.iloc[1:items+1]  # exclude the first item since it's the movie itself

        recommendations = []
        for title in top_items.index:
            movie_details = df.loc[df['title'] == title]
            recommendations.append(get_movie_details_from_df(movie_details.iloc[0]))

        return recommendations

    except KeyError:
        return None

def get_movie_details(title_id, df):
    try:
        movie_details = df.loc[df['titleId'] == title_id].iloc[0]
        return get_movie_details_from_df(movie_details)
    except IndexError:
        return None

def get_movies_by_genre(genre, df):
    genre_movies = df[df['main_genre'].str.contains(genre, case=False, na=False)]
    movies = [get_movie_details_from_df(row) for _, row in genre_movies.iterrows()]
    return movies

def setup_recommendations_routes(app):
    @app.route('/recommendations', methods=['GET'])
    def recommendations():
        movie_title = request.args.get('title')
        if not movie_title:
            return jsonify({'error': 'Missing title parameter'}), 400

        recommended_movies = get_recommendations(movie_title, sim_matrix_df, df)
        if recommended_movies is None:
            return jsonify({'error': 'Movie title not found in database'}), 404

        return jsonify(recommended_movies)

    @app.route('/splash-movies', methods=['GET'])
    def splash_movies():
        return get_splash_movies()

    @app.route('/movie-details/<title_id>', methods=['GET'])
    def movie_details(title_id):
        movie = get_movie_details(title_id, df)
        if movie is None:
            return jsonify({'error': 'Movie not found'}), 404
        return jsonify(movie)

    @app.route('/movies-by-genre/<genre>', methods=['GET'])
    def movies_by_genre(genre):
        movies = get_movies_by_genre(genre, df)
        return jsonify(movies)
    
    @app.route('/genres', methods=['GET'])
    def genres():
        genres = df['main_genre'].unique().tolist()  # Assuming 'main_genre' column exists in your DataFrame
        return jsonify(genres)
    
    @app.route('/search', methods=['GET'])
    def search_movies():
        query = request.args.get('query', '')
        if not query:
            return jsonify([])

        # Perform a case-insensitive search for the query in the 'title' column
        search_results = df[df['title'].str.contains(query, case=False, na=False)]
        
        results = search_results.head(10).to_dict(orient='records')  # Limit to 10 results

        return jsonify(results)

