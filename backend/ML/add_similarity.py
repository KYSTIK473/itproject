from numpy.typing import ArrayLike
import h5py

MATRIX_PATH = 'similarity_matrix.h5'
MATRIX_DATASET_NAME = 'similarities'
INDEX_GROUP_NAME = 'index'


def add_similarity(movie_id: int, cosine_vector: ArrayLike, path: str = MATRIX_PATH,
                   dataset_name: str = MATRIX_DATASET_NAME, group_name: str = INDEX_GROUP_NAME) -> None:
    with h5py.File(path, 'r') as hf:
        similarities = hf[dataset_name]
        index_group = hf[group_name]
        n_movies = similarities.shape[0]

        similarities.resize((n_movies + 1, n_movies + 1))
        similarities[n_movies, :n_movies] = cosine_vector
        similarities[:n_movies, n_movies] = cosine_vector
        similarities[n_movies, n_movies] = 1.0

        index_group[str(movie_id)] = n_movies
