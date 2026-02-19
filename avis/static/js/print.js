const handlePrint = (baseUrl, target) => {
  const skipEtichetteEl = document.getElementById("skipEtichette");
  const skipEtichette = parseInt(skipEtichetteEl.value);
  window.open(`${baseUrl}&skip_etichette=${skipEtichette}`, target);
  const myModalEl = document.getElementById("myModal");
  const modal = bootstrap.Modal.getInstance(myModalEl);
  modal.hide();
};
