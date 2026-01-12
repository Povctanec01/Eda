
let currentDish = { name: '', price: 0, description: '' };
let currentRating = 0;

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
    alert('У вас 2 новых уведомления:\n1. Заказ готов к получению\n2. Баланс пополнен');
}

function topUpBalance() {
    const amount = prompt('Введите сумму для пополнения (руб):');
    if (amount && !isNaN(amount) && amount > 0) {
        const balance = document.getElementById('balanceAmount');
        balance.textContent = parseInt(balance.textContent) + parseInt(amount);
        alert(`Баланс успешно пополнен на ${amount} руб!`);
    }
}

function manageSubscription() {
    alert('Управление абонементом:\nТекущий абонемент: Завтраки на месяц\nДействует до: 28.02.2024\nСтоимость продления: 1500 руб/мес');
}

function editAllergies() {
    showSection('preferences');
}

function filterMenu(type) {
    document.querySelectorAll('.meal-type-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        if (type === 'all' || item.dataset.type === type) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

function openOrderModal(name, price, description) {
    currentDish = { name, price, description };
    document.getElementById('modalDishName').textContent = name;
    document.getElementById('modalDishDesc').textContent = description;
    document.querySelector('.order-details .price').textContent = price + ' ₽';
    document.getElementById('orderModal').style.display = 'block';
    updateTotalPrice();
}

function closeOrderModal() {
    document.getElementById('orderModal').style.display = 'none';
    document.getElementById('quantity').value = 1;
}

function changeQuantity(delta) {
    const quantityInput = document.getElementById('quantity');
    let quantity = parseInt(quantityInput.value) + delta;

    if (quantity < 1) quantity = 1;
    if (quantity > 10) quantity = 10;

    quantityInput.value = quantity;
    updateTotalPrice();
}

function updatePaymentType() {
    updateTotalPrice();
}

function updateTotalPrice() {
    const price = currentDish.price;
    const quantity = parseInt(document.getElementById('quantity').value);
    const paymentType = document.querySelector('input[name="payment"]:checked').value;

    let total = price * quantity;
    if (paymentType === 'subscription') {
        total = 0;
    }

    document.getElementById('totalPrice').textContent = total;
}

function placeOrder() {
    const quantity = document.getElementById('quantity').value;
    const paymentType = document.querySelector('input[name="payment"]:checked').value;
    const total = document.getElementById('totalPrice').textContent;

    alert(`Заказ оформлен!\nБлюдо: ${currentDish.name}\nКоличество: ${quantity}\nТип оплаты: ${paymentType === 'subscription' ? 'Абонемент' : 'Разовый платёж'}\nСумма: ${total} руб`);
    closeOrderModal();
}

function leaveReview(dishName) {
    document.getElementById('reviewDish').value = dishName;
    openReviewModal();
}

function markAsReceived(button, dishName) {
    if (confirm(`Отметить блюдо "${dishName}" как полученное?`)) {
        button.innerHTML = '<i class="fas fa-check"></i> Получено';
        button.disabled = true;
        button.style.opacity = '0.7';
        button.closest('tr').querySelector('.status').textContent = 'Получено';
        button.closest('tr').querySelector('.status').className = 'status received';
        alert('Блюдо отмечено как полученное!');
    }
}

function savePreferences() {
    const allergies = document.getElementById('allergiesInput').value;
    const preferences = document.getElementById('preferencesInput').value;
    const dislikes = document.getElementById('dislikesInput').value;

    alert('Предпочтения успешно сохранены!');
}

function openReviewModal() {
    currentRating = 0;
    updateStars();
    document.getElementById('reviewModal').style.display = 'block';
}

function closeReviewModal() {
    document.getElementById('reviewModal').style.display = 'none';
    document.getElementById('reviewComment').value = '';
    currentRating = 0;
    updateStars();
}

function updateStars() {
    const stars = document.querySelectorAll('#ratingStars i');
    stars.forEach((star, index) => {
        if (index < currentRating) {
            star.className = 'fas fa-star';
        } else {
            star.className = 'far fa-star';
        }
    });
    document.getElementById('ratingValue').value = currentRating;
}

document.querySelectorAll('#ratingStars i').forEach(star => {
    star.addEventListener('click', function() {
        currentRating = parseInt(this.dataset.rating);
        updateStars();
    });

    star.addEventListener('mouseover', function() {
        const hoverRating = parseInt(this.dataset.rating);
        const stars = document.querySelectorAll('#ratingStars i');
        stars.forEach((s, index) => {
            if (index < hoverRating) {
                s.className = 'fas fa-star';
            } else {
                s.className = 'far fa-star';
            }
        });
    });

    star.addEventListener('mouseout', function() {
        updateStars();
    });
});

function submitReview() {
    const dish = document.getElementById('reviewDish').value;
    const rating = currentRating;
    const comment = document.getElementById('reviewComment').value;

    if (rating === 0) {
        alert('Пожалуйста, поставьте оценку!');
        return;
    }

    alert(`Отзыв отправлен!\nБлюдо: ${dish}\nОценка: ${rating}/5\nСпасибо за ваш отзыв!`);
    closeReviewModal();
}

function editReview(button) {
    const reviewItem = button.closest('.review-item');
    const dishName = reviewItem.querySelector('h4').textContent;
    const rating = reviewItem.querySelectorAll('.fa-star').length;
    const comment = reviewItem.querySelector('.review-text').textContent;

    document.getElementById('reviewDish').value = dishName;
    currentRating = rating;
    updateStars();
    document.getElementById('reviewComment').value = comment;
    openReviewModal();

    reviewItem.remove();
}

function logout() {
    if (confirm('Вы уверены, что хотите выйти?')) {
        window.location.href = 'index.html';
    }
}

window.addEventListener('click', function(event) {
    const modals = ['orderModal', 'reviewModal'];
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});
