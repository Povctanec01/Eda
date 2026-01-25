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
    checkbox.checked = !checkbox.checked;
    // Имитируем событие изменения, чтобы обновить счетчик
    checkbox.dispatchEvent(new Event('change'));
}

// Функция для обновления счетчика
function updateCount(type, isChecked) {
    const countElement = document.getElementById(`${type}-count`);
    let currentCount = parseInt(countElement.textContent.split(': ')[1]);
    if (isChecked) {
        currentCount++;
    } else {
        currentCount--;
    }
    countElement.textContent = `Всего: ${currentCount}`;
}

// Инициализация счетчиков при загрузке страницы
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
    document.getElementById('critical-count').textContent = `Всего: ${criticalCount}`;
    document.getElementById('noncritical-count').textContent = `Всего: ${noncriticalCount}`;
});