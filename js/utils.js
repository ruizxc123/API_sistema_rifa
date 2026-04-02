function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

function formatarData(data) {
    return new Date(data).toLocaleDateString('pt-BR');
}

function formatarDataHora(data) {
    return new Date(data).toLocaleString('pt-BR');
}

function mostrarMensagem(mensagem, tipo = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${tipo}`;
    toast.innerHTML = `
        <span>${mensagem}</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.remove(), 5000);
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function loading(mostrar = true, elemento = null) {
    if (mostrar) {
        const loader = document.createElement('div');
        loader.id = 'global-loader';
        loader.className = 'loader-overlay';
        loader.innerHTML = '<div class="loader"></div>';
        document.body.appendChild(loader);
    } else {
        const loader = document.getElementById('global-loader');
        if (loader) loader.remove();
    }
}

function validarCPF(cpf) {
    cpf = cpf.replace(/[^\d]/g, '');
    if (cpf.length !== 11) return false;
    return true;
}

function validarEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function mascaraCPF(input) {
    let valor = input.value.replace(/\D/g, '');
    if (valor.length <= 11) {
        valor = valor.replace(/(\d{3})(\d)/, '$1.$2');
        valor = valor.replace(/(\d{3})(\d)/, '$1.$2');
        valor = valor.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
        input.value = valor;
    }
}

function mascaraTelefone(input) {
    let valor = input.value.replace(/\D/g, '');
    if (valor.length <= 11) {
        valor = valor.replace(/(\d{2})(\d)/, '($1) $2');
        valor = valor.replace(/(\d{5})(\d)/, '$1-$2');
        input.value = valor;
    }
}