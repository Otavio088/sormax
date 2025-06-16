let productIndex = 0;

function openProductModal(category) { console.log('category: ', category);
  const modal = document.getElementById("modal-product");
  const form = document.getElementById("form-products");
  const products = document.getElementById("products-container");

  // Resetar formulário
  form.reset();
  products.innerHTML = "";
  productIndex = 0;

  let restrictionsList = [];
  let fixedCostsList = [];

  document.getElementById("modal-product-category-name").innerText = category.name;
  document.getElementById("category_id_prod").value = category.id;


  // Mostrar insumos disponíveis e suas quantidades
  const availableRestrictions = document.getElementById("available-restrictions");
  availableRestrictions.innerHTML = "<h4>Insumos Disponíveis:</h4>";

  restrictionsList = category.restrictions;
  restrictionsList.forEach(r => {
    availableRestrictions.innerHTML += `<p><strong>${r.name}</strong>: ${r.quantity_available} ${r.unit_type}</p>`;
  });

  // Mostrar custos fixos disponíveis e suas quantidades
  const availableFixedCosts = document.getElementById("available-fixed-costs");
  availableFixedCosts.innerHTML = "<h4>Custos Fixos Disponíveis:</h4>";

  fixedCostsList = category.fixed_costs || [];
  fixedCostsList.forEach(f => {
    availableFixedCosts.innerHTML += `<p><strong>${f.name}</strong>: ${f.quantity_available} ${f.unit_type} - R$ ${f.unit_price}</p>`;
  });

  // Disponibiliza o restrictionsList e fixedCostsList mesmo se não tiver categoria ou produtos
  modal.dataset.fixedCosts = JSON.stringify(fixedCostsList);
  modal.dataset.restrictions = JSON.stringify(restrictionsList);

  // Carrega produtos já existentes
  if (category.products && category.products.length > 0) {
    category.products.forEach((product, index) => {
      loadProducts(product, index);
    })
  } else {
    addProductForm();
  }

  modal.style.display = "block";
}

function loadProducts(product, index) {
  const container = document.getElementById("products-container");

  const div = document.createElement("div");
  div.classList.add("product-group");

  let inner = `
    <input type="hidden" name="products[${index}][id]" value="${product.id}">
    <label>Nome do Produto:</label>
    <input type="text" name="products[${index}][name]" value="${product.name}" required>
    <label>Preço por unidade:</label>
    <input type="number" step="0.01" min="0" name="products[${index}][price]" value="${product.price}" disabled style="background-color: #e9ecef;">
  `;

  product.restrictions.forEach((r, i) => {
    inner += `
      <label>Quantidade de ${r.name}:</label>
      <input type="hidden" name="products[${index}][restrictions][${i}][id]" value="${r.id}">
      <input type="number" step="0.01" min="0" name="products[${index}][restrictions][${i}][quantity]" value="${r.quantity}" required>
    `;
  });

  inner += `<h5>Custos Fixos:</h5>`;
  fixedCostsList.forEach((f, j) => {
    inner += `
      <label>Quantidade de ${f.name}:</label>
      <input type="hidden" name="products[${index}][fixed_costs][${j}][id]" value="${f.id}">
      <input type="number" step="0.01" min="0" name="products[${index}][fixed_costs][${j}][quantity]" value="${(product.fixed_costs || []).find(fc => fc.fixed_cost_id === f.id)?.quantity_used || 0}" required>
    `;
  });

  div.innerHTML = inner + `
    <button type="button" onclick="removeProduct(this)">Remover</button><hr>
  `;
  container.appendChild(div);
  productIndex++;
}

function addProductForm() {
  const container = document.getElementById("products-container");
  const modal = document.getElementById("modal-product");
  const restrictionsList = JSON.parse(modal.dataset.restrictions || '[]');
  const fixedCostsList = JSON.parse(modal.dataset.fixedCosts || '[]');

  const div = document.createElement("div");
  div.classList.add("product-group");

  let inner = `
    <label>Nome do Produto:</label>
    <input type="text" name="products[${productIndex}][name]" required>
    <label>Preço por unidade:</label>
    <input type="number" step="0.01" min="0" name="products[${productIndex}][price]" disabled style="background-color: #e9ecef;">
  `;

  restrictionsList.forEach((r, i) => {
    inner += `
      <label>Quantidade de ${r.name}:</label>
      <input type="hidden" name="products[${productIndex}][restrictions][${i}][id]" value="${r.id}">
      <input type="number" step="0.01" min="0" name="products[${productIndex}][restrictions][${i}][quantity]" required>
    `;
  });

  inner += `<h5>Custos Fixos:</h5>`;
  fixedCostsList.forEach((f, j) => {
    inner += `
      <label>Quantidade de ${f.name}:</label>
      <input type="hidden" name="products[${productIndex}][fixed_costs][${j}][id]" value="${f.id}">
      <input type="number" step="0.01" min="0" name="products[${productIndex}][fixed_costs][${j}][quantity]" required>
    `;
  });

  div.innerHTML = inner + `
    <button type="button" onclick="removeProduct(this)">Remover</button><hr>
  `;
  container.appendChild(div);
  productIndex++;
}

function removeProduct(button) {
  const inputDiv = button.parentElement;
  inputDiv.remove();
}

function closeProductModal() {
    document.getElementById("modal-product").style.display = "none";

    document.getElementById("category").value = '';

    const container = document.getElementById("products-container");
    container.innerHTML = ''; // Remove produtos
}
