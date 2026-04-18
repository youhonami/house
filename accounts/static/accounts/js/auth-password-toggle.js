(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.auth-password-toggle').forEach(function (btn) {
      var wrap = btn.closest('.auth-password-wrap');
      if (!wrap) return;
      var input = wrap.querySelector('input[type="password"], input[type="text"]');
      if (!input || input.name === undefined) return;

      btn.addEventListener('click', function () {
        var showing = input.getAttribute('type') === 'text';
        if (showing) {
          input.setAttribute('type', 'password');
          btn.classList.remove('is-revealed');
          btn.setAttribute('aria-pressed', 'false');
          btn.setAttribute('aria-label', 'パスワードを表示');
        } else {
          input.setAttribute('type', 'text');
          btn.classList.add('is-revealed');
          btn.setAttribute('aria-pressed', 'true');
          btn.setAttribute('aria-label', 'パスワードを隠す');
        }
      });
    });
  });
})();
