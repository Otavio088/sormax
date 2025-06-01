function openProductModal() {
  document.getElementById("modal-product").style.display = "block";
}

function closeProductModal() {
  document.getElementById("modal-product").style.display = "none";
}

function loadRestrictions2() {
  const categoryId = document.getElementById("category-select").value;
  const restrictionSelect = document.getElementById("restriction-select");
  restrictionSelect.innerHTML = '<option value="">Carregando...</option>';

  fetch("/get-restrictions/" + categoryId)
    .then(res => res.json())
    .then(data => {
      restrictionSelect.innerHTML = '<option value="">Selecione</option>';
      for (const r of data) {
        restrictionSelect.innerHTML += `<option value="${r.id}">${r.name} - ${r.quantity_available} ${r.unit_type}</option>`;
      }
    });
}