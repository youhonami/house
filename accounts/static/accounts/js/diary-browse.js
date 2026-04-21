(function () {
  const form = document.querySelector("[data-diary-browse-form]");
  if (!form) return;

  form.addEventListener("change", function (e) {
    const target = e.target;
    if (!(target instanceof HTMLInputElement) || target.name !== "date") {
      return;
    }
    let autoShown = form.querySelector('input[name="shown"][data-diary-auto-shown]');
    if (!autoShown) {
      autoShown = document.createElement("input");
      autoShown.type = "hidden";
      autoShown.name = "shown";
      autoShown.value = "1";
      autoShown.setAttribute("data-diary-auto-shown", "");
      form.appendChild(autoShown);
    }
    form.submit();
  });
})();
