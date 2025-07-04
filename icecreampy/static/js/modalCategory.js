let restrictionIndex = 0;

function openModal(category) {
    const modal = document.getElementById("modal-category");
    const form = document.getElementById("form-category");
    const formDelete = document.getElementById("form-delete");
    const restrictions = document.getElementById("restrictions");

    // Resetar formulário
    form.reset();
    restrictions.innerHTML = "";

    if (category) {
        formDelete.style.display = 'block';
        document.getElementById("category").value = category.name;
        document.getElementById("category_id").value = category.id;
        document.getElementById("category_id_remove").value = category.id; // para permitir deleção
        document.getElementById("days_production").value = parseInt(category.days_production);

        restrictionIndex = category.restrictions.length;

        category.restrictions.forEach((r, index) => {
            loadRestrictions(r, index);
        });
    } else {
        formDelete.style.display = 'none';
        document.getElementById("category_id").value = "";
        restrictionIndex = 0;
        addRestriction();  // inicia com um insumo
    }

    modal.style.display = "block";
}

function loadRestrictions(restriction, index) {
    const container = document.getElementById("restrictions");

    const showRestriction = document.createElement("div");
    showRestriction.className = "restriction";
    showRestriction.setAttribute("data-index", index);

    // Dentro do innerHTML da função loadRestrictions
    showRestriction.innerHTML = `
        <label>Insumo:</label>
        <input type="text" id="restriction_name_${index}" name="restrictions[${index}][name]" value="${restriction.name}" placeholder="Nome do insumo" required>

        <label>Quantidade disponível:</label>
        <input type="number" step="0.01" id="restriction_quantity_${index}" name="restrictions[${index}][quantity]" value="${restriction.quantity_available}" placeholder="Quantidade" required>

        <label>Tipo:</label>
        <select id="restriction_unit_${index}" name="restrictions[${index}][unit]" required>
            <option value="">Selecione</option>
            <option value="g">Grama</option>
            <option value="kg">Quilograma</option>
            <option value="ml">Mililitro</option>
            <option value="L">Litro</option>
        </select>

        <label>Preço Unitário:</label>
        <input type="number" step="0.01" id="restriction_unit_price_${index}" name="restrictions[${index}][unit_price]" value="${restriction.unit_price || ''}" placeholder="Preço Unitário" required>

        <button type="button" onclick="removeRestriction(this)">Remover</button> <hr>
    `;

    if (restriction.id) {
        showRestriction.innerHTML += `<input type="hidden" name="restrictions[${index}][id]" value="${restriction.id}">`;
    }

    container.appendChild(showRestriction);

    document.getElementById(`restriction_unit_${index}`).value = restriction.unit_type;
}

function addRestriction() {
    const container = document.getElementById("restrictions");

    const newRestriction = document.createElement("div");
    newRestriction.className = "restriction";
    newRestriction.setAttribute("data-index", restrictionIndex);

    newRestriction.innerHTML = `
        <label>Insumo:</label>
        <input type="text" id="restriction_name_${restrictionIndex}" name="restrictions[${restrictionIndex}][name]" placeholder="Nome do insumo" required>

        <label>Quantidade disponível:</label>
        <input type="number" step="0.01" id="restriction_quantity_${restrictionIndex}" name="restrictions[${restrictionIndex}][quantity]" placeholder="Quantidade" required>

        <label>Tipo:</label>
        <select id="restriction_unit_${restrictionIndex}" name="restrictions[${restrictionIndex}][unit]" required>
            <option value="">Selecione</option>
            <option value="g">Grama</option>
            <option value="kg">Quilograma</option>
            <option value="ml">Mililitro</option>
            <option value="L">Litro</option>
        </select>

        <label>Preço Unitário:</label>
        <input type="number" step="0.01" id="restriction_unit_price_${restrictionIndex}" name="restrictions[${restrictionIndex}][unit_price]" placeholder="Preço Unitário" required>

        <button type="button" onclick="removeRestriction(this)">Remover</button> <hr>
    `;

    container.appendChild(newRestriction);
    restrictionIndex++;
}

function removeRestriction(button) {
    const inputDiv = button.parentElement;
    inputDiv.remove();
}

function closeModal() {
    document.getElementById("modal-category").style.display = "none";

    document.getElementById("category").value = '';

    const container = document.getElementById("restrictions");
    container.innerHTML = ''; // Remove todas as restrições

    const restriction = document.createElement("div");
    restriction.className = 'restriction';
    restriction.setAttribute("data-index", 0);
    restriction.innerHTML = `
        <label>Insumo:</label>
        <input type="text" id="restriction_name_0" name="restrictions[0][name]" placeholder="Nome do insumo" required>

        <label>Quantidade disponível:</label>
        <input type="number" step="0.01" id="restriction_quantity_0" name="restrictions[0][quantity]" placeholder="Quantidade" required>

        <label>Tipo:</label>
        <select id="restriction_unit_0" name="restrictions[0][unit]" required>
            <option value="">Selecione</option>
            <option value="g">Grama</option>
            <option value="kg">Quilograma</option>
            <option value="ml">Mililitro</option>
            <option value="L">Litro</option>
        </select>

        <label>Preço Unitário:</label>
        <input type="number" step="0.01" id="restriction_unit_price_0" name="restrictions[0][unit_price]" placeholder="Preço Unitário" required>
    `;

    container.appendChild(restriction)
}
