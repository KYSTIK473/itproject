from pandas import Series, DataFrame, concat
from joblib import load
from numpy.typing import ArrayLike
from warnings import filterwarnings

filterwarnings('ignore')
columns = ['release_date', 'budget', 'popularity', 'runtime',
           'vote_average', 'adult', 'original_language', 'genres', 'spoken_languages', 'production_companies', 'status',
           'crew', 'cast']
TO_SCALE = ['budget', 'popularity', 'runtime', 'vote_average', 'release_date']
TO_VECTORIZE = ['genres', 'spoken_languages', 'production_companies']
TO_PROCESS = ['staff', 'cast']
TOP_COUNTRIES = ['en', 'fr', 'it', 'ja', 'de', 'es', 'ru', 'hi', 'ko', 'zh']


def to_str(x):
    return ' '.join(map(lambda s: '_'.join(s.lower().split(' ')), x))


def process_movie(movie_row: Series) -> ArrayLike:
    """
    movie_row содержит пары индекс-значение:
        budget: int,
        original_language: str,
        popularity: float,
        release_date: int (timestamp),
        runtime: int,
        status: str,
        vote_average: float,
        genres: list[str],
        spoken_languages: list[str],
        production_companies: list[str],
        adult: bool,
        crew: list[str],
        cast: list[str]
    """
    vector = movie_row[columns]

    for scaler_name in TO_SCALE:
        scaler = load(f'./scalers/{scaler_name}_scaler.save')
        value = vector[scaler_name]
        vector[scaler_name] = scaler.transform([[value]])[0, 0]

    for country in TOP_COUNTRIES:
        vector[f'is_from_{country}'] = int(vector['original_language'] == country)
    vector = vector.drop('original_language')

    vector['adult'] = int(vector['adult'])
    vector['not_adult'] = 1 - vector['adult']

    vector['released'] = int(vector['status'] == 'Released')
    vector['in_production'] = int(vector['status'] in ['Post Production', 'In Production', 'Planned'])
    vector = vector.drop('status')

    vector['genres'] = to_str(vector['genres'])
    vector['spoken_languages'] = to_str(vector['spoken_languages'])
    vector['production_companies'] = to_str(vector['production_companies'])

    for vectorizer_name in TO_VECTORIZE:
        vectorizer = load(f'./vectorizers/{vectorizer_name}_vectorizer.save')
        vectorized = DataFrame(vectorizer.transform([vector[vectorizer_name]]).todense(),
                               columns=vectorizer.get_feature_names_out()).iloc[0]
        vector = concat([vector.drop(vectorizer_name), vectorized])

    vector['staff'] = to_str(vector['crew'])
    vector = vector.drop('crew')
    vector['cast'] = to_str(vector['cast'])
    for vectorizer_name in TO_PROCESS:
        vectorizer = load(f'./vectorizers/{vectorizer_name}_vectorizer.save')
        vectorized = DataFrame(vectorizer.transform([vector[vectorizer_name]]).todense(),
                               columns=vectorizer.get_feature_names_out()).iloc[0]
        vector = concat([vector.drop(vectorizer_name), vectorized])

    return vector.astype('float32')