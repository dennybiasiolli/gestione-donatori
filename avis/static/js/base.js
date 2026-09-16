function getCsrfToken() {
  return document.cookie
    .split("; ")
    .find((c) => c.startsWith("csrftoken="))
    ?.split("=")[1];
}

function showToast(message) {
  const toastEl = document.getElementById("appToast");
  const toastBody = document.getElementById("appToastBody");
  if (!toastEl || !toastBody) {
    return;
  }
  toastBody.textContent = message;
  bootstrap.Toast.getOrCreateInstance(toastEl).show();
}

function postAction(url) {
  return fetch(url, {
    method: "POST",
    headers: { "X-CSRFToken": getCsrfToken() },
  });
}

function updatePrintToggle(button, inList) {
  button.dataset.inList = inList ? "1" : "0";
  const icon = button.querySelector("i");
  if (icon) {
    icon.className = inList
      ? "bi bi-x-circle-fill text-danger"
      : "bi bi-printer text-muted";
  }
  const label = button.querySelector(".print-toggle-label");
  if (label) {
    label.textContent = inList ? "Rimuovi da elenco" : "Aggiungi all'elenco";
  }
  button.setAttribute(
    "aria-label",
    inList ? "Rimuovi da elenco stampa" : "Aggiungi a elenco stampa",
  );
  button.setAttribute(
    "data-bs-title",
    inList ? "Rimuovi da elenco stampa" : "Aggiungi a elenco stampa",
  );
  const tooltip = bootstrap.Tooltip.getInstance(button);
  if (tooltip) {
    tooltip.setContent({
      ".tooltip-inner": inList
        ? "Rimuovi da elenco stampa"
        : "Aggiungi a elenco stampa",
    });
  }
}

function updatePrivacyToggle(button, checked) {
  button.dataset.checked = checked ? "1" : "0";
  button.innerHTML = checked
    ? '<i class="bi bi-check-square-fill"></i> Privacy ok'
    : '<i class="bi bi-square"></i> Privacy mancante';
  button.classList.toggle("text-success", checked);
  button.classList.toggle("text-muted", !checked);
  button.setAttribute(
    "data-bs-title",
    checked ? "Annulla consegna del modulo" : "Imposta consegnato",
  );
  const tooltip = bootstrap.Tooltip.getInstance(button);
  if (tooltip) {
    tooltip.setContent({
      ".tooltip-inner": checked
        ? "Annulla consegna del modulo"
        : "Imposta consegnato",
    });
  }
}

window.addEventListener("load", () => {
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
    new bootstrap.Tooltip(el);
  });
});

document.addEventListener("click", (event) => {
  const printClear = event.target.closest(".print-clear");
  if (printClear) {
    event.preventDefault();
    const redirectTo = printClear.dataset.redirect;
    postAction(printClear.dataset.url).then(() => {
      if (redirectTo) {
        window.location.href = redirectTo;
      }
    });
    return;
  }

  const printToggle = event.target.closest(".print-toggle");
  if (printToggle) {
    event.preventDefault();
    const inList = printToggle.dataset.inList === "1";
    const url = inList
      ? printToggle.dataset.removeUrl
      : printToggle.dataset.addUrl;
    postAction(url).then(() => {
      updatePrintToggle(printToggle, !inList);
      showToast(
        inList
          ? "Donatore rimosso dall'elenco di stampa."
          : 'Donatore aggiunto all\'elenco di stampa. Lo trovi nel menu "Elenco stampa".',
      );
    });
    return;
  }

  const privacyToggle = event.target.closest(".privacy-toggle");
  if (privacyToggle) {
    event.preventDefault();
    const checked = privacyToggle.dataset.checked === "1";
    const url = checked
      ? privacyToggle.dataset.uncheckUrl
      : privacyToggle.dataset.checkUrl;
    postAction(url).then(() => {
      updatePrivacyToggle(privacyToggle, !checked);
    });
  }
});
