function addCostField() {
    const container = document.getElementById('fixed-costs-container');
    const div = document.createElement('div');
    div.classList.add('fixed-cost-input');

    div.innerHTML = `
        <input type="hidden" name="id[]" value="">
        <input name="name[]" class="input-name" placeholder="Nome" required>
        <select name="unit_type[]" class="input-unit" required>
            <option value="">Tipo de unidade</option>
            <option value="hr">Hora</option>
            <option value="min">Minuto</option>
            <option value="L">Litro</option>
            <option value="ml">Mililitro</option>
            <option value="g">Grama</option>
            <option value="kg">Quilograma</option>
            <option value="un">Unidade</option>
            <option value="m">Metro</option>
            <option value="m2">Metro Quadrado</option>
            <option value="m4">Metro Cúbico</option>
            <option value="energ">Energia</option>
        </select>
        <input name="quantity_available[]" type="number" step="0.01" placeholder="Qtd. disponível" required>
        <input name="unit_price[]" type="number" step="0.01" placeholder="Preço por un." class="input-small" required>
        <button type="button" onclick="removeCost(this)">Remover</button>
    `;

    container.appendChild(div);
}

function loadCosts(costs) {
    if (!costs || costs.length === 0) {
        return;
    }

    const container = document.getElementById('fixed-costs-container');
    container.innerHTML = ''; // Limpa container antes de carregar

    costs.forEach(cost => {
        const div = document.createElement('div');
        div.classList.add('fixed-cost-input');

        div.innerHTML = `
            <input type="hidden" name="id[]" value="${cost.id || ''}">
            <input name="name[]" class="input-name" placeholder="Nome" value="${cost.name || ''}" required>
            <select name="unit_type[]" class="input-unit" required>
                <option value="">Tipo de unidade</option>
                <option value="hr" ${cost.unit_type === 'hr' ? 'selected' : ''}>Hora</option>
                <option value="min" ${cost.unit_type === 'min' ? 'selected' : ''}>Minuto</option>
                <option value="L" ${cost.unit_type === 'L' ? 'selected' : ''}>Litro</option>
                <option value="ml" ${cost.unit_type === 'ml' ? 'selected' : ''}>Mililitro</option>
                <option value="g" ${cost.unit_type === 'g' ? 'selected' : ''}>Grama</option>
                <option value="kg" ${cost.unit_type === 'kg' ? 'selected' : ''}>Quilograma</option>
                <option value="un" ${cost.unit_type === 'un' ? 'selected' : ''}>Unidade</option>
                <option value="m" ${cost.unit_type === 'm' ? 'selected' : ''}>Metro</option>
                <option value="m2" ${cost.unit_type === 'm2' ? 'selected' : ''}>Metro Quadrado</option>
                <option value="m4" ${cost.unit_type === 'm4' ? 'selected' : ''}>Metro Cúbico</option>
                <option value="energ" ${cost.unit_type === 'energ' ? 'selected' : ''}>Energia</option>
            </select>
            <input name="quantity_available[]" type="number" step="0.01" placeholder="Qtd. disponível" value="${cost.quantity_available || ''}" required>
            <input name="unit_price[]" type="number" step="0.01" placeholder="Preço por un." class="input-small" value="${cost.unit_price || ''}" required>
            <button type="button" onclick="removeCost(this)">Remover</button>
        `;

        container.appendChild(div);
    });
}

function removeCost(button) {
    const div = button.parentElement;
    const hiddenIdInput = div.querySelector('input[name="id[]"]');
    if (hiddenIdInput && hiddenIdInput.value) {
        // Cria um input hidden separado para exclusão
        const form = div.closest('form');
        let inputDelete = document.createElement('input');
        inputDelete.type = 'hidden';
        inputDelete.name = 'delete_id[]';
        inputDelete.value = hiddenIdInput.value;
        form.appendChild(inputDelete);
    }

    // Remove todo o bloco do DOM (ou esconde)
    div.remove();
}


// Carrega automaticamente ao iniciar (se houver dados)
document.addEventListener('DOMContentLoaded', () => {
    if (allCosts.length > 0) {
        loadCosts(allCosts);
    }
});
