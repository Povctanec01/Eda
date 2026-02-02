document.addEventListener('DOMContentLoaded', function () {
    //1Переключение темы
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

    //2 Генерация отчётов
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

    //3 Просмотр деталей дня
    const viewDetailsBtns = document.querySelectorAll('.view-details-btn');
    if (viewDetailsBtns.length > 0) {
        viewDetailsBtns.forEach(btn => {
            btn.addEventListener('click', function () {
                const date = this.dataset.date;
                window.location.href = `/admin/statistics/details/${date}/`;
            });
        });
    }

    //4 Закрытие модальных окон
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

    //5 Вспомогательная функция для CSRF
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

    //6 Управление списком пользователей
    const searchInput = document.getElementById('userSearch');
    const deleteBtn = document.getElementById('deleteSelectedBtn');
    const userItems = document.querySelectorAll('.allergen-item.user-item');
    const resultsCount = document.getElementById('resultsCount');
    const searchResultsInfo = document.getElementById('searchResultsInfo');
    const totalUsersCount = document.getElementById('totalUsersCount');

    // Сохраняем оригинальные данные пользователей для поиска
    const userData = [];
    userItems.forEach(item => {
        const username = item.querySelector('.allergen-name').textContent.trim();
        userData.push({
            element: item,
            username: username.toLowerCase()
        });
        item.style.display = 'flex';
    });

    //Фильтрация
    function filterUsers(query) {
        if (!query.trim()) {
            //Если поиск пустой — показываем всех
            userData.forEach(user => {
                user.element.style.display = 'flex';
            });
            searchResultsInfo.style.display = 'none';
            resultsCount.textContent = totalUsersCount.textContent;
            return;
        }

        const searchTerm = query.toLowerCase().trim();
        let visibleCount = 0;

        userData.forEach(user => {
            if (user.username.includes(searchTerm)) {
                user.element.style.display = 'flex';
                visibleCount++;
            } else {
                user.element.style.display = 'none';
            }
        });

        //Счётчик
        resultsCount.textContent = visibleCount;
        searchResultsInfo.style.display = 'block';

        // Если нет результатов — показываем сообщение
        const noResults = document.querySelector('.no-results-placeholder');
        if (visibleCount === 0) {
            if (!noResults) {
                const noResultsMsg = document.createElement('div');
                noResultsMsg.className = 'no-results-placeholder';
                noResultsMsg.innerHTML = '<i class="fas fa-search"></i> Пользователи не найдены';
                document.querySelector('.allergens-scrollable').appendChild(noResultsMsg);
            }
        } else if (noResults) {
            noResults.remove();
        }

        updateDeleteButton();
    }

    //Обработчик ввода
    if (searchInput) {
        searchInput.addEventListener('input', function (e) {
            filterUsers(e.target.value);
        });
    }
    userItems.forEach(item => {
        item.addEventListener('click', function (e) {
            // Не переключаем чекбокс, если кликнули по самому чекбоксу или роли
            if (e.target.classList.contains('user-checkbox') ||
                e.target.closest('.user-role-badge')) {
                return;
            }
            const checkbox = this.querySelector('.user-checkbox');
            if (checkbox) {
                checkbox.checked = !checkbox.checked;
                updateUserItemSelection(this, checkbox.checked);
                updateDeleteButton();
            }
        });
    });

    //Синхронизация чекбокса и выделения карточки
    document.addEventListener('change', function (e) {
        if (e.target.classList.contains('user-checkbox')) {
            const item = e.target.closest('.user-item');
            if (item) {
                updateUserItemSelection(item, e.target.checked);
                updateDeleteButton();
            }
        }
    });

    //Обновления выделения карточки
    function updateUserItemSelection(item, isSelected) {
        if (isSelected) {
            item.classList.add('selected');
        } else {
            item.classList.remove('selected');
        }
    }

    //Обновления состояния кнопки удаления
    function updateDeleteButton() {
        const checkboxes = document.querySelectorAll('.user-checkbox:checked');
        if (deleteBtn) {
            deleteBtn.disabled = checkboxes.length === 0;
        }
    }


    // Удаление выбранных пользователей
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const selectedUsernames = Array.from(document.querySelectorAll('.user-checkbox:checked'))
                .map(cb => cb.value);

            if (selectedUsernames.length === 0) {
                alert('Пожалуйста, выберите хотя бы одного пользователя для удаления.');
                return;
            }

            // ПРОВЕРКА: нельзя удалить себя
            if (selectedUsernames.includes('{{ request.user.username }}')) {
                alert('Нельзя удалить свой собственный аккаунт!');
                return;
            }
            if (!confirmUserDeletion(selectedUsernames)) {
                return;
            }

            if (!confirm(`Вы уверены, что хотите удалить ${selectedUsernames.length} пользователей? Это действие нельзя отменить!`)) {
                return;
            }

            const deleteUrl = deleteBtn.dataset.deleteUrl;
            const csrfToken = getCookie('csrftoken');
            if (!csrfToken) {
                alert('Ошибка CSRF токена. Пожалуйста, обновите страницу.');
                return;
            }

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
        });
    }

    updateDeleteButton();

});

function toggleVisibilityFilter() { //функция для фильтрации скрытых блюд
    const items = document.querySelectorAll('.dish-item');
    const showHiddenOnly = true;

    items.forEach(item => {
        const isHidden = item.getAttribute('data-hidden') === 'true';
        item.style.display = showHiddenOnly ? (isHidden ? 'block' : 'none') : 'block';
    });
}
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

    if (adminUsernames.length > 0) {
        message += `\n\n⚠️ Внимание! Среди выбранных есть администраторы:\n${adminUsernames.join(', ')}\n\nИх удаление может нарушить работу системы.`;
    }

    return confirm(message);
}