import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import numpy as np
import requests
import io


# url = "https://raw.githubusercontent.com/LuaGeo/ml_cine-creuse-backend/main/data/df_numeric.parquet"
path = "./data/df_numeric.parquet"

# response = requests.get(url)
# response.raise_for_status()

# df = pd.read_parquet(io.BytesIO(response.content)) #io.BytesIO(response.content)
# df = pd.read_csv('/Users/lua/wild/project2/test_ml_cine-creuse-backend/data/data_cleaned_ml_with_original_columns.csv')

df = pd.read_parquet(path)
df = df.dropna()

# One-Hot Encoding for Directors
onehot_encoder = OneHotEncoder()
directors_encoded = onehot_encoder.fit_transform(df[['nconst_director']]).toarray()

# One-Hot Encoding for Actors
actor_columns = ['actor1', 'actor2', 'actor3', 'actor4', 'actor5', 'actor6', 'actor7']
actors_encoded = onehot_encoder.fit_transform(df[actor_columns]).toarray()

# One-Hot Encoding for Genres
genre_columns = ['genre1', 'genre2']
genres_encoded = onehot_encoder.fit_transform(df[genre_columns]).toarray()

# Standardize numerical features
numeric_features = df[['averageRating', 'startYear', 'runtimeMinutes', 'popularity']]
scaler = StandardScaler()
numeric_features_scaled = scaler.fit_transform(numeric_features)

# Extract overview features (already processed and included in df)
overview_columns = [col for col in df.columns if col not in ['titleId',  'nconst_director',   'original_actors', 'Director_name',  'production_companies_name', 'title', 'overview', 'main_genre', 'poster_path', 'backdrop_path', 'original_overview'] + actor_columns + genre_columns + list(numeric_features.columns)]
overview_features = df[overview_columns].values

# Combine all features
combined_features = np.hstack([numeric_features_scaled, directors_encoded, actors_encoded, genres_encoded, overview_features])

# Calculate the cosine similarity matrix
similarity_matrix = cosine_similarity(combined_features)

sim_matrix_df = pd.DataFrame(similarity_matrix, index=df['titleId'], columns=df['titleId'])