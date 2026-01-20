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