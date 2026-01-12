// main/js/auth.js
document.addEventListener('DOMContentLoaded', function () {
  // Показать всплывающую ошибку
  function showFloatingError(element) {
    const errorClone = element.cloneNode(true);
    errorClone.classList.remove('hidden');
    errorClone.classList.add('show');
    document.body.appendChild(errorClone);

    setTimeout(() => {
      errorClone.classList.add('fade-out');
      setTimeout(() => {
        if (errorClone.parentNode) {
          errorClone.parentNode.removeChild(errorClone);
        }
      }, 300);
    }, 5000);
  }

  // === ПОКАЗ СЕРВЕРНЫХ ОШИБОК ПРИ ЗАГРУЗКЕ ===
  const serverErrors = document.querySelectorAll('.floating-error.hidden');
  serverErrors.forEach(err => {
    showFloatingError(err);
  });

  // === ВКЛАДКИ ===
  function showTab(tabName) {
    document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));
    document.querySelectorAll('.auth-tab').forEach(tab => tab.classList.remove('active'));
    document.getElementById(tabName + '-form').classList.add('active');
    document.getElementById(tabName + 'Tab').classList.add('active');
  }

  document.getElementById('loginTab')?.addEventListener('click', () => showTab('login'));
  document.getElementById('registerTab')?.addEventListener('click', () => showTab('register'));

  // === Показ/скрытие пароля (если реализовано) ===
  const showPasswordBtn = document.querySelector('.show-password');
  if (showPasswordBtn) {
    showPasswordBtn.addEventListener('click', function () {
      const passwordInput = document.getElementById('password');
      const icon = this.querySelector('i');
      if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
      } else {
        passwordInput.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
      }
    });
  }

  // === Обработка отправки форм (опционально — без AJAX) ===
  // Убран preventDefault, чтобы формы работали нормально с Django
  // Если нужна AJAX — реализуйте отдельно
});