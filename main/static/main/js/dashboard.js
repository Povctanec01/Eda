document.addEventListener('DOMContentLoaded', function () {
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
});

function showMeals(mealType) {
  const items = document.querySelectorAll('.dish-item');
  items.forEach(item => {
    if (mealType === 'Все' || item.dataset.mealType === mealType) {
      item.style.display = 'block';
    } else {
      item.style.display = 'none';
    }
  });
}

// По умолчанию показываем все блюда
document.addEventListener('DOMContentLoaded', () => {
  showMeals('Все');

  // Проверка совпадения паролей с проверкой на существование формы
  const passwordForm = document.getElementById('passwordForm');
  if (passwordForm) {
    passwordForm.addEventListener('submit', function(e) {
      const password1 = document.getElementById('new_password1');
      const password2 = document.getElementById('new_password2');

      if (!password1 || !password2) {
        console.warn('Поля пароля не найдены');
        return;
      }

      if (password1.value !== password2.value) {
        e.preventDefault();
        alert('Новые пароли не совпадают!');
        return false;
      }

      if (password1.value.length < 8) {
        e.preventDefault();
        alert('Пароль должен содержать минимум 8 символов!');
        return false;
      }
    });
  }
});
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