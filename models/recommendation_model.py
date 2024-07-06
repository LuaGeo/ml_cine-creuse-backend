import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import numpy as np
from scipy.sparse import hstack, csr_matrix
import scipy.sparse

def process_chunk(chunk):
    # Drop NaN values
    chunk = chunk.dropna()

    # One-Hot Encoding for Directors
    directors_encoded = onehot_encoder.fit_transform(chunk[['nconst_director']]).toarray()

    # One-Hot Encoding for Actors
    actors_encoded = onehot_encoder.fit_transform(chunk[actor_columns]).toarray()

    # One-Hot Encoding for Genres
    genres_encoded = onehot_encoder.fit_transform(chunk[genre_columns]).toarray()

    # Standardize numerical features
    numeric_features = chunk[['averageRating', 'startYear', 'runtimeMinutes', 'popularity']]
    numeric_features_scaled = scaler.fit_transform(numeric_features)

    # Convert to sparse matrix
    numeric_features_sparse = csr_matrix(numeric_features_scaled)

    # Extract overview features (already processed and included in df)
    overview_features = chunk[overview_columns].values
    overview_features_sparse = csr_matrix(overview_features)


    # Combine all features
    combined_features_chunk = hstack([numeric_features_sparse, directors_encoded, actors_encoded, genres_encoded, overview_features_sparse])
    
    return combined_features_chunk, chunk['title'].values

def process_data_in_chunks(df, chunk_size=10000):
    combined_features = []
    titles = []

    # Split the DataFrame into chunks
    for start in range(0, len(df), chunk_size):
        end = min(start + chunk_size, len(df))
        chunk = df.iloc[start:end]
        chunk_combined_features, chunk_titles = process_chunk(chunk)
        combined_features.append(chunk_combined_features)
        titles.extend(chunk_titles)
    
    # Concatenate all chunk results
    combined_features = scipy.sparse.vstack(combined_features)
    return combined_features, titles

# Initialize encoders and scalers
onehot_encoder = OneHotEncoder()
scaler = StandardScaler()

# Specify the columns to be encoded
actor_columns = ['actor1', 'actor2', 'actor3', 'actor4', 'actor5', 'actor6', 'actor7']
genre_columns = ['genre1', 'genre2']

# Specify the overview columns
overview_columns = ['overview1', 'overview2']  # Replace with your actual overview columns

# Process the data in chunks
link = "https://raw.githubusercontent.com/LuaGeo/test_ml_cine-creuse-backend/main/data/data_cleaned_ml_with_original_columns.parquet"
df = pd.read_parquet(link)  # Load the entire Parquet file
combined_features, titles = process_data_in_chunks(df)

# Calculate the cosine similarity matrix
similarity_matrix = cosine_similarity(combined_features)

# Create a DataFrame for the similarity matrix
sim_matrix_df = pd.DataFrame(similarity_matrix, index=titles, columns=titles)
