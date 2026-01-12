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
