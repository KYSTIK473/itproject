document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('http://127.0.0.1:8000/user_data/', {
            credentials: 'include',
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                // Добавьте авторизацию при необходимости
                // 'Authorization': `Bearer ${token}`
            },
        });

        if (!response.ok) throw new Error('Ошибка загрузки данных');

        const userData = await response.json();
        fillForm(userData);

    } catch (error) {
        showMessage(error.message, 'error');
    }
});

// Заполнение формы данными
function fillForm(data) {
    document.getElementById('first_name').value = data.first_name || '';
    document.getElementById('last_name').value = data.last_name || '';
    document.getElementById('email').value = data.email || '';
    document.getElementById('phone').value = data.phone || '';
}

// Обновление профиля
async function updateProfile() {
    const updateData = {
        first_name: document.getElementById('first_name').value,
        last_name: document.getElementById('last_name').value,
        phone: document.getElementById('phone').value,
        email: document.getElementById('email').value
    };

    try {
        const response = await fetch('http://127.0.0.1:8000/update_user_data/', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData),
            credentials: 'include'
        });

        const result = await response.json();
        if (!response.ok) throw new Error(result.detail || 'Ошибка обновления');

        showMessage('Профиль успешно обновлен!', 'success');
        document.getElementById('password').value = '';

    } catch (error) {
        showMessage(error.message, 'error');
    }
}

// Выход из профиля
async function logout() {
    try {
        const response = await fetch('http://127.0.0.1:8000/logout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        const result = await response.json();
        if (!response.ok) throw new Error(result.detail || 'Ошибка обновления');

        showMessage('Logout', 'success');

    } catch (error) {
        showMessage(error.message, 'error');
    }

    window.location.href = '/pages/index.html';
}

// Переключение видимости пароля
function togglePassword() {
    const passwordField = document.getElementById('password');
    passwordField.type = passwordField.type === 'password' ? 'text' : 'password';
}

// Уведомления
function showMessage(text, type = 'info') {
    const messageEl = document.getElementById('message');
    messageEl.textContent = text;
    messageEl.className = type + ' message';
    messageEl.style.display = 'block';

    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 3000);
}