document.addEventListener('DOMContentLoaded', async () => {
    const movieDetailContainer = document.getElementById('movie-detail-container');
    const authPromptSection = document.getElementById('auth-prompt-section');
    const similarMoviesContainer = document.getElementById('similar-movies-container');

    const DEFAULT_POSTER_PLACEHOLDER = 'https://via.placeholder.com/300x450?text=No+Poster';
    const LOADING_POSTER_PLACEHOLDER = 'https://via.placeholder.com/300x450?text=Loading+Poster...';
    const ERROR_LOADING_POSTER_PLACEHOLDER = 'https://via.placeholder.com/300x450?text=Error+Loading+Poster';

    const movieItemConfig = {
        posterAPIBaseURL: 'http://127.0.0.1:8000',
        placeholderImage: 'https://via.placeholder.com/120x180?text=No+Poster',
    };

    const urlParams = new URLSearchParams(window.location.search);
    const movieId = urlParams.get('film_id');

    if (!movieId || isNaN(movieId)) {
        movieDetailContainer.innerHTML = '<p>Неверный ID фильма.</p>';
        return;
    }

    const escapeHTML = (str) => {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    };

    const createMovieElement = (movie) => {
        if (!movie || typeof movie !== 'object') {
            console.error("Некорректные данные фильма переданы в createMovieElement:", movie);
            return null;
        }

        const element = document.createElement('article');
        element.className = 'movie-item';

        const title = escapeHTML(movie.title || 'Без названия');
        const year = movie.release_date ? new Date(movie.release_date).getFullYear() : 'N/A';
        const overview = (movie.overview && typeof movie.overview === 'string')
            ? escapeHTML(movie.overview.slice(0, 150) + (movie.overview.length > 150 ? '...' : ''))
            : 'Описание отсутствует';

        const currentMovieId = movie.movie_id || movie.film_id;
        if (!currentMovieId) {
            console.warn("Фильм без ID в createMovieElement:", movie);
            return null;
        }

        const detailPageUrl = `movie_detail.html?film_id=${currentMovieId}`;
        const posterImgId = `poster-img-similar-${currentMovieId}`;

        element.innerHTML = `
            <a href="${detailPageUrl}" class="movie-link">
                <img id="${posterImgId}" src="${movieItemConfig.placeholderImage}" alt="Постер ${title}" loading="lazy">
                <div class="movie-info">
                    <h2>${title}</h2>
                    <div class="meta">
                        <p class="year">${year}</p>
                        ${movie.vote_average ? `<p class="rating">★ ${Number(movie.vote_average).toFixed(1)}</p>` : ''}
                    </div>
                    ${overview ? `<p class="overview">${overview}</p>` : ''}
                </div>
            </a>
        `;
        return element;
    };

    async function updatePosterAsync(movieIdForPoster, imgElementId) {
        const imgElement = document.getElementById(imgElementId);
        if (!imgElement) {
            // console.warn(`Элемент изображения с ID ${imgElementId} не найден.`);
            return; // Возвращаем Promise, который разрешится, если элемент не найден
        }

        try {
            const posterApiUrl = new URL(`${movieItemConfig.posterAPIBaseURL}/get_poster_link`);
            posterApiUrl.searchParams.append('film_id', String(movieIdForPoster));

            const response = await fetch(posterApiUrl.toString());
            if (!response.ok) {
                // console.warn(`Не удалось загрузить постер для фильма ID ${movieIdForPoster}. Статус: ${response.status}`);
                return; // Возвращаем Promise, который разрешится
            }
            const data = await response.json();
            if (data.poster_link && data.poster_link !== "N/A") {
                imgElement.src = data.poster_link;
            }
        } catch (error) {
            console.error(`Ошибка при обновлении постера для фильма ID ${movieIdForPoster}:`, error);
            // Ошибка здесь не должна прерывать Promise.all, если только это не критично
        }
    }

    async function checkAuthStatus() {
        try {
            const response = await fetch('http://127.0.0.1:8000/check_auth', {
                method: 'GET',
                credentials: 'include'
            });
            if (response.ok) {
                const data = await response.json();
                return data.is_authenticated === true;
            } else {
                try {
                    const errorData = await response.json();
                    console.warn('/check_auth non-OK response with JSON:', response.status, errorData);
                } catch (e) {
                    const textError = await response.text();
                    console.warn('/check_auth non-OK response, not JSON:', response.status, textError);
                }
                return false;
            }
        } catch (error) {
            console.error('Ошибка при вызове /check_auth:', error);
            return false;
        }
    }

    async function submitRating(ratingValue) {
        console.log('lof');
        if (!movieId) return;
        ratingFeedback.textContent = 'Отправка оценки...';
        const apiUrl = new URL('http://127.0.0.1:8000/like');
        apiUrl.searchParams.append('rating', String(ratingValue));
        apiUrl.searchParams.append('film_id', String(movieId));

        try {
            const response = await fetch(apiUrl.toString(), {
                method: 'POST',
                credentials: 'include'
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Оценка отправлена:', result);
                ratingFeedback.textContent = `Ваша оценка (${ratingValue}) сохранена!`;
            } else {
                let errorDetailMessage = 'Не удалось сохранить оценку.';
                let rawErrorDataOutput = `Статус ответа: ${response.status}. Нет дополнительных деталей от сервера.`;
                try {
                    const errorData = await response.json();
                    rawErrorDataOutput = JSON.stringify(errorData, null, 2);
                    if (errorData.detail) {
                        if (typeof errorData.detail === 'string') {
                            errorDetailMessage = errorData.detail;
                        } else if (Array.isArray(errorData.detail)) {
                            errorDetailMessage = 'Ошибка валидации данных:';
                            errorData.detail.forEach(err => {
                                const field = err.loc ? err.loc.join(' -> ') : 'неизвестное поле';
                                errorDetailMessage += `\n- Поле '${field}': ${err.msg}`;
                            });
                        }
                    } else if (Array.isArray(errorData)) {
                        errorDetailMessage = 'Ошибка валидации данных:';
                        errorData.forEach(err => {
                            const field = err.loc ? err.loc.join(' -> ') : 'неизвестное поле';
                            errorDetailMessage += `\n- Поле '${field}': ${err.msg}`;
                        });
                    } else if (typeof errorData === 'object' && errorData !== null) {
                        errorDetailMessage = Object.values(errorData).join('; ') || errorDetailMessage;
                    }
                } catch (e) {
                    console.error('Не удалось распарсить JSON ошибки, или тело ответа пустое:', e);
                    try {
                        const textError = await response.text();
                        if (textError) rawErrorDataOutput = textError;
                    } catch (textErr) { }
                }
                console.error(`Ошибка отправки оценки (статус ${response.status}): ${errorDetailMessage}\nДетали от сервера:\n${rawErrorDataOutput}`);
                const userFriendlyError = errorDetailMessage.includes('\n') ? errorDetailMessage.split('\n')[0] : errorDetailMessage;
                ratingFeedback.textContent = `Ошибка (${response.status}): ${userFriendlyError}`;
                permanentRating = 0;
                renderStars(currentRating, false);
            }
        } catch (error) {
            console.error('Сетевая ошибка при отправке оценки:', error);
            ratingFeedback.textContent = 'Сетевая ошибка при отправке оценки.';
            permanentRating = 0;
            renderStars(currentRating, false);
        }
    }

    let currentRating = 0;
    let permanentRating = 0;
    const MAX_STARS = 10;

    function renderStars(ratingToDisplay, isFixed = false) {
        if (!starRatingContainer) return;
        starRatingContainer.innerHTML = '';
        for (let i = 1; i <= MAX_STARS; i++) {
            const star = document.createElement('span');
            star.classList.add('star');
            star.textContent = '★';
            star.dataset.value = i;

            if (i <= ratingToDisplay) {
                star.classList.add('selected');
            }

            if (!isFixed) {
                star.addEventListener('mouseover', () => {
                    if (!permanentRating || currentRating !== permanentRating) {
                        renderStars(i, false);
                    }
                });
                star.addEventListener('mouseout', () => {
                    if (!permanentRating || currentRating !== permanentRating) {
                        renderStars(currentRating, false);
                    }
                });
                star.addEventListener('click', (event) => {
                    event.preventDefault();
                    currentRating = i;
                    permanentRating = i;
                    renderStars(currentRating, true);
                    submitRating(currentRating);
                });
            }
            starRatingContainer.appendChild(star);
        }
    }


    function showAuthPrompt() {
        starRatingSection.style.display = 'none';
        authPromptSection.style.display = 'block';
    }

    // ИЗМЕНЕННАЯ ФУНКЦИЯ: Функция для загрузки и отображения похожих фильмов (с параллельными запросами постеров)
    async function loadSimilarMovies(currentMovieId) {
        if (!similarMoviesContainer) {
            console.error('Контейнер для похожих фильмов (similar-movies-container) не найден.');
            return;
        }

        similarMoviesContainer.innerHTML = '<h3>Похожие фильмы</h3><p>Загрузка...</p>';

        try {
            const response = await fetch(`http://127.0.0.1:8000/get_similarity?film_id=${currentMovieId}`);
            if (!response.ok) {
                if (response.status === 404) {
                    similarMoviesContainer.innerHTML = '<h3>Похожие фильмы</h3><p>Похожие фильмы не найдены.</p>';
                } else {
                    similarMoviesContainer.innerHTML = `<h3>Похожие фильмы</h3><p>Ошибка загрузки: ${response.statusText}</p>`;
                }
                return;
            }
            const movies = await response.json();

            if (!Array.isArray(movies) || movies.length === 0) {
                similarMoviesContainer.innerHTML = '<h3>Похожие фильмы</h3><p>Похожие фильмы не найдены.</p>';
                return;
            }

            similarMoviesContainer.innerHTML = '<h3>Похожие фильмы</h3>';
            const listElement = document.createElement('div');
            listElement.className = 'movies-list similar-movies-grid';

            const posterUpdateTasksInfo = [];

            movies.forEach(movieData => {
                const moviePrepared = { ...movieData };
                if (movieData.film_id && !movieData.movie_id) {
                    moviePrepared.movie_id = movieData.film_id;
                }

                const movieElement = createMovieElement(moviePrepared);
                if (movieElement instanceof Node) {
                    listElement.appendChild(movieElement);

                    const posterId = moviePrepared.movie_id || moviePrepared.film_id;
                    if (posterId) {
                        posterUpdateTasksInfo.push({
                            id: String(posterId),
                            imgElementId: `poster-img-similar-${posterId}`
                        });
                    }
                }
            });

            similarMoviesContainer.appendChild(listElement);

            // Создаем массив промисов для параллельного выполнения
            const updatePromises = posterUpdateTasksInfo.map(task =>
                updatePosterAsync(task.id, task.imgElementId)
            );

            // Ожидаем завершения всех запросов на постеры
            await Promise.all(updatePromises);
            // console.log('Все постеры для похожих фильмов попытались загрузиться.');

        } catch (error) {
            console.error('Ошибка при загрузке похожих фильмов:', error);
            similarMoviesContainer.innerHTML = '<h3>Похожие фильмы</h3><p>Не удалось загрузить список похожих фильмов.</p>';
        }
    }


    async function loadMovieDetails() {
        try {
            const response = await fetch(`http://127.0.0.1:8000/get_film_by_id?film_id=${movieId}`);
            if (!response.ok) {
                movieDetailContainer.innerHTML = response.status === 404
                    ? '<p>Фильм не найден.</p>'
                    : '<p>Ошибка загрузки данных.</p>';
                return;
            }
            const movie = await response.json();
            movieDetailContainer.innerHTML = '';

            const moviePoster = document.createElement('img');
            moviePoster.classList.add('movie-poster');
            moviePoster.alt = `Постер к фильму ${movie.title || 'Без названия'}`;
            moviePoster.src = LOADING_POSTER_PLACEHOLDER;
            movieDetailContainer.appendChild(moviePoster);

            // Загрузка постера для основного фильма
            if (movieId) {
                try {
                    const posterLinkResponse = await fetch(`http://127.0.0.1:8000/get_poster_link?film_id=${movieId}`);
                    if (posterLinkResponse.ok) {
                        const posterData = await posterLinkResponse.json();
                        moviePoster.src = (posterData.poster_link && posterData.poster_link !== "N/A") ? posterData.poster_link : DEFAULT_POSTER_PLACEHOLDER;
                    } else {
                        moviePoster.src = ERROR_LOADING_POSTER_PLACEHOLDER;
                    }
                } catch (error) {
                    moviePoster.src = ERROR_LOADING_POSTER_PLACEHOLDER;
                }
            } else {
                moviePoster.src = DEFAULT_POSTER_PLACEHOLDER;
            }

            const movieDetailsDiv = document.createElement('div');
            movieDetailsDiv.classList.add('movie-details');
            const titleElement = document.createElement('h1'); // Изменено имя переменной для избежания конфликта
            titleElement.textContent = movie.title || 'Без названия';
            movieDetailsDiv.appendChild(titleElement);

            if (movie.tagline) {
                const taglineEl = document.createElement('p');
                taglineEl.classList.add('tagline');
                taglineEl.textContent = movie.tagline;
                movieDetailsDiv.appendChild(taglineEl);
            }
            const overviewEl = document.createElement('p');
            overviewEl.classList.add('overview');
            overviewEl.textContent = movie.overview || 'Описание отсутствует.';
            movieDetailsDiv.appendChild(overviewEl);

            const infoGrid = document.createElement('div');
            infoGrid.classList.add('info-grid');
            const addInfoRow = (label, value) => {
                if (value || typeof value === 'number') {
                    const strong = document.createElement('strong');
                    strong.textContent = label + ':';
                    infoGrid.appendChild(strong);
                    const span = document.createElement('span');
                    span.textContent = value;
                    infoGrid.appendChild(span);
                }
            };
            addInfoRow('Дата выхода', movie.release_date);
            addInfoRow('Продолжительность', movie.runtime ? `${movie.runtime} мин.` : null);
            addInfoRow('Рейтинг TMDb', movie.vote_average ? `${Number(movie.vote_average).toFixed(1)}/10 (${movie.vote_count || 0} голосов)` : null);
            addInfoRow('Бюджет', movie.budget ? `$${movie.budget.toLocaleString('en-US')}` : null);
            addInfoRow('Сборы', movie.revenue ? `$${movie.revenue.toLocaleString('en-US')}` : null);
            movieDetailsDiv.appendChild(infoGrid);
            movieDetailContainer.appendChild(movieDetailsDiv);

            if (movieId) {
                loadSimilarMovies(movieId); // Загрузка похожих фильмов
            }

        } catch (error) {
            console.error('Ошибка при загрузке деталей фильма:', error);
            movieDetailContainer.innerHTML = '<p>Не удалось загрузить детали фильма.</p>';
            if (similarMoviesContainer) similarMoviesContainer.innerHTML = '';
        }
    }

    loadMovieDetails();
});