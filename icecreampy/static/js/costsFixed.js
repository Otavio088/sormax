function addCostField(cost = {}) {
    const container = document.getElementById('fixed-costs-container');
    const div = document.createElement('div');
    div.classList.add('fixed-cost-input');

    div.innerHTML = `
        <input type="hidden" name="id[]" value="${cost.id || ''}">
        <input name="name[]" class="input-name" type="text" placeholder="Nome do custo" value="${cost.name || ''}" required>
        <input name="price_month[]" type="number" step="0.01" placeholder="Custo mensal (R$)" value="${cost.price_month || ''}" required>
        <button type="button" onclick="confirmRemove(this)">Remover</button>
    `;

    container.appendChild(div);
}

function loadCosts(costs) {
    if (!costs || costs.length === 0) return;
    const container = document.getElementById('fixed-costs-container');
    container.innerHTML = '';
    costs.forEach(addCostField);
}

function confirmRemove(button) {
    const confirmDelete = confirm('Tem certeza que deseja deletar este custo fixo?');
    if (confirmDelete) {
        removeCost(button);
    }
}

function removeCost(button) {
    const div = button.parentElement;
    const hiddenIdInput = div.querySelector('input[name="id[]"]');
    if (hiddenIdInput && hiddenIdInput.value) {
        const form = div.closest('form');
        const inputDelete = document.createElement('input');
        inputDelete.type = 'hidden';
        inputDelete.name = 'delete_id[]';
        inputDelete.value = hiddenIdInput.value;
        form.appendChild(inputDelete);
    }
    div.remove();
}

document.addEventListener('DOMContentLoaded', () => {
    if (allCosts.length > 0) {
        loadCosts(allCosts);
    }
});
