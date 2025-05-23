document.addEventListener('DOMContentLoaded', () => {
    // Получаем элементы формы (убедитесь, что ID в HTML соответствуют)
    const registrationForm = document.getElementById('registrationForm');
    const phoneInput = document.querySelector('#phone_number');
    const firstNameInput = document.querySelector('#first_name');
    const lastNameInput = document.querySelector('#last_name');
    const emailInput = document.querySelector('#email');
    const passwordInput = document.querySelector('#password');
    // const submitButton = document.querySelector('#submit'); // Эта переменная не используется, если обработчик на форме

    if (!registrationForm) {
        console.error('Форма с ID "registrationForm" не найдена!');
        return;
    }
    if (!phoneInput || !firstNameInput || !lastNameInput || !emailInput || !passwordInput) {
        console.error('Одно или несколько полей формы не найдены! Проверьте ID: phone_number, first_name, last_name, email, password.');
        return;
    }

    // Обработчик отправки формы
    registrationForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Отмена стандартного поведения формы

        // Сбор данных в формате, совместимом с Pydantic схемой UserAdd
        const userData = {
            phone_number: phoneInput.value,
            first_name: firstNameInput.value,
            last_name: lastNameInput.value,
            email: emailInput.value,
            password: passwordInput.value,
        };

        try {
            // Отправка POST-запроса на эндпоинт /register/
            const response = await fetch('http://localhost:8000/register/', { // Убедитесь, что URL правильный
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData),
            });

            // Пытаемся получить JSON из ответа, даже если статус не ok
            // Это важно для получения деталей ошибки от FastAPI
            let responseData = null;
            try {
                responseData = await response.json();
            } catch (jsonError) {
                console.warn('Не удалось разобрать ответ сервера как JSON:', jsonError);
                // Если тело ответа не JSON, можно попробовать получить его как текст
                // для дополнительной отладки, но для пользователя покажем общую ошибку.
            }

            if (response.ok) {
                // Успешная регистрация (статус 2xx)
                alert((responseData && responseData.message) || 'Регистрация прошла успешно! Пожалуйста, войдите.');
                window.location.href = 'auth.html'; // Перенаправление на страницу входа
            } else if (response.status === 409) {
                // Пользователь уже существует (статус 409 Conflict)
                alert((responseData && responseData.detail) || 'Пользователь с таким email уже существует.');
                window.location.href = 'auth.html'; // Перенаправление на страницу входа после нажатия "ОК"
            } else {
                // Другие ошибки сервера (например, 400, 422 Validation Error, 500)
                let errorMessage = `Ошибка регистрации. Статус: ${response.status}`;
                if (responseData && responseData.detail) {
                    if (typeof responseData.detail === 'string') {
                        errorMessage = responseData.detail;
                    } else if (Array.isArray(responseData.detail)) {
                        // Форматируем ошибки валидации Pydantic от FastAPI
                        errorMessage = 'Пожалуйста, исправьте следующие ошибки:';
                        responseData.detail.forEach(err => {
                            const field = err.loc && err.loc.length > 1 ? err.loc[1] : 'поле'; // Получаем имя поля
                            errorMessage += `\n- ${field}: ${err.msg}`;
                        });
                    } else {
                        // Если detail - это объект, но не массив
                        errorMessage = JSON.stringify(responseData.detail);
                    }
                } else if (responseData) {
                    // Если нет поля detail, но есть другие данные в JSON
                     errorMessage = JSON.stringify(responseData);
                }
                console.error('Ошибка регистрации, детали от сервера:', responseData);
                alert(errorMessage);
                // При ошибках валидации (422) или других ошибках сервера (кроме 409)
                // мы не перенаправляем, чтобы пользователь мог исправить данные или увидеть проблему.
            }
        } catch (networkError) {
            // Ошибки сети или если fetch сам по себе не удался
            console.error('Сетевая ошибка или ошибка выполнения fetch при регистрации:', networkError);
            alert('Произошла ошибка при попытке регистрации. Проверьте ваше интернет-соединение и попробуйте снова. ' + networkError.message);
        }
    });
});
