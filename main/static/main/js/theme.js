// main/static/main/js/theme.js

class ThemeManager {
    constructor() {
        this.themeToggle = document.getElementById('themeToggle');
        this.currentTheme = this.getCurrentTheme();
        this.init();
    }

    init() {
        // Применяем сохранённую тему
        this.applyTheme(this.currentTheme);

        // Настраиваем переключатель
        if (this.themeToggle) {
            this.themeToggle.checked = this.currentTheme === 'dark';
            this.themeToggle.addEventListener('change', () => this.toggleTheme());
        }

        // Добавляем обработчики для специфичных элементов
        this.addThemeListeners();
    }

    getCurrentTheme() {
        // Проверяем локальное хранилище
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            return savedTheme;
        }

        // Проверяем системные настройки
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }

        // По умолчанию светлая тема
        return 'light';
    }

    applyTheme(theme) {
        // Устанавливаем data-атрибут на body
        document.body.setAttribute('data-theme', theme);

        // Обновляем скрытый элемент
        const themeData = document.getElementById('themeData');
        if (themeData) {
            themeData.setAttribute('data-theme', theme);
        }

        // Сохраняем в localStorage
        localStorage.setItem('theme', theme);

        // Обновляем иконку переключателя
        this.updateToggleIcon();

        // Генерируем событие смены темы
        document.dispatchEvent(new CustomEvent('themeChange', { detail: { theme } }));
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.currentTheme = newTheme;
        this.applyTheme(newTheme);
    }

    updateToggleIcon() {
        const themeSlider = document.querySelector('.theme-slider');
        if (themeSlider) {
            const icon = themeSlider.querySelector('.theme-icon') || document.createElement('span');
            icon.className = 'theme-icon';
            icon.textContent = this.currentTheme === 'dark' ? '🌙' : '☀️';

            if (!themeSlider.querySelector('.theme-icon')) {
                themeSlider.appendChild(icon);
            }
        }
    }

    addThemeListeners() {
        // Обработка системных изменений темы
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                this.applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    // Метод для получения текущей темы извне
    static getTheme() {
        return document.body.getAttribute('data-theme') || 'light';
    }

    // Метод для принудительной смены темы
    static setTheme(theme) {
        const manager = new ThemeManager();
        manager.applyTheme(theme);
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    new ThemeManager();

    // Добавляем глобальную функцию для переключения темы
    window.toggleTheme = function() {
        const themeManager = new ThemeManager();
        themeManager.toggleTheme();
    };
});

// Экспортируем для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}