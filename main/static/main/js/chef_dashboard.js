// === Функция: отметить один заказ как готовый ===
function markAsReady(event, orderId) {
    event.preventDefault();
    const form = event.target;
    fetch('', {
        method: 'POST',
        body: new FormData(form),
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Удаляем карточку
            const el = document.getElementById('order-' + orderId);
            if (el) el.remove();

            // Обновляем счётчик в боковом меню
            const badge = document.getElementById('ordersBadge');
            if (badge) {
                let current = parseInt(badge.textContent);
                if (!isNaN(current) && current > 0) {
                    badge.textContent = current - 1;
                }
            }
        }
    })
    .catch(err => {
        alert('Ошибка при обновлении заказа');
        console.error(err);
    });
}

// === Функция: отметить все видимые заказы как готовые ===
function markAllPrepared() {
    if (!confirm('Отметить все заказы как готовые?')) return;

    const forms = document.querySelectorAll('form[method="post"]');
    let updatedCount = 0;
    const total = forms.length;

    forms.forEach(form => {
        const orderId = form.querySelector('input[name="order_id"]').value;
        fetch('', {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const el = document.getElementById('order-' + orderId);
                if (el) el.remove();
                updatedCount++;
                if (updatedCount === total) {
                    // Обновляем счётчик на все заказы
                    const badge = document.getElementById('ordersBadge');
                    if (badge) {
                        badge.textContent = '0';
                    }
                }
            }
        })
        .catch(err => console.error(err));
    });
}

// === Обновление счётчика в боковом меню ===
function updateOrdersBadge(delta) {
    const badge = document.getElementById('ordersBadge');
    if (!badge) return;
    let current = parseInt(badge.textContent) || 0;
    current += delta;
    if (current < 0) current = 0;
    badge.textContent = current;
}

// === Инициализация при загрузке ===
document.addEventListener('DOMContentLoaded', function () {
    // Обновляем дату
    const months = [
        'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
        'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
    ];
    const now = new Date();
    const day = now.getDate();
    const month = months[now.getMonth()];
    const year = now.getFullYear();
    const dateElement = document.getElementById('currentDate');
    if (dateElement) {
        dateElement.textContent = `${day} ${month} ${year}`;
    }

    // Обновляем счётчик заказов из Django
    if (typeof window.djangoData !== 'undefined' && window.djangoData.allOrdersCount !== undefined) {
        updateOrdersBadge(window.djangoData.allOrdersCount - (parseInt(document.getElementById('ordersBadge').textContent) || 0));
    }
});