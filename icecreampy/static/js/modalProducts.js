let productIndex = 0;

function openProductModal(category) {
  const modal = document.getElementById("modal-product");
  const form = document.getElementById("form-products");
  const products = document.getElementById("products-container");

  // Resetar formulário
  form.reset();
  products.innerHTML = "";
  productIndex = 0;

  let restrictionsList = [];

  document.getElementById("modal-product-category-name").innerText = category.name;
  document.getElementById("category_id_prod").value = category.id;


  // Mostrar insumos disponíveis e suas quantidades
  const availableRestrictions = document.getElementById("available-restrictions");
  availableRestrictions.innerHTML = "<h4>Insumos Disponíveis:</h4>";

  restrictionsList = category.restrictions;
  restrictionsList.forEach(r => {
    availableRestrictions.innerHTML += `<p><strong>${r.name}</strong>: ${r.quantity_available} ${r.unit_type} - R$ ${r.unit_price} Litro.</p>`;
  });

  // Disponibiliza o restrictionsList mesmo se não tiver categoria ou produtos
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

    <label>% de Lucro desejado:</label>
    <input type="number" step="0.01" min="0" name="products[${index}][profit_percentage]" value="${product.profit_percentage || 0}" required>

    <label>Preço por litro:</label>
    <input type="number" step="0.01" min="0" name="products[${index}][price]" value="${product.price_total}" disabled style="background-color: #e9ecef;">
  `;

  product.restrictions.forEach((r, i) => {
    inner += `
      <label>Quantidade de ${r.name}:</label>
      <input type="hidden" name="products[${index}][restrictions][${i}][id]" value="${r.id}">
      <input type="number" step="0.01" min="0" name="products[${index}][restrictions][${i}][quantity]" value="${r.quantity}" required>
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

  const div = document.createElement("div");
  div.classList.add("product-group");

  let inner = `
    <label>Nome do Produto:</label>
    <input type="text" name="products[${productIndex}][name]" required>

    <label>% de Lucro:</label>
    <input type="number" step="0.01" min="1" name="products[${productIndex}][profit_percentage]" required>

    <label>Preço por litro:</label>
    <input type="number" step="0.01" min="0" name="products[${productIndex}][price]" disabled style="background-color: #e9ecef;">
  `;

  restrictionsList.forEach((r, i) => {
    inner += `
      <label>Quantidade de ${r.name}:</label>
      <input type="hidden" name="products[${productIndex}][restrictions][${i}][id]" value="${r.id}">
      <input type="number" step="0.01" min="0" name="products[${productIndex}][restrictions][${i}][quantity]" required>
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
