// ============================================
// ОСНОВНЫЕ УТИЛИТЫ И ХЕЛПЕРЫ
// ============================================

// Получение CSRF токена
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

// Функция для показа уведомлений
function showNotification(title, message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `floating-notification ${type}`;

    const typeIcons = {
        'success': 'fa-check-circle',
        'error': 'fa-times-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };

    notification.innerHTML = `
        <div class="notification-header">
            <div class="d-flex align-items-center">
                <i class="fas ${typeIcons[type] || 'fa-info-circle'} me-2"></i>
                <h6 class="notification-title mb-0">${title}</h6>
            </div>
            <button class="notification-close" onclick="this.parentElement.parentElement.classList.add('fade-out')">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <p class="notification-content">${message}</p>
    `;

    document.body.appendChild(notification);

    // Показать с анимацией
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Глобальная функция для AJAX действий
function handleAdminAction(url, method = 'POST', data = {}, successMessage, errorMessage) {
    const csrfToken = getCookie('csrftoken');

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Успех', successMessage || data.message, 'success');
            if (data.redirect) {
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 1000);
            }
        } else {
            showNotification('Ошибка', errorMessage || data.error || 'Произошла ошибка', 'error');
        }
    })
    .catch(error => {
        showNotification('Ошибка', 'Произошла ошибка при выполнении действия', 'error');
        console.error('Error:', error);
    });
}

// ============================================
// ФУНКЦИИ ДЛЯ УПРАВЛЕНИЯ ПОЛЬЗОВАТЕЛЯМИ
// ============================================

// Обновление выделения карточки пользователя
function updateUserItemSelection(item, isSelected) {
    if (isSelected) {
        item.classList.add('selected');
    } else {
        item.classList.remove('selected');
    }
}

// Обновление состояния кнопки удаления
function updateDeleteButton() {
    const deleteBtn = document.getElementById('deleteSelectedBtn');
    if (deleteBtn) {
        const checkboxes = document.querySelectorAll('.user-checkbox:checked');
        deleteBtn.disabled = checkboxes.length === 0;
    }
}

// Подтверждение удаления пользователей
function confirmUserDeletion(selectedUsernames) {
    const adminUsernames = [];
    const superuserUsernames = [];

    // Проверить, нет ли среди выбранных администраторов
    selectedUsernames.forEach(username => {
        const userItem = document.querySelector(`.user-item[data-username="${username}"]`);
        if (userItem) {
            const roleBadge = userItem.querySelector('.badge');
            if (roleBadge && roleBadge.textContent.includes('Администратор')) {
                adminUsernames.push(username);
            }
        }
    });

    let message = `Вы уверены, что хотите удалить ${selectedUsernames.length} пользователей?`;
    let hasWarnings = false;

    if (adminUsernames.length > 0) {
        message += `\n\n⚠️ Внимание! Среди выбранных есть администраторы:\n${adminUsernames.join(', ')}\n\nИх удаление может нарушить работу системы.`;
        hasWarnings = true;
    }

    // Создаем модальное окно с уведомлением
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'block';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h3>Подтверждение удаления</h3>
                <button class="close-btn" onclick="this.closest('.modal').style.display='none'">&times;</button>
            </div>
            <div class="modal-body">
                <p>${message.replace(/\n/g, '<br>')}</p>
                ${hasWarnings ? '<div class="alert alert-warning"><i class="fas fa-exclamation-triangle"></i> Это действие может повлиять на работу системы</div>' : ''}
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="this.closest('.modal').style.display='none'">Отмена</button>
                <button class="btn btn-danger" id="confirmDeleteBtn">Удалить</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    document.getElementById('confirmDeleteBtn').addEventListener('click', function() {
        modal.style.display = 'none';
        performUserDeletion(selectedUsernames);
    });

    return false; // Отменяем стандартное подтверждение
}

// Выполнение удаления пользователей
function performUserDeletion(selectedUsernames) {
    const deleteBtn = document.getElementById('deleteSelectedBtn');
    if (!deleteBtn) return;

    const deleteUrl = deleteBtn.dataset.deleteUrl;
    const csrfToken = getCookie('csrftoken');

    if (!csrfToken) {
        showNotification('Ошибка', 'Ошибка CSRF токена. Пожалуйста, обновите страницу.', 'error');
        return;
    }

    showNotification('Информация', `Удаление ${selectedUsernames.length} пользователей...`, 'info');

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = deleteUrl;

    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);

    selectedUsernames.forEach(username => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'usernames[]';
        input.value = username;
        form.appendChild(input);
    });

    document.body.appendChild(form);
    form.submit();
}

// Фильтрация пользователей
function filterUsers(query) {
    const userItems = document.querySelectorAll('.allergen-item.user-item');
    const resultsCount = document.getElementById('resultsCount');
    const searchResultsInfo = document.getElementById('searchResultsInfo');
    const totalUsersCount = document.getElementById('totalUsersCount');

    if (!query.trim()) {
        // Если поиск пустой — показываем всех
        userItems.forEach(item => {
            item.style.display = 'flex';
        });
        if (searchResultsInfo) {
            searchResultsInfo.style.display = 'none';
        }
        if (resultsCount) {
            resultsCount.textContent = totalUsersCount ? totalUsersCount.textContent : '0';
        }
        return;
    }

    const searchTerm = query.toLowerCase().trim();
    let visibleCount = 0;

    userItems.forEach(item => {
        const usernameElement = item.querySelector('.allergen-name');
        if (usernameElement) {
            const username = usernameElement.textContent.toLowerCase().trim();
            if (username.includes(searchTerm)) {
                item.style.display = 'flex';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        }
    });

    // Обновление счетчика
    if (resultsCount) {
        resultsCount.textContent = visibleCount;
    }
    if (searchResultsInfo) {
        searchResultsInfo.style.display = 'block';
    }

    // Если нет результатов — показываем сообщение
    const scrollableContainer = document.querySelector('.allergens-scrollable');
    if (scrollableContainer) {
        let noResults = scrollableContainer.querySelector('.no-results-placeholder');
        if (visibleCount === 0) {
            if (!noResults) {
                noResults = document.createElement('div');
                noResults.className = 'no-results-placeholder';
                noResults.innerHTML = '<i class="fas fa-search"></i> Пользователи не найдены';
                scrollableContainer.appendChild(noResults);
            }
        } else if (noResults) {
            noResults.remove();
        }
    }

    updateDeleteButton();
}

// Добавление нового пользователя в список
function addUserToList(userData) {
    const container = document.querySelector('.allergens-scrollable');
    const userCount = document.getElementById('totalUsersCount');

    if (!container || !userCount) return;

    const currentCount = parseInt(userCount.textContent) || 0;

    const userItem = document.createElement('div');
    userItem.className = 'allergen-item user-item';
    userItem.setAttribute('data-username', userData.username);

    userItem.innerHTML = `
        <div class="user-checkbox-wrapper">
            <input type="checkbox" class="user-checkbox form-check-input" value="${userData.username}" id="user-new">
        </div>
        <div class="allergen-info">
            <div class="allergen-name">${userData.username}</div>
            <div class="allergen-id">ID: ${userData.id}</div>
        </div>
        <div class="user-role-badge">
            <span class="badge ${getRoleBadgeClass(userData.role)}">
                ${userData.role_display || userData.role}
            </span>
        </div>
    `;

    // Вставляем в начало списка
    if (container.firstChild) {
        container.insertBefore(userItem, container.firstChild);
    } else {
        container.appendChild(userItem);
    }

    // Обновляем счетчик
    userCount.textContent = currentCount + 1;

    // Добавляем обработчики событий
    addUserItemListeners(userItem);
}

// Получение класса для бейджа роли
function getRoleBadgeClass(role) {
    switch(role) {
        case 'student': return 'bg-primary';
        case 'chef': return 'bg-success';
        case 'admin': return 'bg-danger';
        default: return 'bg-secondary';
    }
}

// Добавление обработчиков для элементов пользователей
function addUserItemListeners(item) {
    item.addEventListener('click', function(e) {
        if (!e.target.classList.contains('user-checkbox') &&
            !e.target.closest('.user-role-badge')) {
            const checkbox = this.querySelector('.user-checkbox');
            if (checkbox) {
                checkbox.checked = !checkbox.checked;
                updateUserItemSelection(this, checkbox.checked);
                updateDeleteButton();
            }
        }
    });

    const checkbox = item.querySelector('.user-checkbox');
    if (checkbox) {
        checkbox.addEventListener('change', function() {
            updateUserItemSelection(item, this.checked);
            updateDeleteButton();
        });
    }
}

// ============================================
// ФУНКЦИИ ДЛЯ УПРАВЛЕНИЯ БЛЮДАМИ
// ============================================

// Обработка действий с закупками
function handleBuyAction(buyId, action, title) {
    const actionText = action === 'approve' ? 'принять' : 'отклонить';

    if (!confirm(`Вы уверены, что хотите ${actionText} закупку "${title}"?`)) {
        return;
    }

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = window.location.href;

    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = getCookie('csrftoken');
    form.appendChild(csrfInput);

    const actionInput = document.createElement('input');
    actionInput.type = 'hidden';
    actionInput.name = 'action';
    actionInput.value = action;
    form.appendChild(actionInput);

    const buyIdInput = document.createElement('input');
    buyIdInput.type = 'hidden';
    buyIdInput.name = 'buy_id';
    buyIdInput.value = buyId;
    form.appendChild(buyIdInput);

    document.body.appendChild(form);
    form.submit();

    showNotification('Информация', `Закупка "${title}" обрабатывается...`, 'info');
}

// Удаление блюда или закупки
function handleDeleteCard(cardId, title, isBuy = false) {
    if (!confirm(`Вы уверены, что хотите удалить "${title}"?`)) {
        return;
    }

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = window.location.href;

    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = getCookie('csrftoken');
    form.appendChild(csrfInput);

    const deleteInput = document.createElement('input');
    deleteInput.type = 'hidden';
    deleteInput.name = 'delete';
    deleteInput.value = '1';
    form.appendChild(deleteInput);

    const cardIdInput = document.createElement('input');
    cardIdInput.type = 'hidden';
    cardIdInput.name = isBuy ? 'card_id_buys' : 'card_id';
    cardIdInput.value = cardId;
    form.appendChild(cardIdInput);

    document.body.appendChild(form);
    form.submit();

    showNotification('Информация', `"${title}" удаляется...`, 'info');
}

// Переключение видимости блюда
function handleToggleVisibility(cardId, title, isHidden) {
    const action = isHidden ? 'показать' : 'скрыть';

    if (!confirm(`Вы уверены, что хотите ${action} "${title}"?`)) {
        return;
    }

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = window.location.href;

    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = getCookie('csrftoken');
    form.appendChild(csrfInput);

    const toggleInput = document.createElement('input');
    toggleInput.type = 'hidden';
    toggleInput.name = 'toggle_visibility';
    toggleInput.value = '1';
    form.appendChild(toggleInput);

    const cardIdInput = document.createElement('input');
    cardIdInput.type = 'hidden';
    cardIdInput.name = 'card_id';
    cardIdInput.value = cardId;
    form.appendChild(cardIdInput);

    document.body.appendChild(form);
    form.submit();

    showNotification('Информация', `"${title}" ${action}...`, 'info');
}

// Фильтрация скрытых блюд
function toggleVisibilityFilter() {
    const items = document.querySelectorAll('.dish-item');
    const toggleText = document.getElementById('visibilityToggleText');

    if (!toggleText) return;

    const showHiddenOnly = toggleText.textContent === 'Показать скрытые';

    items.forEach(item => {
        const isHidden = item.getAttribute('data-hidden') === 'true';
        item.style.display = showHiddenOnly ? (isHidden ? 'block' : 'none') : 'block';
    });

    toggleText.textContent = showHiddenOnly ? 'Показать все' : 'Показать скрытые';
}

// Фильтрация по типу еды
function showMeals(type) {
    const items = document.querySelectorAll('.dish-item');
    items.forEach(item => {
        const mealType = item.getAttribute('data-meal-type');
        if (type === 'Все' || mealType === type) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// ============================================
// ФУНКЦИИ ДЛЯ НАСТРОЕК
// ============================================

// Обработка формы смены пароля
function handlePasswordForm() {
    const passwordForm = document.getElementById('passwordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);

            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
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
                showNotification('Ошибка', 'Произошла ошибка при смене пароля', 'error');
            });
        });
    }
}

// Обработка формы поведения при входе
function handleAutoRedirectForm() {
    const autoRedirectForm = document.querySelector('form:not(#passwordForm)');
    if (autoRedirectForm && autoRedirectForm.querySelector('input[name="auto_redirect"]')) {
        autoRedirectForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);

            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Успех', 'Настройки сохранены', 'success');
                } else {
                    showNotification('Ошибка', data.error || 'Ошибка при сохранении настроек', 'error');
                }
            })
            .catch(error => {
                showNotification('Ошибка', 'Произошла ошибка при сохранении настроек', 'error');
            });
        });
    }
}

// Обработка удаления аккаунта
function handleDeleteAccountForm() {
    const deleteAccountForm = document.querySelector('form[action*="admin_settings"]:not(#passwordForm)');
    if (deleteAccountForm) {
        deleteAccountForm.addEventListener('submit', function(e) {
            e.preventDefault();

            if (confirm('Вы уверены, что хотите удалить свой аккаунт? Это действие нельзя отменить!')) {
                showNotification('Внимание', 'Начинается удаление аккаунта...', 'warning');
                this.submit();
            }
        });
    }
}

// ============================================
// ФУНКЦИИ ДЛЯ ОТЧЕТОВ И АНАЛИТИКИ
// ============================================

// Генерация отчетов
function generateReport(period) {
    const periodText = {
        'daily': 'дневной',
        'weekly': 'недельный',
        'monthly': 'месячный'
    }[period] || period;

    showNotification('Информация', `Генерация ${periodText} отчета...`, 'info');

    // Здесь можно добавить AJAX запрос для генерации отчета
    setTimeout(() => {
        showNotification('Успех', `${periodText} отчет успешно сгенерирован`, 'success');
    }, 1500);
}

// Просмотр деталей дня
function viewDayDetails(date) {
    // Реализация просмотра деталей дня
    showNotification('Информация', `Загрузка деталей за ${date}...`, 'info');
}

// Печать деталей
function printDetails() {
    window.print();
}

// ============================================
// ОСНОВНОЙ КОД ПРИ ЗАГРУЗКЕ СТРАНИЦЫ
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // 1. Переключение темы
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        themeToggle.checked = (savedTheme === 'dark');
        themeToggle.addEventListener('change', function() {
            const newTheme = this.checked ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    // 2. Автоматическое скрытие сообщений Django
    const alerts = document.querySelectorAll('.messages .alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // 3. Управление списком пользователей
    const searchInput = document.getElementById('userSearch');
    const deleteBtn = document.getElementById('deleteSelectedBtn');
    const userItems = document.querySelectorAll('.allergen-item.user-item');

    // Инициализация данных пользователей для поиска
    if (userItems.length > 0) {
        userItems.forEach(item => {
            addUserItemListeners(item);
        });
    }

    // Обработчик поиска
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            filterUsers(e.target.value);
        });
    }

    // Обработчик удаления выбранных пользователей
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function(e) {
            e.preventDefault();

            const selectedUsernames = Array.from(document.querySelectorAll('.user-checkbox:checked'))
                .map(cb => cb.value);

            if (selectedUsernames.length === 0) {
                showNotification('Ошибка', 'Пожалуйста, выберите хотя бы одного пользователя для удаления.', 'warning');
                return;
            }

            // ПРОВЕРКА: нельзя удалить себя
            const currentUser = document.body.getAttribute('data-current-user');
            if (currentUser && selectedUsernames.includes(currentUser)) {
                showNotification('Ошибка', 'Нельзя удалить свой собственный аккаунт!', 'error');
                return;
            }

            // Используем модальное окно вместо стандартного confirm
            confirmUserDeletion(selectedUsernames);
        });
    }

    // 4. Обработка форм добавления сотрудников
    const staffForm = document.querySelector('form[method="post"]');
    if (staffForm && staffForm.querySelector('input[name="username"]')) {
        staffForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);

            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Успех', 'Сотрудник успешно создан', 'success');
                    this.reset();

                    // Обновить список пользователей
                    if (data.user_data) {
                        addUserToList(data.user_data);
                    }
                } else {
                    showNotification('Ошибка', data.error || 'Ошибка при создании сотрудника', 'error');
                }
            })
            .catch(error => {
                showNotification('Ошибка', 'Произошла ошибка при создании сотрудника', 'error');
                console.error('Error:', error);
            });
        });
    }

    // 5. Обработка форм управления блюдами и закупками
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            // Для форм удаления блюд
            if (this.querySelector('input[name="delete"]')) {
                e.preventDefault();
                const cardIdInput = this.querySelector('input[name="card_id"], input[name="card_id_buys"]');
                if (cardIdInput) {
                    const cardId = cardIdInput.value;
                    const isBuy = cardIdInput.name === 'card_id_buys';

                    // Находим название блюда
                    const dishItem = this.closest('.dish-item');
                    const title = dishItem ? dishItem.querySelector('h3').textContent.trim() : 'элемент';

                    handleDeleteCard(cardId, title, isBuy);
                }
            }

            // Для форм подтверждения/отклонения закупок
            const actionInput = this.querySelector('input[name="action"]');
            if (actionInput && this.querySelector('input[name="buy_id"]')) {
                e.preventDefault();
                const action = actionInput.value;
                const buyId = this.querySelector('input[name="buy_id"]').value;
                const dishItem = this.closest('.dish-item');
                const title = dishItem ? dishItem.querySelector('h3').textContent.trim() : 'закупку';

                handleBuyAction(buyId, action, title);
            }

            // Для форм переключения видимости
            if (this.querySelector('input[name="toggle_visibility"]')) {
                e.preventDefault();
                const cardId = this.querySelector('input[name="card_id"]').value;
                const dishItem = this.closest('.dish-item');
                const title = dishItem ? dishItem.querySelector('h3').textContent.trim() : 'блюдо';
                const isHidden = dishItem ? dishItem.querySelector('.badge.bg-warning') : false;

                handleToggleVisibility(cardId, title, !!isHidden);
            }
        });
    });

    // 6. Обработка кнопок генерации отчетов
    const reportBtns = document.querySelectorAll('.report-btn, .btn[onclick*="generateReport"]');
    reportBtns.forEach(btn => {
        const originalOnClick = btn.getAttribute('onclick');
        if (originalOnClick && originalOnClick.includes('generateReport')) {
            btn.removeAttribute('onclick');
            btn.addEventListener('click', function() {
                const periodMatch = originalOnClick.match(/generateReport\('(.+?)'\)/);
                const period = periodMatch ? periodMatch[1] : 'daily';
                generateReport(period);
            });
        }
    });

    // 7. Обработка настроек
    handlePasswordForm();
    handleAutoRedirectForm();
    handleDeleteAccountForm();

    // 8. Инициализация кнопок фильтрации блюд
    const visibilityToggle = document.getElementById('visibilityToggleText');
    if (visibilityToggle) {
        window.toggleVisibilityFilter = toggleVisibilityFilter;
    }

    // 9. Инициализация кнопок фильтрации по типу еды
    const mealButtons = document.querySelectorAll('[onclick*="showMeals"]');
    mealButtons.forEach(btn => {
        const originalOnClick = btn.getAttribute('onclick');
        if (originalOnClick && originalOnClick.includes('showMeals')) {
            btn.removeAttribute('onclick');
            const typeMatch = originalOnClick.match(/showMeals\('(.+?)'\)/);
            const type = typeMatch ? typeMatch[1] : 'Все';
            btn.addEventListener('click', () => showMeals(type));
        }
    });

    // 10. Закрытие модальных окон
    const closeModalButtons = document.querySelectorAll('.close-modal, .modal-close');
    closeModalButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    });

    // 11. Обновление даты на главной странице
    const currentDateElement = document.getElementById('currentDate');
    if (currentDateElement) {
        const now = new Date();
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        currentDateElement.textContent = now.toLocaleDateString('ru-RU', options);
    }

    // Обновляем кнопку удаления при загрузке
    updateDeleteButton();
});

// Делаем функции глобально доступными
window.showNotification = showNotification;
window.handleAdminAction = handleAdminAction;
window.confirmUserDeletion = confirmUserDeletion;
window.performUserDeletion = performUserDeletion;
window.toggleVisibilityFilter = toggleVisibilityFilter;
window.showMeals = showMeals;
window.generateReport = generateReport;
window.viewDayDetails = viewDayDetails;
window.printDetails = printDetails;