import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import numpy as np

path = "./data/df_numeric.parquet"

# ---- Chargement et préparation (au démarrage, mais sans la matrice N×N) ----
df = pd.read_parquet(path)
df = df.dropna()

onehot_encoder_director = OneHotEncoder(handle_unknown='ignore')
directors_encoded = onehot_encoder_director.fit_transform(df[['nconst_director']]).toarray()

onehot_encoder_actors = OneHotEncoder(handle_unknown='ignore')
actor_columns = ['actor1', 'actor2', 'actor3', 'actor4', 'actor5', 'actor6', 'actor7']
actors_encoded = onehot_encoder_actors.fit_transform(df[actor_columns]).toarray()

onehot_encoder_genres = OneHotEncoder(handle_unknown='ignore')
genre_columns = ['genre1', 'genre2']
genres_encoded = onehot_encoder_genres.fit_transform(df[genre_columns]).toarray()

numeric_features = df[['averageRating', 'startYear', 'runtimeMinutes', 'popularity']]
scaler = StandardScaler()
numeric_features_scaled = scaler.fit_transform(numeric_features)

overview_columns = [
    col for col in df.columns
    if col not in [
        'titleId', 'nconst_director', 'original_actors', 'Director_name',
        'production_companies_name', 'title', 'overview', 'main_genre',
        'poster_path', 'backdrop_path', 'original_overview'
    ] + actor_columns + genre_columns + list(numeric_features.columns)
]
overview_features = df[overview_columns].values

# Matrice de features combinées (N × features) — beaucoup plus légère que N×N
combined_features = np.hstack([
    numeric_features_scaled,
    directors_encoded,
    actors_encoded,
    genres_encoded,
    overview_features
])

# Index titleId → position dans le DataFrame
title_index = pd.Series(df.index, index=df['titleId']).drop_duplicates()

# ---- Fonction de recommandation à la demande ----
def get_similar_movies(title_id, n=10):
    """Calcule la similarité uniquement pour le film demandé."""
    if title_id not in title_index:
        return []

    idx = title_index[title_id]

    # Vecteur du film cible (1 × features)
    movie_vector = combined_features[idx].reshape(1, -1)

    # Similarité de CE film vs tous les autres (1 × N) — pas N×N !
    sim_scores = cosine_similarity(movie_vector, combined_features)[0]

    # Top N films les plus similaires (en excluant le film lui-même)
    similar_indices = sim_scores.argsort()[::-1][1:n+1]

    return df.iloc[similar_indices]['titleId'].tolist()