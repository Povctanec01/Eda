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
