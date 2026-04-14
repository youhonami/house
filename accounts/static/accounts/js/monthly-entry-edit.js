(function () {
  'use strict';

  var FIELD_LABELS = {
    __all__: '入力',
    date: '日付',
    amount: '金額',
    note: '内容',
    category: 'カテゴリ',
  };

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }

  function qsa(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function clearErrors(el) {
    el.textContent = '';
    el.hidden = true;
  }

  function showErrors(el, errors) {
    if (!errors || typeof errors !== 'object') {
      el.textContent = '保存に失敗しました。';
      el.hidden = false;
      return;
    }
    var lines = [];
    Object.keys(errors).forEach(function (key) {
      var label = FIELD_LABELS[key] || key;
      (errors[key] || []).forEach(function (msg) {
        lines.push(label + '：' + msg);
      });
    });
    el.textContent = lines.length ? lines.join('\n') : '入力内容を確認してください。';
    el.hidden = false;
  }

  function csrfFromForm(form) {
    var input = form.querySelector('input[name=csrfmiddlewaretoken]');
    return input ? input.value : '';
  }

  function openEdit(dialog, titleEl, incomeForm, expenseForm, errEl, kind, url) {
    clearErrors(errEl);
    titleEl.textContent = kind === 'income' ? '収入を編集' : '支出を編集';
    incomeForm.hidden = kind !== 'income';
    expenseForm.hidden = kind !== 'expense';

    return fetch(url, {
      method: 'GET',
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
    })
      .then(function (r) {
        if (!r.ok) throw new Error('load');
        return r.json();
      })
      .then(function (body) {
        if (!body.ok || !body.data) throw new Error('load');
        var d = body.data;
        if (kind === 'income') {
          qs('#monthly-edit-income-date', incomeForm).value = d.date;
          qs('#monthly-edit-income-amount', incomeForm).value = d.amount;
          qs('#monthly-edit-income-note', incomeForm).value = d.note || '';
        } else {
          qs('#monthly-edit-expense-date', expenseForm).value = d.date;
          qs('#monthly-edit-expense-amount', expenseForm).value = d.amount;
          qs('#monthly-edit-expense-category', expenseForm).value = d.category;
          qs('#monthly-edit-expense-note', expenseForm).value = d.note || '';
        }
        dialog.showModal();
      })
      .catch(function () {
        showErrors(errEl, null);
        errEl.textContent = 'データの読み込みに失敗しました。';
        dialog.showModal();
      });
  }

  function submitForm(dialog, errEl, form, url) {
    clearErrors(errEl);
    var fd = new FormData(form);
    var submitBtn = form.querySelector('button[type=submit]');
    var delBtn = form.querySelector('[data-monthly-entry-delete]');
    if (submitBtn) submitBtn.disabled = true;
    if (delBtn) delBtn.disabled = true;

    return fetch(url, {
      method: 'POST',
      body: fd,
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': csrfFromForm(form),
        Accept: 'application/json',
      },
    })
      .then(function (r) {
        return r.json().then(function (body) {
          return { ok: r.ok, status: r.status, body: body };
        });
      })
      .then(function (res) {
        if (res.ok && res.body && res.body.ok) {
          dialog.close();
          window.location.reload();
          return;
        }
        if (res.body && res.body.errors) {
          showErrors(errEl, res.body.errors);
        } else {
          showErrors(errEl, null);
        }
      })
      .catch(function () {
        showErrors(errEl, null);
        errEl.textContent = '通信に失敗しました。';
      })
      .finally(function () {
        if (submitBtn) submitBtn.disabled = false;
        if (delBtn) delBtn.disabled = false;
      });
  }

  function deleteEntry(dialog, errEl, form, url) {
    if (
      !window.confirm(
        'この記録を削除しますか？この操作は取り消せません。'
      )
    ) {
      return;
    }
    clearErrors(errEl);
    var submitBtn = form.querySelector('button[type=submit]');
    var delBtn = form.querySelector('[data-monthly-entry-delete]');
    if (submitBtn) submitBtn.disabled = true;
    if (delBtn) delBtn.disabled = true;

    fetch(url, {
      method: 'DELETE',
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': csrfFromForm(form),
        Accept: 'application/json',
      },
    })
      .then(function (r) {
        return r.json().then(function (body) {
          return { ok: r.ok, body: body };
        });
      })
      .then(function (res) {
        if (res.ok && res.body && res.body.ok) {
          dialog.close();
          window.location.reload();
          return;
        }
        showErrors(errEl, null);
        errEl.textContent = '削除に失敗しました。';
      })
      .catch(function () {
        showErrors(errEl, null);
        errEl.textContent = '通信に失敗しました。';
      })
      .finally(function () {
        if (submitBtn) submitBtn.disabled = false;
        if (delBtn) delBtn.disabled = false;
      });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var dialog = qs('#monthly-entry-edit-dialog');
    if (!dialog || typeof dialog.showModal !== 'function') return;

    var titleEl = qs('#monthly-entry-edit-title');
    var errEl = qs('#monthly-entry-edit-errors');
    var incomeForm = qs('#monthly-income-edit-form');
    var expenseForm = qs('#monthly-expense-edit-form');
    var postUrl = '';

    qsa('[data-monthly-entry-dialog-close]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        dialog.close();
      });
    });

    dialog.addEventListener('close', function () {
      clearErrors(errEl);
    });

    qsa('.monthly-entry-edit-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var kind = btn.getAttribute('data-edit-kind');
        var url = btn.getAttribute('data-edit-url');
        if (!kind || !url) return;
        postUrl = url;
        openEdit(dialog, titleEl, incomeForm, expenseForm, errEl, kind, url);
      });
    });

    incomeForm.addEventListener('submit', function (e) {
      e.preventDefault();
      submitForm(dialog, errEl, incomeForm, postUrl);
    });

    expenseForm.addEventListener('submit', function (e) {
      e.preventDefault();
      submitForm(dialog, errEl, expenseForm, postUrl);
    });

    qsa('[data-monthly-entry-delete]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var form = btn.closest('form');
        if (!form || !postUrl) return;
        deleteEntry(dialog, errEl, form, postUrl);
      });
    });
  });
})();
