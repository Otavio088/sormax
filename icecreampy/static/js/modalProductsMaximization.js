function openMaximizationModal(category) {
    const modal = document.getElementById('modal-product');
    document.getElementById('modal-max-product-name').textContent = category.name;
    document.getElementById('category_id_max').value = category.id;
    
    // Preenche os insumos disponíveis
    const restrictionsList = document.getElementById('restrictions-list');
    restrictionsList.innerHTML = '';
    category.restrictions.forEach(r => {
        restrictionsList.innerHTML += `
            <div class="restriction-item">
                <strong>${r.name}</strong>: ${r.quantity_available} ${r.unit_type}
            </div>
        `;
    });
    
    // Preenche os produtos
    const productsContainer = document.getElementById('products-container');
    productsContainer.innerHTML = '';
    category.products.forEach(product => {
        const productDiv = document.createElement('div');
        productDiv.className = 'product-item';
        productDiv.innerHTML = `
            <input type="checkbox" name="products[]" value="${product.id}" id="product-${product.id}">
            <label for="product-${product.id}">
                ${product.name} - R$ ${product.price.toFixed(2)}
            </label>
        `;
        productsContainer.appendChild(productDiv);
    });
    
    // Configura o "Selecionar todos"
    document.getElementById('select-all').addEventListener('change', function(e) {
        const checkboxes = document.querySelectorAll('#products-container input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = e.target.checked;
        });
    });
    
    modal.style.display = 'block';
}

function closeMaximizationModal() {
    document.getElementById('modal-product').style.display = 'none';
}