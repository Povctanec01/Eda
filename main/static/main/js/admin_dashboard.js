// main/static/main/js/admin_dashboard.js

document.addEventListener('DOMContentLoaded', function () {
    // === 1. Переключение темы ===
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        // Загружаем сохранённую тему
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        themeToggle.checked = (savedTheme === 'dark');

        themeToggle.addEventListener('change', function () {
            const newTheme = this.checked ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    // === 2. Генерация отчётов ===
    const reportBtns = document.querySelectorAll('.report-btn');
    if (reportBtns.length > 0) {
        reportBtns.forEach(btn => {
            btn.addEventListener('click', function () {
                const period = this.dataset.period;
                fetch('/admin/generate-report/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({ period: period })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Отчёт успешно сгенерирован!');
                    } else {
                        alert('Ошибка при генерации отчёта: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Ошибка:', error);
                    alert('Не удалось связаться с сервером.');
                });
            });
        });
    }

    // === 3. Просмотр деталей дня ===
    const viewDetailsBtns = document.querySelectorAll('.view-details-btn');
    if (viewDetailsBtns.length > 0) {
        viewDetailsBtns.forEach(btn => {
            btn.addEventListener('click', function () {
                const date = this.dataset.date;
                window.location.href = `/admin/statistics/details/${date}/`;
            });
        });
    }

    // === 4. Закрытие модальных окон (если есть) ===
    const closeModalButtons = document.querySelectorAll('.close-modal, .modal-close');
    if (closeModalButtons.length > 0) {
        closeModalButtons.forEach(btn => {
            btn.addEventListener('click', function () {
                const modal = this.closest('.modal');
                if (modal) {
                    modal.style.display = 'none';
                }
            });
        });
    }

    // === 5. Вспомогательная функция для CSRF ===
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});