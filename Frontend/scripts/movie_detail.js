document.addEventListener('DOMContentLoaded', async () => {
    const movieDetailContainer = document.getElementById('movie-detail-container');
    const starRatingSection = document.getElementById('star-rating-section');
    const starRatingContainer = document.getElementById('star-rating-container');
    const ratingFeedback = document.getElementById('rating-feedback');
    const authPromptSection = document.getElementById('auth-prompt-section');

    // Плейсхолдер по умолчанию, если не удастся загрузить постер
    const DEFAULT_POSTER_PLACEHOLDER = 'https://via.placeholder.com/300x450?text=No+Poster';
    const LOADING_POSTER_PLACEHOLDER = 'https://via.placeholder.com/300x450?text=Loading+Poster...';
    const ERROR_LOADING_POSTER_PLACEHOLDER = 'https://via.placeholder.com/300x450?text=Error+Loading+Poster';


    const urlParams = new URLSearchParams(window.location.search);
    const movieId = urlParams.get('film_id');

    if (!movieId || isNaN(movieId)) {
        movieDetailContainer.innerHTML = '<p>Неверный ID фильма.</p>';
        return;
    }

    async function checkAuthStatus() {
        try {
            const response = await fetch('http://127.0.0.1:8000/check_auth', {
                method: 'GET',
                headers: {
                    // 'Accept': 'application/json'
                },
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
        if (!movieId) return;
        ratingFeedback.textContent = 'Отправка оценки...';
        const apiUrl = new URL('http://127.0.0.1:8000/like');
        apiUrl.searchParams.append('raiting', String(ratingValue));
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
                renderStars(ratingValue, true);
            } else {
                let errorDetailMessage = 'Не удалось сохранить оценку.';
                let rawErrorDataOutput = `Статус ответа: ${response.status}. Нет дополнительных деталей от сервера.`;
                try {
                    const errorData = await response.json();
                    console.log('ПОЛНЫЙ ОТВЕТ ОБ ОШИБКЕ ОТ СЕРВЕРА (errorData):', JSON.stringify(errorData, null, 2));
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
                        if (textError) {
                           rawErrorDataOutput = textError;
                           console.log('ОТВЕТ СЕРВЕРА (текст):', rawErrorDataOutput);
                        }
                    } catch (textErr) {
                        console.error('Не удалось получить тело ответа как текст:', textErr);
                    }
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

    function renderStars(ratingToDisplay, isFixed = false) {
        starRatingContainer.innerHTML = '';
        for (let i = 1; i <= 10; i++) {
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
                star.addEventListener('click', (event) => { // Восстановлен полный обработчик
                    event.preventDefault(); // На всякий случай, если еще не убрали проблему с перезагрузкой
                    currentRating = i;
                    permanentRating = i;
                    renderStars(currentRating, true);
                    submitRating(currentRating);
                });
            }
            starRatingContainer.appendChild(star);
        }
    }

    function initStarRating() {
        starRatingSection.style.display = 'block';
        authPromptSection.style.display = 'none';
        renderStars(currentRating, permanentRating > 0);
    }

    function showAuthPrompt() {
        starRatingSection.style.display = 'none';
        authPromptSection.style.display = 'block';
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
            movieDetailContainer.innerHTML = ''; // Очищаем "Загрузка..."

            // ----- ИЗМЕНЕНИЯ ДЛЯ ПОСТЕРА -----
            const moviePoster = document.createElement('img');
            moviePoster.classList.add('movie-poster'); // Убедитесь, что этот класс стилизован в movie_detail.css
            moviePoster.alt = `Постер к фильму ${movie.title || 'Без названия'}`;
            moviePoster.src = LOADING_POSTER_PLACEHOLDER; // Начальный плейсхолдер загрузки
            movieDetailContainer.appendChild(moviePoster);

            // Асинхронно загружаем "нормальный" постер
            if (movieId) {
                try {
                    const posterLinkResponse = await fetch(`http://127.0.0.1:8000/get_poster_link?film_id=${movieId}`);
                    if (posterLinkResponse.ok) {
                        const posterData = await posterLinkResponse.json();
                        if (posterData.poster_link && posterData.poster_link !== "N/A") {
                            moviePoster.src = posterData.poster_link;
                        } else {
                            console.warn(`Постер не найден через /get_poster_link для film_id ${movieId}. Ответ: ${posterData.poster_link}`);
                            moviePoster.src = DEFAULT_POSTER_PLACEHOLDER; // Плейсхолдер "нет постера"
                        }
                    } else {
                        console.warn(`Ошибка при запросе ссылки на постер для film_id ${movieId}: ${posterLinkResponse.status}`);
                        moviePoster.src = ERROR_LOADING_POSTER_PLACEHOLDER; // Плейсхолдер ошибки
                    }
                } catch (error) {
                    console.error('Сетевая ошибка при запросе ссылки на постер:', error);
                    moviePoster.src = ERROR_LOADING_POSTER_PLACEHOLDER; // Плейсхолдер ошибки
                }
            } else {
                moviePoster.src = DEFAULT_POSTER_PLACEHOLDER; // Если нет movieId для запроса постера
            }
            // ----- КОНЕЦ ИЗМЕНЕНИЙ ДЛЯ ПОСТЕРА -----

            const movieDetailsDiv = document.createElement('div');
            movieDetailsDiv.classList.add('movie-details'); // Убедитесь, что этот класс стилизован
            const title = document.createElement('h1');
            title.textContent = movie.title || 'Без названия';
            movieDetailsDiv.appendChild(title);

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
                if (value || typeof value === 'number') { // Позволяем отображать 0
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
            addInfoRow('Рейтинг TMDb', movie.vote_average ? `${movie.vote_average.toFixed(1)}/10 (${movie.vote_count || 0} голосов)` : null);
            addInfoRow('Бюджет', movie.budget ? `$${movie.budget.toLocaleString('en-US')}` : null);
            addInfoRow('Сборы', movie.revenue ? `$${movie.revenue.toLocaleString('en-US')}` : null);
            movieDetailsDiv.appendChild(infoGrid);
            movieDetailContainer.appendChild(movieDetailsDiv); // Добавляем блок с деталями ПОСЛЕ постера

            const isAuthenticated = await checkAuthStatus();
            if (isAuthenticated) {
                initStarRating();
            } else {
                showAuthPrompt();
            }

        } catch (error) {
            console.error('Ошибка при загрузке деталей фильма:', error);
            movieDetailContainer.innerHTML = '<p>Не удалось загрузить детали фильма.</p>';
        }
    }

    loadMovieDetails();
});