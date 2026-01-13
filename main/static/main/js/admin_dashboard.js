function approveRequest(button) {
    const requestItem = button.closest('.request-item');
    const productName = requestItem.querySelector('h4').textContent;

    requestItem.style.opacity = '0.7';
    setTimeout(() => {
        requestItem.remove();
        updateRequestCount();
    }, 300);

    alert(`Заявка на "${productName}" одобрена!`);
}

function rejectRequest(button) {
    const requestItem = button.closest('.request-item');
    const productName = requestItem.querySelector('h4').textContent;

    if (confirm(`Отклонить заявку на "${productName}"?`)) {
        requestItem.style.opacity = '0.7';
        setTimeout(() => {
            requestItem.remove();
            updateRequestCount();
        }, 300);
        alert('Заявка отклонена!');
    }
}

function processAllRequests() {
    if (confirm('Одобрить все заявки на согласование?')) {
        const requests = document.querySelectorAll('.request-item');
        requests.forEach(request => {
            request.style.opacity = '0.7';
            setTimeout(() => request.remove(), 300);
        });
        updateRequestCount();
        alert('Все заявки обработаны!');
    }
}

function updateRequestCount() {
    const badge = document.querySelector('.sidebar-menu .badge');
    const requests = document.querySelectorAll('.request-item').length;
    if (badge) {
        badge.textContent = requests;
    }
}

function generateReport(type) {
    const reports = {
        daily: 'Дневной отчет сгенерирован и отправлен на печать',
        weekly: 'Недельный отчет сгенерирован в формате PDF',
        monthly: 'Месячный отчет сгенерирован, открывается в новой вкладке'
    };

    alert(reports[type]);

    if (type === 'monthly') {
        window.open('#', '_blank');
    }
}

function viewDayDetails(date) {
    const modalContent = document.getElementById('modalContent');
    if (modalContent) {
        modalContent.innerHTML = `
            <h4>Детали за ${date}</h4>
            <div class="day-details">
                <div class="detail-item">
                    <strong>Всего пользователей:</strong> 156
                </div>
                <div class="detail-item">
                    <strong>Новых пользователей:</strong> 12
                </div>
                <div class="detail-item">
                    <strong>Заказов:</strong> 156 (84 завтрака, 72 обеда)
                </div>
                <div class="detail-item">
                    <strong>Выручка:</strong> 12,540 ₽
                </div>
                <div class="detail-item">
                    <strong>Популярные блюда:</strong>
                    <ul>
                        <li>Омлет с овощами - 45 заказов</li>
                        <li>Суп куриный - 38 заказов</li>
                        <li>Плов - 32 заказа</li>
                    </ul>
                </div>
                <div class="detail-item">
                    <strong>Среднее время обслуживания:</strong> 18 минут
                </div>
                <div class="detail-item">
                    <strong>Отзывы:</strong> 4.7/5 (28 отзывов)
                </div>
            </div>
        `;
    }

    const detailsModal = document.getElementById('detailsModal');
    if (detailsModal) {
        detailsModal.style.display = 'block';
    }
}

function printDetails() {
    window.print();
}

// Функция для открытия модального окна регистрации персонала
function openStaffModal() {
    const staffModal = document.getElementById('staffModal');
    if (staffModal) {
        staffModal.style.display = 'flex';

        // Скрыть ошибки при открытии окна
        const errorsContainer = document.getElementById('staffErrors');
        if (errorsContainer) {
            errorsContainer.style.display = 'none';
        }

        const errorList = document.getElementById('errorList');
        if (errorList) {
            errorList.innerHTML = '';
        }

        // Очистить поля формы при открытии
        const form = document.getElementById('staffForm');
        if (form) {
            form.reset();
        }
    }
}

// Функция для закрытия модального окна регистрации
function closeModal() {
    const staffModal = document.getElementById('staffModal');
    if (staffModal) {
        staffModal.style.display = 'none';

        // Скрыть ошибки при закрытии окна
        const errorsContainer = document.getElementById('staffErrors');
        if (errorsContainer) {
            errorsContainer.style.display = 'none';
        }

        const errorList = document.getElementById('errorList');
        if (errorList) {
            errorList.innerHTML = '';
        }
    }
}

// Функция для отображения ошибок регистрации
function showStaffErrors(errors) {
    const errorsContainer = document.getElementById('staffErrors');
    const errorList = document.getElementById('errorList');

    if (!errorsContainer || !errorList) return;

    // Очищаем предыдущие ошибки
    errorList.innerHTML = '';

    // Добавляем новые ошибки
    if (errors && errors.length > 0) {
        errors.forEach(error => {
            const li = document.createElement('li');
            li.textContent = error;
            errorList.appendChild(li);
        });

        // Показываем контейнер с ошибками
        errorsContainer.style.display = 'block';

        // Прокручиваем к ошибкам
        errorsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Функция для отображения успешной регистрации
function showSuccessModal(username, role) {
    const successUsername = document.getElementById('successUsername');
    const successRole = document.getElementById('successRole');

    if (!successUsername || !successRole) return;

    // Устанавливаем данные пользователя
    successUsername.textContent = username;

    // Преобразуем роль в читаемый формат
    const roleMap = {
        'chef': 'Повар',
        'admin': 'Администратор'
    };
    successRole.textContent = roleMap[role] || role;

    // Показываем модальное окно
    const successModal = document.getElementById('successModal');
    if (successModal) {
        successModal.style.display = 'flex';
    }
}

// Функция для закрытия модального окна успеха
function closeSuccessModal() {
    const successModal = document.getElementById('successModal');
    if (successModal) {
        successModal.style.display = 'none';
    }

    // Закрываем и модальное окно регистрации, если оно открыто
    closeModal();
}

// Функция для проверки формы на стороне клиента перед отправкой
function validateStaffForm() {
    const username = document.querySelector('#staffForm input[name="username"]');
    const password1 = document.querySelector('#staffForm input[name="password1"]');
    const password2 = document.querySelector('#staffForm input[name="password2"]');
    const role = document.querySelector('#staffForm select[name="role"]');

    const errors = [];

    if (!username || !username.value.trim()) {
        errors.push('Имя пользователя обязательно для заполнения');
    }

    if (!password1 || !password1.value) {
        errors.push('Пароль обязателен для заполнения');
    } else if (password1.value.length < 8) {
        errors.push('Пароль должен содержать минимум 8 символов');
    }

    if (!password2 || !password2.value) {
        errors.push('Подтверждение пароля обязательно');
    }

    if (password1 && password2 && password1.value !== password2.value) {
        errors.push('Пароли не совпадают');
    }

    if (!role || !role.value) {
        errors.push('Необходимо выбрать роль');
    }

    if (errors.length > 0) {
        showStaffErrors(errors);
        return false;
    }

    return true;
}

// Основная инициализация при загрузке документа
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing admin dashboard...');

    // Обработчик отправки формы регистрации персонала
    const staffForm = document.getElementById('staffForm');
    if (staffForm) {
        console.log('Staff form found');
        staffForm.addEventListener('submit', function(event) {
            console.log('Staff form submitted');
            // Отключаем стандартную валидацию для пользовательской
            if (!validateStaffForm()) {
                event.preventDefault();
                return false;
            }
        });
    } else {
        console.log('Staff form NOT found');
    }

    // Автоматически показываем модальное окно с ошибками, если они есть в форме
    const formErrors = document.querySelectorAll('.field-error');
    console.log('Form errors found:', formErrors.length);

    if (formErrors.length > 0) {
        // Собираем все ошибки из Django формы
        const djangoErrors = [];
        formErrors.forEach(errorElement => {
            if (errorElement.textContent && errorElement.textContent.trim()) {
                djangoErrors.push(errorElement.textContent.trim());
            }
        });

        if (djangoErrors.length > 0) {
            console.log('Opening modal with Django errors:', djangoErrors);
            // Открываем модальное окно и показываем ошибки
            openStaffModal();
            showStaffErrors(djangoErrors);
        }
    }

    // Проверяем, была ли успешная регистрация
    // Проверяем наличие элемента с данными или используем data-атрибуты
    const successElement = document.getElementById('registrationSuccessData');
    let registrationSuccess = false;
    let registeredUsername = '';
    let registeredRole = '';

    if (successElement) {
        registrationSuccess = successElement.dataset.success === 'true';
        registeredUsername = successElement.dataset.username || '';
        registeredRole = successElement.dataset.role || '';
    }

    console.log('Registration success:', registrationSuccess, 'Username:', registeredUsername);

    if (registrationSuccess && registeredUsername) {
        // Показываем окно успеха
        console.log('Showing success modal');
        showSuccessModal(registeredUsername, registeredRole);
    }

    // Инициализация других элементов (если они есть на странице)
    const closeModalButtons = document.querySelectorAll('.close-modal');
    if (closeModalButtons.length > 0) {
        closeModalButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const detailsModal = document.getElementById('detailsModal');
                if (detailsModal) {
                    detailsModal.style.display = 'none';
                }
            });
        });
    }
    console.log('Admin dashboard initialization complete');
});