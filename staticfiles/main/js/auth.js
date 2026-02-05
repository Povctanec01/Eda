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

  // Сами ошибки
  const serverErrors = document.querySelectorAll('.floating-error.hidden');
  serverErrors.forEach(err => {
    showFloatingError(err);
  });

  // === ВКЛАДКИ ===
  function showTab(tabName) {
    document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));
    document.querySelectorAll('.auth-tab').forEach(tab => tab.classList.remove('active'));

    const targetForm = document.getElementById(tabName + '-form');
    const targetTab = document.getElementById(tabName + 'Tab');

    if (targetForm) targetForm.classList.add('active');
    if (targetTab) targetTab.classList.add('active');
  }

  const loginTab = document.getElementById('loginTab');
  const registerTab = document.getElementById('registerTab');

  if (loginTab) {
    loginTab.addEventListener('click', () => showTab('login'));
  }

  if (registerTab) {
    registerTab.addEventListener('click', () => showTab('register'));
  }

  // === УНИВЕРСАЛЬНЫЙ ПОКАЗ/СКРЫТИЕ ПАРОЛЯ ===
  document.querySelectorAll('.show-password').forEach(button => {
    button.addEventListener('click', function() {
      // Находим поле ввода пароля в том же password-wrapper
      const passwordWrapper = this.closest('.password-wrapper');
      if (!passwordWrapper) return;

      const passwordInput = passwordWrapper.querySelector('input');
      if (!passwordInput) return;

      const icon = this.querySelector('i');
      if (!icon) return;

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
  });
});