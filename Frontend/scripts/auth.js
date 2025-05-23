const Auth = (() => {
    // Приватные методы
    const _checkAuth = async () => {
        try {
            // Укажите полный URL (замените порт при необходимости)
            const response = await fetch('http://127.0.0.1:8000/check_auth', { 
                method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // Добавьте авторизацию при необходимости
          // 'Authorization': `Bearer ${token}`
        },
        credentials: 'include'
            });
            return await response.json();
        } catch (error) {
            console.error('Auth check failed:', error);
            return { is_authenticated: false };
        }
    };

    const _updateUI = (isAuthenticated, avatarUrl) => {
        const signInBtn = document.getElementById('sign-in-btn');
        const avatarImg = document.getElementById('user-avatar-img');
        const avatarLink = document.querySelector('.user-avatar');

        // Проверка существования элементов
        if (!signInBtn || !avatarImg || !avatarLink) {
            console.warn('Элементы аутентификации не найдены');
            return;
        }

        if (isAuthenticated) {
            signInBtn.style.display = 'none';
            avatarLink.style.display = 'block';
            avatarImg.src = avatarUrl || '../pic/default-avatar.jpg';
        } else {
            signInBtn.style.display = 'block';
            avatarLink.style.display = 'none';
        }
    };

    // Публичные методы
    return {
        init: () => {
            document.addEventListener('DOMContentLoaded', async () => {
                const authData = await _checkAuth();
                _updateUI(authData.is_authenticated, authData.avatar_url);

                // Обработчик формы входа
                const loginForm = document.getElementById('loginForm');
                if (loginForm) {
                    loginForm.addEventListener('submit', async (e) => {
                        e.preventDefault();
                        try {
                            const response = await fetch('http://127.0.0.1:8000/login/', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                credentials: 'include',
                                body: JSON.stringify({
                                    email: document.getElementById('email').value,
                                    password: document.getElementById('password').value
                                }),
                            });
                            if (!response.ok) throw new Error('Ошибка авторизации');
                            window.location.href = 'index.html';
                        } catch (error) {
                            alert(error.message);
                        }
                    });
                }
            });
        }
    };
})();

Auth.init();