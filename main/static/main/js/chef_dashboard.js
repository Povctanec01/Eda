
let currentRequest = null;
let currentDish = null;

function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('show');
}

function showSection(sectionId) {
    document.querySelectorAll('.dashboard-section').forEach(section => {
        section.classList.remove('active');
    });
    document.querySelectorAll('.sidebar-menu a').forEach(link => {
        link.classList.remove('active');
    });

    document.getElementById(sectionId).classList.add('active');
    event.target.closest('a').classList.add('active');
}

function showNotifications() {
    alert('У вас 5 новых уведомлений:\n1. Новая заявка на закупку одобрена\n2. Критически мало молока\n3. Новые заказы ожидают приготовления\n4. Статистика за неделю готова\n5. Напоминание о инвентаризации');
}

function toggleKitchenStatus() {
    const indicator = document.querySelector('.status-indicator');
    const statusText = document.querySelector('.kitchen-status span:nth-child(2)');

    if (indicator.classList.contains('active')) {
        indicator.classList.remove('active');
        indicator.style.background = '#dc3545';
        statusText.textContent = 'Кухня закрыта';
        alert('Кухня переведена в режим "Закрыто"');
    } else {
        indicator.classList.add('active');
        indicator.style.background = '#28a745';
        statusText.textContent = 'Кухня работает';
        alert('Кухня переведена в режим "Работает"');
    }
}

function showDailyStats() {
    alert('Статистика за сегодня:\n\nПриготовлено блюд: 24\nЗавтраков: 12\nОбедов: 12\nСреднее время приготовления: 15 мин\nПопулярное блюдо: Омлет с овощами');
}

function optimizeTime() {
    alert('Советы по оптимизации времени:\n1. Подготовьте ингредиенты заранее\n2. Используйте несколько плит одновременно\n3. Сортируйте заказы по типу блюд\n4. Автоматизируйте простые процессы');
}

function markPrepared(orderNumber) {
    const orderItem = document.querySelector(`[data-order="${orderNumber}"]`);
    const student = orderItem.querySelector('.student-info span').textContent;
    const dish = orderItem.querySelector('h4').textContent;

    orderItem.querySelector('.badge').textContent = 'Готово';
    orderItem.querySelector('.badge').className = 'badge bg-green';
    orderItem.querySelector('.btn-success').disabled = true;
    orderItem.querySelector('.btn-success').innerHTML = '<i class="fas fa-check"></i> Готово';
    orderItem.querySelector('.btn-success').classList.remove('btn-success');
    orderItem.querySelector('.btn-success').classList.add('btn-secondary');

    updateOrdersCount(-1);
    alert(`Заказ #${orderNumber} для ${student} (${dish}) отмечен как готовый!`);
}

function markAllPrepared() {
    if (confirm('Отметить все заказы как готовые?')) {
        const orders = document.querySelectorAll('.orders-list .order-item');
        orders.forEach(order => {
            const orderNumber = order.dataset.order;
            markPrepared(orderNumber);
        });
        alert('Все заказы отмечены как готовые!');
    }
}

function updateOrdersCount(change) {
    const badge = document.getElementById('ordersBadge');
    let current = parseInt(badge.textContent);
    current += change;
    if (current < 0) current = 0;
    badge.textContent = current;
}

function requestProduct(name, amount, stock) {
    document.getElementById('productName').value = name;

    const match = amount.match(/(\d+)\s*(кг|л|шт)/);
    if (match) {
        document.getElementById('productQuantity').value = match[1];
        document.getElementById('productUnit').value = match[2];
    }

    document.getElementById('purchaseReason').value = `Низкий запас продукта. Текущий остаток: ${amount} (${stock} от нормы)`;

    if (parseInt(stock) <= 20) {
        document.querySelector('input[name="priority"][value="critical"]').checked = true;
    } else if (parseInt(stock) <= 40) {
        document.querySelector('input[name="priority"][value="high"]').checked = true;
    }

    updatePriority();
    openPurchaseModal();
}

function openPurchaseModal() {
    document.getElementById('purchaseModal').style.display = 'block';
}

function closePurchaseModal() {
    document.getElementById('purchaseModal').style.display = 'none';
    document.getElementById('purchaseForm').reset();
}

function updatePriority() {

}

function submitPurchase() {
    const productName = document.getElementById('productName').value;
    const quantity = document.getElementById('productQuantity').value;
    const unit = document.getElementById('productUnit').value;
    const priority = document.querySelector('input[name="priority"]:checked').value;
    const reason = document.getElementById('purchaseReason').value;

    if (!productName || !quantity || !reason) {
        alert('Заполните все обязательные поля!');
        return;
    }

    const table = document.querySelector('.requests-table tbody');
    const newRow = document.createElement('tr');
    newRow.className = 'request-item';
    newRow.dataset.status = 'pending';
    newRow.innerHTML = `
        <td>${productName}</td>
        <td>${quantity} ${unit}</td>
        <td>${reason}</td>
        <td>${new Date().toLocaleDateString()}</td>
        <td><span class="status pending">В ожидании</span></td>
        <td>
            <button class="btn-action btn-edit" onclick="editRequest(this)">
                <i class="fas fa-edit"></i>
            </button>
        </td>
    `;

    table.prepend(newRow);
    updatePurchasesCount(1);

    alert(`Заявка на закупку ${quantity}${unit} "${productName}" отправлена!`);
    closePurchaseModal();
}

function updatePurchasesCount(change) {
    const badge = document.getElementById('purchasesBadge');
    let current = parseInt(badge.textContent);
    current += change;
    if (current < 0) current = 0;
    badge.textContent = current;
}

function filterRequests(status) {
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    const requests = document.querySelectorAll('.request-item');
    requests.forEach(request => {
        if (status === 'all' || request.dataset.status === status) {
            request.style.display = '';
        } else {
            request.style.display = 'none';
        }
    });
}

function editRequest(button) {
    const row = button.closest('tr');
    const product = row.cells[0].textContent;
    const quantity = row.cells[1].textContent;
    const reason = row.cells[2].textContent;

    document.getElementById('productName').value = product;

    const match = quantity.match(/(\d+)\s*(кг|л|шт)/);
    if (match) {
        document.getElementById('productQuantity').value = match[1];
        document.getElementById('productUnit').value = match[2];
    }

    document.getElementById('purchaseReason').value = reason;

    currentRequest = row;
    openPurchaseModal();
}

function viewRequest(button) {
    const row = button.closest('tr');
    const product = row.cells[0].textContent;
    const quantity = row.cells[1].textContent;
    const reason = row.cells[2].textContent;
    const date = row.cells[3].textContent;
    const status = row.cells[4].querySelector('.status').textContent;

    alert(`Детали заявки:\n\nПродукт: ${product}\nКоличество: ${quantity}\nПричина: ${reason}\nДата: ${date}\nСтатус: ${status}`);
}

function deleteRequest(button) {
    if (confirm('Удалить эту заявку?')) {
        const row = button.closest('tr');
        row.style.opacity = '0.5';
        setTimeout(() => {
            row.remove();
            updatePurchasesCount(-1);
        }, 300);
    }
}

function addNewDish() {
    document.getElementById('dishModalTitle').textContent = 'Новое блюдо';
    document.getElementById('dishForm').reset();
    currentDish = null;
    document.getElementById('dishModal').style.display = 'block';
}

function editMenu() {
    alert('Режим редактирования меню активирован. Вы можете изменять существующие блюда.');
}

function updatePrices() {
    const increase = confirm('Увеличить все цены на 10%?');
    if (increase) {
        const prices = document.querySelectorAll('.dish-price');
        prices.forEach(priceElement => {
            let price = parseInt(priceElement.textContent);
            price = Math.round(price * 1.1);
            priceElement.textContent = price + ' ₽';
        });
        alert('Цены обновлены! Все блюда подорожали на 10%.');
    }
}

function editDish(button) {
    const dishItem = button.closest('.dish-item');
    const name = dishItem.querySelector('h4').textContent;
    const price = dishItem.querySelector('.dish-price').textContent.replace(' ₽', '');
    const desc = dishItem.querySelector('.dish-desc').textContent;

    document.getElementById('dishModalTitle').textContent = 'Редактировать блюдо';
    document.getElementById('dishName').value = name;
    document.getElementById('dishPrice').value = price;
    document.getElementById('dishDescription').value = desc;
    document.getElementById('dishIngredients').value = 'яйца, помидоры, перец, лук, зелень';

    currentDish = dishItem;
    document.getElementById('dishModal').style.display = 'block';
}

function removeDish(button) {
    if (confirm('Удалить это блюдо из меню?')) {
        const dishItem = button.closest('.dish-item');
        dishItem.style.opacity = '0.5';
        setTimeout(() => dishItem.remove(), 300);
    }
}

function closeDishModal() {
    document.getElementById('dishModal').style.display = 'none';
}

function saveDish() {
    const name = document.getElementById('dishName').value;
    const price = document.getElementById('dishPrice').value;
    const desc = document.getElementById('dishDescription').value;
    const ingredients = document.getElementById('dishIngredients').value;

    if (!name || !price || !desc || !ingredients) {
        alert('Заполните все поля!');
        return;
    }

    if (currentDish) {
        currentDish.querySelector('h4').textContent = name;
        currentDish.querySelector('.dish-price').textContent = price + ' ₽';
        currentDish.querySelector('.dish-desc').textContent = desc;
        alert('Блюдо обновлено!');
    } else {
        const dishesList = document.querySelector('.dishes-list');
        const newDish = document.createElement('div');
        newDish.className = 'dish-item';
        newDish.innerHTML = `
            <div class="dish-header">
                <h4>${name}</h4>
                <span class="dish-price">${price} ₽</span>
            </div>
            <p class="dish-desc">${desc}</p>
            <div class="dish-actions">
                <button class="btn btn-sm btn-outline" onclick="editDish(this)">Изменить</button>
                <button class="btn btn-sm btn-danger" onclick="removeDish(this)">Удалить</button>
            </div>
        `;
        dishesList.appendChild(newDish);
        alert('Новое блюдо добавлено в меню!');
    }

    closeDishModal();
}

function logout() {
    if (confirm('Вы уверены, что хотите выйти?')) {
        window.location.href = 'index.html';
    }
}

window.addEventListener('click', function(event) {
    const modals = ['purchaseModal', 'dishModal'];
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});

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
