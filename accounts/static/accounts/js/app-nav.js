(function () {
  const mq = window.matchMedia('(max-width: 720px)');
  const shell = document.querySelector('[data-app-shell]');
  const btn = document.getElementById('app-nav-toggle');
  const backdrop = document.getElementById('app-shell-backdrop');
  const drawer = document.getElementById('app-sidebar-drawer');
  if (!shell || !btn || !backdrop || !drawer) return;

  function isDrawerMode() {
    return mq.matches;
  }

  function openNav() {
    shell.classList.add('app-shell--drawer-open');
    btn.setAttribute('aria-expanded', 'true');
    btn.setAttribute('aria-label', 'メニューを閉じる');
    backdrop.removeAttribute('hidden');
    backdrop.setAttribute('aria-hidden', 'false');
    document.body.classList.add('app-shell-lock-scroll');
  }

  function closeNav() {
    shell.classList.remove('app-shell--drawer-open');
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-label', 'メニューを開く');
    backdrop.setAttribute('hidden', '');
    backdrop.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('app-shell-lock-scroll');
  }

  function toggleNav() {
    if (shell.classList.contains('app-shell--drawer-open')) closeNav();
    else openNav();
  }

  btn.addEventListener('click', function () {
    if (!isDrawerMode()) return;
    toggleNav();
  });

  backdrop.addEventListener('click', function () {
    closeNav();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && shell.classList.contains('app-shell--drawer-open')) {
      closeNav();
      btn.focus();
    }
  });

  function closeIfDrawerLink() {
    if (isDrawerMode() && shell.classList.contains('app-shell--drawer-open')) closeNav();
  }

  const brand = drawer.querySelector('.app-sidebar__brand');
  if (brand) brand.addEventListener('click', closeIfDrawerLink);

  drawer.querySelectorAll('.app-sidebar__link[href]').forEach(function (el) {
    el.addEventListener('click', closeIfDrawerLink);
  });

  const lo = drawer.querySelector('.app-sidebar__link--logout');
  if (lo) lo.addEventListener('click', closeIfDrawerLink);

  mq.addEventListener('change', function () {
    if (!isDrawerMode()) closeNav();
  });
})();
