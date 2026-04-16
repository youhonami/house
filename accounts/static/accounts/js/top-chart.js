(function () {
  'use strict';

  function readJson(id) {
    var el = document.getElementById(id);
    if (!el || !el.textContent) return null;
    try {
      return JSON.parse(el.textContent);
    } catch (e) {
      return null;
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    var canvas = document.getElementById('top-month-chart');
    if (!canvas || typeof Chart === 'undefined') return;

    var income = readJson('top-chart-income');
    var expense = readJson('top-chart-expense');
    if (income === null || expense === null) return;

    var inc = Number(income);
    var exp = Number(expense);
    if (!Number.isFinite(inc)) inc = 0;
    if (!Number.isFinite(exp)) exp = 0;

    new Chart(canvas.getContext('2d'), {
      type: 'bar',
      data: {
        labels: ['収入', '支出'],
        datasets: [
          {
            data: [inc, exp],
            backgroundColor: [
              'rgba(30, 107, 64, 0.88)',
              'rgba(183, 28, 28, 0.88)',
            ],
            borderColor: ['#1e6b40', '#b71c1c'],
            borderWidth: 1,
            borderRadius: 6,
            maxBarThickness: 36,
          },
        ],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 1.65,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                var v = ctx.parsed.x;
                return (
                  (typeof v === 'number' ? v : 0).toLocaleString('ja-JP') + ' 円'
                );
              },
            },
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            grid: { color: 'rgba(0,0,0,0.06)' },
            ticks: {
              maxTicksLimit: 6,
              callback: function (value) {
                return Number(value).toLocaleString('ja-JP');
              },
            },
          },
          y: {
            grid: { display: false },
          },
        },
      },
    });
  });
})();
