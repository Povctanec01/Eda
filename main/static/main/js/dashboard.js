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
});
// Проверка совпадения паролей
document.getElementById('passwordForm').addEventListener('submit', function(e) {
  const password1 = document.getElementById('new_password1').value;
  const password2 = document.getElementById('new_password2').value;

  if (password1 !== password2) {
    e.preventDefault();
    alert('Новые пароли не совпадают!');
    return false;
  }

  if (password1.length < 8) {
    e.preventDefault();
    alert('Пароль должен содержать минимум 8 символов!');
    return false;
  }
});