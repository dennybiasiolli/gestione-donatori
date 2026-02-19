function getCsrfToken() {
  return document.cookie
    .split("; ")
    .find((c) => c.startsWith("csrftoken="))
    ?.split("=")[1];
}

window.addEventListener("load", () => {
  const tooltipTriggerList = document.querySelectorAll(
    '[data-bs-toggle="tooltip"]',
  );
  const tooltipList = [...tooltipTriggerList].map(
    (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl),
  );
});

function handleAddRemovePrint(e, type, donatoreUrl, moveTo = undefined) {
  e.preventDefault();
  fetch(donatoreUrl, {
    method: "POST",
    headers: { "X-CSRFToken": getCsrfToken() },
  });
  const modalMessage = new bootstrap.Modal("#modalMessage");
  const modalMessageContent = document.getElementById("modalMessageContent");
  switch (type) {
    case "add":
      modalMessageContent.innerHTML = `Donatore aggiunto all\'elenco di stampa.<br><br>
            Trovi tutti i donatori nel menu "Elenco stampa".`;
      break;
    case "remove":
      modalMessageContent.innerHTML = `Donatore rimosso dall\'elenco di stampa.`;
      break;
    case "remove-all":
      if (moveTo) {
        window.location.href = moveTo;
        return;
      }
  }
  modalMessage.show();
}

function handleCheckUncheckPrivacy(e, donatoreUrl) {
  fetch(donatoreUrl, {
    method: "POST",
    headers: { "X-CSRFToken": getCsrfToken() },
  });
}
