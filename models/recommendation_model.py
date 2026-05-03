import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from scipy.sparse import hstack, csr_matrix
import numpy as np

path = "./data/df_numeric.parquet"

df = pd.read_parquet(path)
df = df.dropna().reset_index(drop=True)

# OneHot en SPARSE (pas de .toarray() !)
onehot_director = OneHotEncoder(handle_unknown='ignore')
directors_encoded = onehot_director.fit_transform(df[['nconst_director']])  # sparse

onehot_actors = OneHotEncoder(handle_unknown='ignore')
actor_columns = ['actor1', 'actor2', 'actor3', 'actor4', 'actor5', 'actor6', 'actor7']
actors_encoded = onehot_actors.fit_transform(df[actor_columns])  # sparse

onehot_genres = OneHotEncoder(handle_unknown='ignore')
genre_columns = ['genre1', 'genre2']
genres_encoded = onehot_genres.fit_transform(df[genre_columns])  # sparse

# Numériques → sparse aussi
numeric_features = df[['averageRating', 'startYear', 'runtimeMinutes', 'popularity']]
scaler = StandardScaler()
numeric_scaled = csr_matrix(scaler.fit_transform(numeric_features))  # sparse

# Overview features → sparse
overview_columns = [
    col for col in df.columns
    if col not in [
        'titleId', 'nconst_director', 'original_actors', 'Director_name',
        'production_companies_name', 'title', 'overview', 'main_genre',
        'poster_path', 'backdrop_path', 'original_overview'
    ] + actor_columns + genre_columns + list(numeric_features.columns)
]
overview_features = csr_matrix(df[overview_columns].values)  # sparse

# hstack sparse → PAS de np.hstack !
combined_features = hstack([
    numeric_scaled,
    directors_encoded,
    actors_encoded,
    genres_encoded,
    overview_features
])  # reste sparse → ~10× moins de RAM

title_index = pd.Series(df.index, index=df['titleId']).drop_duplicates()

def get_similar_movies(title_id, n=10):
    if title_id not in title_index:
        return []

    idx = title_index[title_id]

    # Vecteur sparse du film (1 × features)
    movie_vector = combined_features[idx]

    # cosine_similarity supporte nativement les sparse matrices
    sim_scores = cosine_similarity(movie_vector, combined_features)[0]

    similar_indices = sim_scores.argsort()[::-1][1:n+1]
    return df.iloc[similar_indices]['titleId'].tolist()