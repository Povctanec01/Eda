// student_dashboard.js

// Функция для отметки всех заказов как готовых
function markAllPrepared() {
    if (!confirm('Отметить все видимые заказы как готовые?')) return;

    const forms = document.querySelectorAll('.mark-ready-form');
    let completed = 0;
    const total = forms.length;

    if (total === 0) {
        alert('Нет заказов для отметки.');
        return;
    }

    forms.forEach(form => {
        const orderId = form.dataset.orderId;
        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('', {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': csrfToken }
        })
        .then(response => {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json();
            } else {
                throw new Error('Сервер вернул HTML');
            }
        })
        .then(data => {
            if (data.success) {
                const el = document.getElementById('order-' + orderId);
                if (el) el.remove();
            }
            completed++;
            if (completed === total) {
                // Обновляем счётчик до нуля
                const badge = document.querySelector('.sidebar-menu .badge');
                if (badge) badge.textContent = '0';
            }
        })
        .catch(err => {
            console.error('Ошибка при отметке заказа', orderId, err);
        });
    });
}

// Функция для переключения чекбокса при клике по всей карточке
function toggleCheckbox(checkboxId) {
    const checkbox = document.getElementById(checkboxId);
    if (!checkbox) return;

    checkbox.checked = !checkbox.checked;
    // Имитируем событие изменения, чтобы обновить счетчик
    checkbox.dispatchEvent(new Event('change'));

    // Показываем уведомление для аллергенов
    const allergenItem = checkbox.closest('.allergen-item');
    if (allergenItem) {
        const allergenName = allergenItem.querySelector('.fw-bold')?.textContent;
        if (allergenName) {
            const action = checkbox.checked ? 'добавлен' : 'удален';
            showNotification('Аллергены', `Аллерген "${allergenName}" ${action}`, 'info');
        }
    }
}

// Функция для обновления счетчика аллергенов
function updateCount(type, isChecked) {
    const countElement = document.getElementById(`${type}-count`);
    if (countElement) {
        let currentCount = parseInt(countElement.textContent.split(': ')[1]);
        if (isChecked) {
            currentCount++;
        } else {
            currentCount--;
        }
        countElement.textContent = `Всего: ${currentCount}`;
    }
}

// Функции для работы с балансом
function showTopUpModal() {
    const modal = document.getElementById('topUpModal');
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeTopUpModal() {
    const modal = document.getElementById('topUpModal');
    if (modal) {
        modal.style.display = 'none';
        const amountInput = document.getElementById('topUpAmount');
        if (amountInput) amountInput.value = '';
    }
}

function setAmount(amount) {
    const amountInput = document.getElementById('topUpAmount');
    if (amountInput) {
        amountInput.value = amount;
    }
}

function topUpBalance() {
    const amountInput = document.getElementById('topUpAmount');
    if (!amountInput) return;

    const amount = parseFloat(amountInput.value);

    if (!amount || amount < 10 || amount > 10000) {
        showNotification('Ошибка', 'Пожалуйста, введите корректную сумму (от 10 до 10000 руб)', 'error');
        return;
    }

    // Отправляем AJAX запрос на пополнение баланса
    fetch('/student/top-up-balance/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `amount=${amount}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Обновляем баланс на странице
            const balanceElement = document.getElementById('balanceAmount');
            if (balanceElement) {
                balanceElement.textContent = data.new_balance.toFixed(2);
            }

            // Обновляем баланс в сайдбаре
            const sidebarBalance = document.querySelector('.user-balance strong');
            if (sidebarBalance) {
                sidebarBalance.textContent = data.new_balance.toFixed(2);
            }

            showNotification('Успешно', data.message, 'success');
            closeTopUpModal();
        } else {
            showNotification('Ошибка', data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка', 'Произошла ошибка при пополнении баланса', 'error');
    });
}

// Функция для обработки формы смены пароля
function initPasswordForm() {
    const passwordForm = document.getElementById('passwordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);

            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Успех', 'Пароль успешно изменен', 'success');
                    this.reset();
                } else {
                    showNotification('Ошибка', data.error || 'Ошибка при смене пароля', 'error');
                }
            })
            .catch(error => {
                showNotification('Ошибка', 'Произошла ошибка', 'error');
            });
        });
    }
}

// Функция для обработки формы удаления аккаунта
function initDeleteAccountForm() {
    const deleteForm = document.querySelector('form[onsubmit*="delete_account"]');
    if (deleteForm) {
        deleteForm.addEventListener('submit', function(e) {
            if (!confirm('Вы уверены, что хотите удалить свой аккаунт? Это действие нельзя отменить!')) {
                e.preventDefault();
                return;
            }

            // Показать уведомление о начале удаления
            showNotification('Информация', 'Начинается удаление аккаунта...', 'warning');
        });
    }
}

// Функция для обработки заказа с уведомлением
function handleOrder(cardId, cardTitle) {
    fetch(`/student/order/create/${cardId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Успех', `Блюдо "${cardTitle}" добавлено в заказы!`, 'success');
            // Обновить счетчик заказов в сайдбаре
            const badge = document.querySelector('.sidebar-menu a[href*="student_my_orders"] .badge');
            if (badge) {
                badge.textContent = parseInt(badge.textContent || '0') + 1;
            }
        } else {
            showNotification('Ошибка', data.error || 'Не удалось добавить заказ', 'error');
        }
    })
    .catch(error => {
        showNotification('Ошибка', 'Произошла ошибка при заказе', 'error');
    });
}

// Функция для обработки успешного сохранения аллергенов
function handleAllergenSave(form, type) {
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const typeName = type === 'critical' ? 'критических' : 'некритических';
                showNotification('Успех', `${data.count} ${typeName} аллергенов сохранено`, 'success');

                // Обновляем счетчик на странице
                const counterElement = document.getElementById(`${type}-count`);
                if (counterElement) {
                    counterElement.textContent = `Всего: ${data.count}`;
                }
            } else {
                showNotification('Ошибка', data.error || 'Произошла ошибка', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Ошибка', 'Произошла ошибка при сохранении', 'error');
        });
    });
}


// Функция для отметки заказа как полученного
function markOrderReceived(orderId) {
    showNotification('Информация', 'Заказ помечен как полученный', 'success');
}

// Функция для фильтрации блюд по типу
function showMeals(mealType) {
    const dishItems = document.querySelectorAll('.dish-item');

    dishItems.forEach(item => {
        if (mealType === 'Все' || item.dataset.mealType === mealType) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// Функции для отчетов (добавлены)
function generateReport(period) {
    console.log('Генерация отчета за период:', period);
    showNotification('Информация', `Генерация отчета за ${period}...`, 'info');
}

function viewDayDetails(date) {
    console.log('Просмотр деталей дня:', date);
    showNotification('Информация', `Просмотр деталей дня ${date}...`, 'info');
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Подсчитываем начальное количество выбранных аллергенов
    let criticalCount = 0;
    let noncriticalCount = 0;

    // Для критических
    document.querySelectorAll('input[name="critical_allergens"]').forEach(cb => {
        if (cb.checked) criticalCount++;
    });

    // Для некритичных
    document.querySelectorAll('input[name="non_critical_allergens"]').forEach(cb => {
        if (cb.checked) noncriticalCount++;
    });

    // Обновляем отображение
    const criticalCountElement = document.getElementById('critical-count');
    const noncriticalCountElement = document.getElementById('noncritical-count');

    if (criticalCountElement) criticalCountElement.textContent = `Всего: ${criticalCount}`;
    if (noncriticalCountElement) noncriticalCountElement.textContent = `Всего: ${noncriticalCount}`;

    // Инициализация форм
    initPasswordForm();
    initDeleteAccountForm();

    // Инициализация форм аллергенов
    const criticalForm = document.querySelector('form[action*="update_critical_allergens"]');
    const noncriticalForm = document.querySelector('form[action*="update_non_critical_allergens"]');

    if (criticalForm) handleAllergenSave(criticalForm, 'critical');
    if (noncriticalForm) handleAllergenSave(noncriticalForm, 'noncritical');

    // Автоматическое скрытие сообщений Django
    const alerts = document.querySelectorAll('.messages .alert');
    alerts.forEach(alert => {
        // Автоматическое скрытие через 5 секунд
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Сворачивание/разворачивание сайдбара
    const sidebarCollapseBtn = document.querySelector('.sidebar-collapse-btn');
    const sidebar = document.querySelector('.sidebar');
    const body = document.body;

    if (sidebarCollapseBtn && sidebar) {
        // Проверяем сохранённое состояние
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';

        // Устанавливаем начальное состояние
        if (isCollapsed) {
            sidebar.classList.add('collapsed');
            body.classList.add('sidebar-collapsed');
        }

        // Обработчик клика по стрелочке
        sidebarCollapseBtn.addEventListener('click', function () {
            sidebar.classList.toggle('collapsed');
            body.classList.toggle('sidebar-collapsed');

            // Сохраняем состояние в localStorage
            const isNowCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isNowCollapsed);
        });
    }
});

// Функция для обработки отметки "Я забрал"
function handleMarkReceived(event, form) {
    event.preventDefault(); // Останавливаем стандартную отправку

    // Показываем уведомление благодарности
    showNotification('Спасибо за заказ!', 'Ваш заказ был успешно получен. Приятного аппетита!', 'success');

    // Отправляем форму через AJAX
    fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (response.ok) {
            // Обновляем статус на странице
            setTimeout(() => {
                const orderItem = form.closest('.order-item');
                if (orderItem) {
                    const orderStatus = orderItem.querySelector('.order-status');
                    if (orderStatus) {
                        orderStatus.innerHTML = '<span class="badge bg-secondary">Получен</span>';
                    }
                    form.style.display = 'none'; // Скрываем кнопку
                }
            }, 500);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showNotification('Ошибка', 'Не удалось отметить заказ как полученный', 'error');
    });
}

// Сделайте функцию глобально доступной
window.handleMarkReceived = handleMarkReceived;
window.showNotification = showNotification;
window.showTopUpModal = showTopUpModal;
window.closeTopUpModal = closeTopUpModal;
window.setAmount = setAmount;
window.topUpBalance = topUpBalance;
window.toggleCheckbox = toggleCheckbox;
window.updateCount = updateCount;
window.showMeals = showMeals;
window.handleOrder = handleOrder;
window.markOrderReceived = markOrderReceived;
window.generateReport = generateReport;
window.viewDayDetails = viewDayDetails;