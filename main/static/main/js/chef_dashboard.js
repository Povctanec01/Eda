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
$(document).ready(function() {
    // Инициализация Select2 для поля аллергенов
    $('#id_allergens').select2({
        placeholder: "Выберите аллергены",
        allowClear: true,
        language: "ru",
        width: '100%',
        dropdownParent: $('.menu-management'),
        // Закрытие при клике вне поля (это поведение по умолчанию в Select2)
        closeOnSelect: false // Оставляем dropdown открытым после выбора
    });

    // Select2 автоматически закрывает dropdown при клике вне элемента
    // но мы можем добавить дополнительную обработку
    $(document).on('click', function(e) {
        // Если клик был не по Select2 и не внутри его dropdown
        if (!$(e.target).closest('.select2-container').length) {
            // Закрываем все открытые Select2 dropdown
            $('.select2-container--open').removeClass('select2-container--open');
            $('.select2-dropdown').hide();
        }
    });
});

// Функция для фильтрации блюд по типу
function showMeals(type) {
    const items = document.querySelectorAll('.dish-item');

    items.forEach(item => {
        if (type === 'Все') {
            item.style.display = 'block';
        } else {
            const mealType = item.getAttribute('data-meal-type');
            item.style.display = mealType === type ? 'block' : 'none';
        }
    });
}
// Функция для фильтрации скрытых блюд
function toggleVisibilityFilter() {
    const items = document.querySelectorAll('.dish-item');
    const showHiddenOnly = true; // или реализуйте переключение

    items.forEach(item => {
        const isHidden = item.getAttribute('data-hidden') === 'true';
        item.style.display = showHiddenOnly ? (isHidden ? 'block' : 'none') : 'block';
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