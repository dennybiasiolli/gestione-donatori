["id_username", "id_password"].forEach(function (id) {
  document.getElementById(id).addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      this.closest("form").submit();
    }
  });
});
