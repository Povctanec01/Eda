// === Функция: отметить один заказ как готовый ===

// === Функция: отметить один заказ как готовый ===
function markAsReady(event, orderId) {
    event.preventDefault();

    // Ищем форму по ID или другому селектору
    const form = document.querySelector(`form[onsubmit*="${orderId}"]`) || event.target;

    // Проверяем форму
    if (!form) {
        console.error('Форма не найдена для заказа', orderId);
        alert('Форма не найдена');
        return;
    }

    // Ищем CSRF токен внутри формы
    const csrfTokenInput = form.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfTokenInput) {
        alert('Ошибка CSRF токена в форме');
        return;
    }

    // Создаем FormData
    const formData = new FormData(form);

    // Для отладки - выводим данные формы
    console.log('Отправляемые данные:', Object.fromEntries(formData.entries()));

    // Получаем текущий URL
    const currentUrl = window.location.pathname;

    // Отправляем запрос
    fetch(currentUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfTokenInput.value,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        console.log('Статус ответа:', response.status);

        // Проверяем успешность ответа
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Пытаемся получить JSON
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            return response.json();
        } else {
            // Если сервер возвращает не JSON
            return response.text().then(text => {
                console.log('Не-JSON ответ:', text);
                throw new Error('Сервер вернул не JSON');
            });
        }
    })
    .then(data => {
        console.log('Ответ сервера:', data);

        if (data && data.success) {
            // Удаляем карточку
            const el = document.getElementById('order-' + orderId);
            if (el) {
                el.style.opacity = '0.5';
                setTimeout(() => el.remove(), 300);
            }

            // Обновляем счётчик
            updateOrdersBadge(-1);

            // Показываем уведомление
            if (typeof showNotification === 'function') {
                showNotification('Блюдо готово', 'Хорошая работа!', 'success');
            } else {
                alert('Заказ отмечен как готовый!');
            }
        } else {
            const errorMsg = data.error || data.message || 'Неизвестная ошибка сервера';
            alert('Ошибка: ' + errorMsg);
        }
    })
    .catch(err => {
        console.error('Ошибка при обновлении заказа:', err);
        alert('Ошибка при обновлении заказа: ' + err.message);
    });
}

// === Функция: отметить все видимые заказы как готовые ===
function markAllPrepared() {
    if (!confirm('Отметить все заказы как готовые?')) return;

    const forms = document.querySelectorAll('form[method="post"]');
    let updatedCount = 0;
    const total = forms.length;

    forms.forEach(form => {
        const orderIdInput = form.querySelector('input[name="order_id"]');
        if (!orderIdInput) return;

        const orderId = orderIdInput.value;
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

// === Инициализация Select2 для поля аллергенов ===
function initSelect2() {
    // Проверяем наличие jQuery
    if (typeof $ === 'undefined') {
        console.warn('jQuery не загружен, Select2 не будет инициализирован');
        return;
    }

    const allergensSelect = $('#id_allergens');
    if (allergensSelect.length) {
        allergensSelect.select2({
            placeholder: "Выберите аллергены",
            allowClear: true,
            language: "ru",
            width: '100%',
            dropdownParent: $('.menu-management'),
            closeOnSelect: false
        });

        // Закрытие при клике вне поля
        $(document).on('click', function(e) {
            if (!$(e.target).closest('.select2-container').length) {
                $('.select2-container--open').removeClass('select2-container--open');
                $('.select2-dropdown').hide();
            }
        });
    }
}

// === Функция для фильтрации блюд по типу ===
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

// === Функция для фильтрации скрытых блюд ===
function toggleVisibilityFilter() {
    const items = document.querySelectorAll('.dish-item');
    const button = document.querySelector('button[onclick*="toggleVisibilityFilter"]');
    if (!button) return;

    let currentState = button.getAttribute('data-state') || 'all'; // Сохраняем состояние в атрибуте кнопки

    if (currentState === 'all') {
        // Переключаемся на показ только скрытых
        items.forEach(item => {
            const isHidden = item.getAttribute('data-hidden') === 'true';
            item.style.display = isHidden ? 'block' : 'none';
        });

        button.innerHTML = '<i class="fas fa-eye"></i> Показать все';
        button.setAttribute('data-state', 'hidden-only');
    } else {
        // Показываем все блюда
        items.forEach(item => {
            item.style.display = 'block';
        });

        button.innerHTML = '<i class="fas fa-eye-slash"></i> Показать скрытые';
        button.setAttribute('data-state', 'all');
    }
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

// === Функция для поиска продуктов ===
function filterProducts() {
    const input = document.getElementById('productSearch');
    if (!input) return;

    const filter = input.value.toLowerCase();
    const rows = document.getElementsByClassName('product-row');

    for (let i = 0; i < rows.length; i++) {
        const productName = rows[i].getElementsByTagName('td')[0].innerText.toLowerCase();
        if (productName.includes(filter)) {
            rows[i].style.display = '';
        } else {
            rows[i].style.display = 'none';
        }
    }
}

// === Функция для показа формы изменения количества ===
function showQuantityForm(productId) {
    // Скрываем все другие формы редактирования
    hideAllEditForms();

    // Показываем нужную форму
    const formRow = document.getElementById('quantity-form-' + productId);
    const productRow = document.getElementById('product-row-' + productId);

    if (formRow && productRow) {
        formRow.style.display = 'table-row';
        productRow.style.display = 'none';
    }
}

// === Функция для скрытия формы изменения количества ===
function hideQuantityForm(productId) {
    const formRow = document.getElementById('quantity-form-' + productId);
    const productRow = document.getElementById('product-row-' + productId);

    if (formRow && productRow) {
        formRow.style.display = 'none';
        productRow.style.display = '';
    }
}

// === Функция для показа формы полного редактирования ===
function showEditForm(productId) {
    // Скрываем все другие формы редактирования
    hideAllEditForms();

    // Показываем нужную форму
    const formRow = document.getElementById('edit-form-' + productId);
    const productRow = document.getElementById('product-row-' + productId);

    if (formRow && productRow) {
        formRow.style.display = 'table-row';
        productRow.style.display = 'none';
    }
}

// === Функция для скрытия формы полного редактирования ===
function hideEditForm(productId) {
    const formRow = document.getElementById('edit-form-' + productId);
    const productRow = document.getElementById('product-row-' + productId);

    if (formRow && productRow) {
        formRow.style.display = 'none';
        productRow.style.display = '';
    }
}

// === Функция для показа формы редактирования буфета ===
function showEditForm_buffet(productId) {
    // Скрываем все формы редактирования
    document.querySelectorAll('.edit-product-form').forEach(form => {
        form.style.display = 'none';
    });

    // Скрываем карточку товара
    const productElement = document.getElementById('product-' + productId);
    if (productElement) {
        productElement.style.display = 'none';
    }

    // Показываем нужную форму
    const formElement = document.getElementById('edit-form-' + productId);
    if (formElement) {
        formElement.style.display = 'block';

        // Прокручиваем к форме
        formElement.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }
}

// === Функция для скрытия формы редактирования буфета ===
function hideEditForm_buffet(productId) {
    // Скрываем форму редактирования
    const formElement = document.getElementById('edit-form-' + productId);
    if (formElement) {
        formElement.style.display = 'none';
    }

    // Показываем карточку товара
    const productElement = document.getElementById('product-' + productId);
    if (productElement) {
        productElement.style.display = 'block';

        // Прокручиваем к карточке
        productElement.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }
}

// === Функция для скрытия всех форм редактирования ===
function hideAllEditForms() {
    const editForms = document.getElementsByClassName('edit-form-row');
    const productRows = document.getElementsByClassName('product-row');

    // Скрываем все формы редактирования
    for (let i = 0; i < editForms.length; i++) {
        editForms[i].style.display = 'none';
    }

    // Показываем все строки продуктов
    for (let i = 0; i < productRows.length; i++) {
        productRows[i].style.display = '';
    }
}

// === Функция для управления карточками блюд ===
function showDishEditForm(cardId) {
    // Скрываем все формы редактирования
    document.querySelectorAll('.edit-dish-form').forEach(form => {
        form.style.display = 'none';
    });

    // Показываем нужную форму
    const formElement = document.getElementById('edit-form-' + cardId);
    if (formElement) {
        formElement.style.display = 'block';
        // Прокручиваем к форме
        formElement.scrollIntoView({ behavior: 'smooth' });
    }
}

function hideDishEditForm(cardId) {
    const formElement = document.getElementById('edit-form-' + cardId);
    if (formElement) {
        formElement.style.display = 'none';
    }
}

// === Инициализация jQuery при готовности ===
if (typeof $ !== 'undefined') {
    $(document).ready(function() {
        initSelect2();
    });
}