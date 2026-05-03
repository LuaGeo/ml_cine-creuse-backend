# precompute_recommendations.py
# à faire tourner une seule fois pour pré-calculer les recommandations, puis les stocker dans un JSON pour un accès rapide dans l'API

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from scipy.sparse import hstack, csr_matrix
import json

path = "./data/df_numeric.parquet"
df = pd.read_parquet(path)
df = df.dropna().reset_index(drop=True)

print(f"Films : {len(df)}")

# Même preprocessing qu'avant
onehot_director = OneHotEncoder(handle_unknown='ignore')
directors_encoded = onehot_director.fit_transform(df[['nconst_director']])

onehot_actors = OneHotEncoder(handle_unknown='ignore')
actor_columns = ['actor1','actor2','actor3','actor4','actor5','actor6','actor7']
actors_encoded = onehot_actors.fit_transform(df[actor_columns])

onehot_genres = OneHotEncoder(handle_unknown='ignore')
genre_columns = ['genre1', 'genre2']
genres_encoded = onehot_genres.fit_transform(df[genre_columns])

numeric_features = df[['averageRating', 'startYear', 'runtimeMinutes', 'popularity']]
scaler = StandardScaler()
numeric_scaled = csr_matrix(scaler.fit_transform(numeric_features))

overview_columns = [
    col for col in df.columns
    if col not in [
        'titleId', 'nconst_director', 'original_actors', 'Director_name',
        'production_companies_name', 'title', 'overview', 'main_genre',
        'poster_path', 'backdrop_path', 'original_overview'
    ] + actor_columns + genre_columns + list(numeric_features.columns)
]
overview_features = csr_matrix(df[overview_columns].values)

combined_features = hstack([
    numeric_scaled, directors_encoded, actors_encoded, genres_encoded, overview_features
])

title_index = pd.Series(df.index, index=df['titleId']).drop_duplicates()

# Précalcule top 20 reco pour chaque film
print("Calcul des recommandations...")
recommendations = {}
total = len(df)

for i, title_id in enumerate(df['titleId']):
    if i % 100 == 0:
        print(f"{i}/{total}...")
    
    idx = title_index[title_id]
    movie_vector = combined_features[idx]
    sim_scores = cosine_similarity(movie_vector, combined_features)[0]
    similar_indices = sim_scores.argsort()[::-1][1:21]  # top 20
    recommendations[str(title_id)] = df.iloc[similar_indices]['titleId'].tolist()

# Sauvegarde
with open("data/recommendations_lookup.json", "w") as f:
    json.dump(recommendations, f)

print(f"✅ Sauvegardé : {len(recommendations)} films")