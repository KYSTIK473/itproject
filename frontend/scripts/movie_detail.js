document.addEventListener('DOMContentLoaded', async () => {
    const movieDetailContainer = document.getElementById('movie-detail-container');
    const similarMoviesContainer = document.getElementById('similar-movies-container');
    const ratingFeedback = document.getElementById('rating-feedback');

    const DEFAULT_POSTER_PLACEHOLDER = 'https://via.placeholder.com/300x450?text=No+Poster';
    const LOADING_POSTER_PLACEHOLDER = 'https://via.placeholder.com/300x450?text=Loading+Poster...';
    const ERROR_LOADING_POSTER_PLACEHOLDER = 'https://via.placeholder.com/300x450?text=Error+Loading+Poster';

    const movieItemConfig = {
        posterAPIBaseURL: 'http://127.0.0.1:8000',
        placeholderImage: 'https://via.placeholder.com/120x180?text=No+Poster',
    };

    const urlParams = new URLSearchParams(window.location.search);
    const movieId = urlParams.get('film_id'); // This is film_id from URL, used as movie_id for API calls

    if (!movieId || isNaN(movieId)) {
        if (movieDetailContainer) movieDetailContainer.innerHTML = '<p>Неверный ID фильма.</p>';
        return;
    }

    const escapeHTML = (str) => {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')

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
            return;
        }
        try {
            const posterApiUrl = new URL(`${movieItemConfig.posterAPIBaseURL}/get_poster_link`);
            posterApiUrl.searchParams.append('film_id', String(movieIdForPoster));
            const response = await fetch(posterApiUrl.toString());
            if (!response.ok) {
                return;
            }
            const data = await response.json();
            if (data.poster_link && data.poster_link !== "N/A") {
                imgElement.src = data.poster_link;
            }
        } catch (error) {
            console.error(`Ошибка при обновлении постера для фильма ID ${movieIdForPoster}:`, error);
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
            }
            return false;
        } catch (error) {
            console.error('Ошибка при вызове /check_auth:', error);
            return false;
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
            if (i <= ratingToDisplay) star.classList.add('selected');
            if (!isFixed) {
                star.addEventListener('mouseover', () => { if (!permanentRating || currentRating !== permanentRating) renderStars(i, false); });
                star.addEventListener('mouseout', () => { if (!permanentRating || currentRating !== permanentRating) renderStars(currentRating, false); });
                star.addEventListener('click', (event) => {
                    event.preventDefault(); currentRating = i; permanentRating = i;
                    renderStars(currentRating, true); submitRating(currentRating);
                });
            }
            starRatingContainer.appendChild(star);
        }
    }

    async function submitRating(ratingValue) {
        if (!movieId || !ratingFeedback) return;
        ratingFeedback.textContent = 'Отправка оценки...';
        const apiUrl = new URL('http://127.0.0.1:8000/like');
        apiUrl.searchParams.append('rating', String(ratingValue));
        apiUrl.searchParams.append('film_id', String(movieId));
        try {
            const response = await fetch(apiUrl.toString(), { method: 'POST', credentials: 'include' });
            if (response.ok) {
                const result = await response.json();
                ratingFeedback.textContent = `Ваша оценка (${ratingValue}) сохранена!`;
            } else {
                let errorDetailMessage = 'Не удалось сохранить оценку.';
                try {
                    const errorData = await response.json();
                    if (errorData.detail) {
                        if (typeof errorData.detail === 'string') {
                            errorDetailMessage = errorData.detail;
                        } else if (Array.isArray(errorData.detail)) {
                            errorDetailMessage = errorData.detail.map(err => `${err.loc ? err.loc.join('->') : ''}: ${err.msg}`).join('; ');
                        } else {
                            errorDetailMessage = JSON.stringify(errorData.detail);
                        }
                    } else {
                        errorDetailMessage = JSON.stringify(errorData);
                    }
                } catch (e) { /* Ошибка парсинга JSON игнорируется, используется сообщение по умолчанию */ }
                ratingFeedback.textContent = `Ошибка (${response.status}): ${errorDetailMessage.split('\n')[0]}`;
                permanentRating = 0; renderStars(currentRating, false);
            }
        } catch (error) {
            ratingFeedback.textContent = 'Сетевая ошибка при отправке оценки.';
            permanentRating = 0; renderStars(currentRating, false);
        }
    }


    async function loadCast(filmId, containerElement) {
        if (!containerElement) return;
        containerElement.innerHTML = '<p>Загрузка актерского состава...</p>';
        try {
            const response = await fetch(`http://127.0.0.1:8000/cast?movie_id=${filmId}`);
            if (!response.ok) {
                containerElement.innerHTML = `<p>Не удалось загрузить актерский состав.</p>`;
                return;
            }
            const castData = await response.json();
            if (!Array.isArray(castData) || castData.length === 0) {
                containerElement.innerHTML = '<p>Информация об актерском составе отсутствует.</p>';
                return;
            }

            containerElement.innerHTML = '';
            const list = document.createElement('ul');
            castData.slice(0, 15).forEach(member => {
                const listItem = document.createElement('li');
                const name = escapeHTML(member.name || 'Неизвестный актер');
                const character = escapeHTML(member.character || 'Неизвестная роль');
                listItem.innerHTML = `${name} <span class="character-name">(как ${character})</span>`;
                list.appendChild(listItem);
            });
            containerElement.appendChild(list);

        } catch (error) {
            console.error('Ошибка при загрузке актерского состава:', error);
            containerElement.innerHTML = '<p>Ошибка при загрузке актерского состава. Пожалуйста, проверьте консоль.</p>';
        }
    }

    async function loadCrew(filmId, containerElement) {
        if (!containerElement) return;
        containerElement.innerHTML = '<p>Загрузка съемочной группы...</p>';
        try {
            const response = await fetch(`http://127.0.0.1:8000/crew/?movie_id=${filmId}`);
            if (!response.ok) {
                containerElement.innerHTML = `<p>Не удалось загрузить съемочную группу.</p>`;
                return;
            }
            const crewData = await response.json();
            if (!Array.isArray(crewData) || crewData.length === 0) {
                containerElement.innerHTML = '<p>Информация о съемочной группе отсутствует.</p>';
                return;
            }

            containerElement.innerHTML = '';
            const list = document.createElement('ul');
            const keyJobs = ["Director", "Screenplay", "Producer", "Director of Photography", "Original Music Composer"];
            let displayedCount = 0;
            const maxDisplay = 10;

            keyJobs.forEach(jobName => {
                crewData.filter(member => member.job === jobName).forEach(member => {
                    if (displayedCount < maxDisplay) {
                        const listItem = document.createElement('li');
                        const name = escapeHTML(member.name || 'Неизвестный участник');
                        const job = escapeHTML(member.job || 'Неизвестная должность');
                        listItem.innerHTML = `<span class="job-title">${job}:</span> ${name}`;
                        list.appendChild(listItem);
                        displayedCount++;
                    }
                });
            });

            crewData.forEach(member => {
                if (displayedCount < maxDisplay && !keyJobs.includes(member.job)) {
                    const listItem = document.createElement('li');
                    const name = escapeHTML(member.name || 'Неизвестный участник');
                    const job = escapeHTML(member.job || 'Неизвестная должность');
                    listItem.innerHTML = `<span class="job-title">${job}:</span> ${name}`;
                    list.appendChild(listItem);
                    displayedCount++;
                }
            });

            if (list.children.length === 0) {
                containerElement.innerHTML = '<p>Информация о ключевых участниках съемочной группы отсутствует.</p>';
            } else {
                containerElement.appendChild(list);
            }

        } catch (error) {
            console.error('Ошибка при загрузке съемочной группы:', error);
            containerElement.innerHTML = '<p>Ошибка при загрузке съемочной группы. Пожалуйста, проверьте консоль.</p>';
        }
    }

    async function loadSimilarMovies(currentMovieId) {
        if (!similarMoviesContainer) {
            console.error('Контейнер для похожих фильмов (similar-movies-container) не найден.');
            return;
        }
        similarMoviesContainer.innerHTML = '<h3>Похожие фильмы</h3><p>Загрузка...</p>';
        try {
            const response = await fetch(`http://127.0.0.1:8000/get_similarity?film_id=${currentMovieId}`);
            if (!response.ok) {
                similarMoviesContainer.innerHTML = `<h3>Похожие фильмы</h3><p>${response.status === 404 ? 'Похожие фильмы не найдены.' : `Ошибка загрузки: ${response.statusText}`}</p>`;
                return;
            }
            const movies = await response.json();
            if (!Array.isArray(movies) || movies.length === 0) {
                similarMoviesContainer.innerHTML = '<h3>Похожие фильмы</h3><p>Похожие фильмы не найдены.</p>';
                return;
            }
            similarMoviesContainer.innerHTML = '<h2 class="section-title">Похожие фильмы</h2>'; // Используем h2 и класс для стилизации из CSS
            const listElement = document.createElement('div');
            listElement.className = 'movies-list similar-movies-grid';
            const posterUpdateTasksInfo = [];
            movies.forEach(movieData => {
                const moviePrepared = { ...movieData, movie_id: movieData.movie_id || movieData.film_id };
                const movieElement = createMovieElement(moviePrepared);
                if (movieElement instanceof Node) {
                    listElement.appendChild(movieElement);
                    if (moviePrepared.movie_id) {
                        posterUpdateTasksInfo.push({ id: String(moviePrepared.movie_id), imgElementId: `poster-img-similar-${moviePrepared.movie_id}` });
                    }
                }
            });
            similarMoviesContainer.appendChild(listElement);
            const updatePromises = posterUpdateTasksInfo.map(task => updatePosterAsync(task.id, task.imgElementId));
            await Promise.all(updatePromises);
        } catch (error) {
            console.error('Ошибка при загрузке похожих фильмов:', error);
            similarMoviesContainer.innerHTML = '<h3>Похожие фильмы</h3><p>Не удалось загрузить список похожих фильмов.</p>';
        }
    }

    async function loadMovieDetails() {
        if (!movieDetailContainer) { // Проверка на существование основного контейнера
            console.error('Главный контейнер movie-detail-container не найден!');
            return;
        }
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
            moviePoster.alt = `Постер к фильму ${escapeHTML(movie.title || 'Без названия')}`;
            moviePoster.src = LOADING_POSTER_PLACEHOLDER;
            // movieDetailContainer.appendChild(moviePoster); // Перенесено ниже

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
            const titleElement = document.createElement('h1');
            titleElement.textContent = escapeHTML(movie.title || 'Без названия');
            movieDetailsDiv.appendChild(titleElement);

            if (movie.tagline) {
                const taglineEl = document.createElement('p');
                taglineEl.classList.add('tagline');
                taglineEl.textContent = escapeHTML(movie.tagline);
                movieDetailsDiv.appendChild(taglineEl);
            }
            const overviewEl = document.createElement('p');
            overviewEl.classList.add('overview');
            overviewEl.textContent = escapeHTML(movie.overview || 'Описание отсутствует.');
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

            // Добавление постера и деталей в основной контейнер
            movieDetailContainer.appendChild(moviePoster);
            movieDetailContainer.appendChild(movieDetailsDiv);

            // Cast Section
            const castSectionDiv = document.createElement('div');
            castSectionDiv.id = 'cast-section';
            castSectionDiv.className = 'movie-info-section';
            const castTitle = document.createElement('h3');
            castTitle.textContent = 'Актерский состав:';
            castSectionDiv.appendChild(castTitle);
            const castListContainer = document.createElement('div');
            castListContainer.id = 'cast-list-container';
            castSectionDiv.appendChild(castListContainer);
            movieDetailContainer.appendChild(castSectionDiv); // Добавляем в главный контейнер

            // Crew Section
            const crewSectionDiv = document.createElement('div');
            crewSectionDiv.id = 'crew-section';
            crewSectionDiv.className = 'movie-info-section';
            const crewTitle = document.createElement('h3');
            crewTitle.textContent = 'Съемочная группа:';
            crewSectionDiv.appendChild(crewTitle);
            const crewListContainer = document.createElement('div');
            crewListContainer.id = 'crew-list-container';
            crewSectionDiv.appendChild(crewListContainer);
            movieDetailContainer.appendChild(crewSectionDiv); // Добавляем в главный контейнер


            if (movieId) {
                loadCast(movieId, castListContainer);
                loadCrew(movieId, crewListContainer);
                loadSimilarMovies(movieId);
            }

        } catch (error) {
            console.error('Ошибка при загрузке деталей фильма:', error);
            if (movieDetailContainer) movieDetailContainer.innerHTML = '<p>Не удалось загрузить детали фильма.</p>';
            if (similarMoviesContainer) similarMoviesContainer.innerHTML = '';
        }
    }

    loadMovieDetails();
});