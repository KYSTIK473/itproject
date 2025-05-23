document.addEventListener('DOMContentLoaded', () => {
    const elements = {
        searchForm: document.getElementById('search-form'),
        searchInput: document.getElementById('search-input'),
        moviesList: document.getElementById('movies-list-container'),
        foundCount: document.getElementById('found-count'),
        prevPageBtn: document.getElementById('prev-page-btn'),
        nextPageBtn: document.getElementById('next-page-btn'),
    };

    const config = {
        baseURL: 'http://127.0.0.1:8000/films', // URL вашего API для списка фильмов
        posterAPIBaseURL: 'http://127.0.0.1:8000', // Базовый URL для API постеров
        placeholderImage: 'https://via.placeholder.com/120x180?text=No+Poster',
        maxQueryLength: 100
    };

    const state = {
        currentQuery: '',
        currentSkip: 0,
        limit: 10,
        isLoading: false,
        hasMorePages: true,
        abortController: null
    };

    // Генерация URL для API списка фильмов
    const getAPIUrl = () => {
        const url = new URL(config.baseURL);
        if (state.currentQuery) {
            url.searchParams.set('query', state.currentQuery);
        }
        url.searchParams.set('limit', String(state.limit));
        url.searchParams.set('skip', String(state.currentSkip));
        return url;
    };

    // Экранирование HTML
    const escapeHTML = (str) => {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    };

    // Создание элемента фильма
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
            ? escapeHTML(movie.overview.slice(0, 250) + (movie.overview.length > 250 ? '...' : ''))
            : 'Описание отсутствует';
        const budget = (typeof movie.budget === 'number' && !isNaN(movie.budget))
            ? `Бюджет: $${movie.budget.toLocaleString()}`
            : '';
        const runtime = (typeof movie.runtime === 'number' && movie.runtime > 0)
            ? `Продолжительность: ${movie.runtime} мин.`
            : '';
        const rating = (typeof movie.vote_average === 'number' && !isNaN(movie.vote_average))
            ? `★ ${movie.vote_average.toFixed(1)} (${movie.vote_count || 0} оценок)`
            : '';

        const movieId = movie.movie_id || '#';
        const detailPageUrl = `movie_detail.html?film_id=${movieId}`; // Ссылка на страницу деталей
        const posterImgId = `poster-img-${movieId}`; // Уникальный ID для изображения

        element.innerHTML = `
            <a href="${detailPageUrl}" class="movie-link">
                <img id="${posterImgId}" src="${config.placeholderImage}" alt="Постер ${title}" loading="lazy">
                <div class="movie-info">
                    <h2>${title}</h2>
                    <div class="meta">
                        <p class="year">${year}</p>
                        ${rating ? `<p class="rating">${rating}</p>` : ''}
                    </div>
                    ${overview ? `<p class="overview">${overview}</p>` : ''}
                    <div class="details">
                        ${budget ? `<p>${budget}</p>` : ''}
                        ${runtime ? `<p>${runtime}</p>` : ''}
                    </div>
                </div>
            </a>
        `;
        return element;
    };

    // Асинхронная загрузка и обновление постера
    async function updatePosterAsync(movieId, imgElementId) {
        const imgElement = document.getElementById(imgElementId);
        if (!imgElement) {
            // console.warn(`Элемент изображения с ID ${imgElementId} не найден.`);
            return;
        }

        try {
            const posterApiUrl = new URL(`${config.posterAPIBaseURL}/get_poster_link`);
            posterApiUrl.searchParams.append('film_id', String(movieId)); // Убедимся, что film_id - строка

            const response = await fetch(posterApiUrl.toString());
            if (!response.ok) {
                // console.warn(`Не удалось загрузить постер для фильма ID ${movieId}. Статус: ${response.status}`);
                return; // Оставляем плейсхолдер
            }
            const data = await response.json();
            if (data.poster_link && data.poster_link !== "N/A") {
                imgElement.src = data.poster_link;
            } else {
                // console.warn(`Ссылка на постер не найдена или N/A для фильма ID ${movieId}.`);
            }
        } catch (error) {
            console.error(`Ошибка при обновлении постера для фильма ID ${movieId}:`, error);
        }
    }

    // Обновление состояния кнопок пагинации
    const updatePaginationButtons = () => {
        elements.prevPageBtn.disabled = state.currentSkip === 0 || state.isLoading;
        elements.nextPageBtn.disabled = !state.hasMorePages || state.isLoading;
    };

    // Загрузка данных
    const loadMovies = async () => {
        if (state.isLoading) return;
        state.isLoading = true;
        updatePaginationButtons();

        if (state.abortController) {
            state.abortController.abort();
        }
        state.abortController = new AbortController();

        try {
            elements.moviesList.innerHTML = '<div class="loader">Загрузка...</div>';
            const apiUrl = getAPIUrl();
            // console.log("Requesting URL for movies:", apiUrl.toString());

            const response = await fetch(apiUrl, { signal: state.abortController.signal });

            if (!response.ok) throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
            const data = await response.json();

            if (!Array.isArray(data)) throw new Error('Некорректные данные от сервера: ожидался массив');

            elements.foundCount.textContent = `Результаты на странице: ${data.length}`;
            elements.moviesList.innerHTML = '';

            if (data.length === 0 && state.currentSkip === 0) {
                elements.moviesList.innerHTML = '<p>Фильмы не найдены.</p>';
                state.hasMorePages = false;
            } else {
                data.forEach(movie => {
                    if (!movie || typeof movie !== 'object' || !movie.movie_id || typeof movie.title === 'undefined') {
                        console.warn('Пропуск некорректных данных фильма:', movie);
                        return;
                    }
                    const movieElement = createMovieElement(movie);
                    if (movieElement instanceof Node) {
                        elements.moviesList.appendChild(movieElement);
                        if (movie.movie_id) {
                            updatePosterAsync(String(movie.movie_id), `poster-img-${movie.movie_id}`);
                        }
                    } else {
                        console.error('Функция createMovieElement не вернула DOM-узел для фильма:', movie);
                    }
                });
                state.hasMorePages = data.length === state.limit;
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                // console.log('Запрос списка фильмов отменен.');
            } else {
                console.error('Ошибка при загрузке фильмов:', error);
                elements.moviesList.innerHTML = `<div class="error"><p>Не удалось загрузить фильмы.</p><small>${escapeHTML(error.message)}</small></div>`;
                state.hasMorePages = false;
            }
        } finally {
            state.isLoading = false;
            updatePaginationButtons();
        }
    };

    // Обработчики событий
    const handleSearch = (e) => {
        e.preventDefault();
        const query = elements.searchInput.value.trim();

        state.currentQuery = query;
        state.currentSkip = 0;
        state.hasMorePages = true;

        sessionStorage.setItem('lastSearchQueryMovies', state.currentQuery);
        sessionStorage.setItem('lastSearchSkipMovies', String(state.currentSkip));

        loadMovies();
    };

    const handleNextPage = () => {
        if (state.hasMorePages && !state.isLoading) {
            state.currentSkip += state.limit;
            sessionStorage.setItem('lastSearchSkipMovies', String(state.currentSkip));
            loadMovies();
        }
    };

    const handlePrevPage = () => {
        if (state.currentSkip > 0 && !state.isLoading) {
            state.currentSkip -= state.limit;
            if (state.currentSkip < 0) state.currentSkip = 0;
            sessionStorage.setItem('lastSearchSkipMovies', String(state.currentSkip));
            loadMovies();
        }
    };

    // Инициализация
    const init = () => {
        if (!elements.searchForm || !elements.searchInput || !elements.moviesList ||
            !elements.foundCount || !elements.prevPageBtn || !elements.nextPageBtn) {
            console.error('Один или несколько HTML-элементов не найдены на странице. Проверьте ID.');
            return;
        }

        elements.searchForm.addEventListener('submit', handleSearch);
        elements.nextPageBtn.addEventListener('click', handleNextPage);
        elements.prevPageBtn.addEventListener('click', handlePrevPage);

        const savedQuery = sessionStorage.getItem('lastSearchQueryMovies');
        const savedSkip = sessionStorage.getItem('lastSearchSkipMovies');

        if (savedQuery !== null) {
            state.currentQuery = savedQuery;
            elements.searchInput.value = savedQuery;
        }
        if (savedSkip !== null) {
            state.currentSkip = parseInt(savedSkip, 10) || 0;
        }

        loadMovies();
    };

    init();
});