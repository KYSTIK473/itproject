import numpy as np
import h5py

MATRIX_PATH = 'D:\it purple\ITproject\itproject-backend_old\ML\similarity_matrix.h5'
MATRIX_DATASET_NAME = 'similarities'
INDEX_GROUP_NAME = 'index'
ARRAY_DATASET_NAME = 'movie_id'


def get_n_predictions(movie_id: int, n: int, path: str = MATRIX_PATH,
                     index_dataset_name: str = ARRAY_DATASET_NAME,
                     matrix_dataset_name: str = MATRIX_DATASET_NAME,
                     group_name: str = INDEX_GROUP_NAME) -> np.ndarray:
    with h5py.File(path, 'r') as hf:
        movie_index = hf[group_name][str(movie_id)][()]
        cosine_vector = hf[matrix_dataset_name][movie_index]
        indices = hf[index_dataset_name][:]

        return indices[cosine_vector.argsort()[::-1]][1:n + 1]
