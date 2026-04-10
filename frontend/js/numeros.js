let numerosSelecionados = [];
let numerosDisponiveis = [];
let numerosReservados = [];
let numerosPagos = [];

async function carregarMapaNumeros(rifaId) {
    const grid = document.getElementById('numeros-grid');
    if (!grid) return;
    
    grid.innerHTML = '<div class="loading-spinner">Carregando números...</div>';
    
    try {
        const data = await API.getNumerosRifa(rifaId);
        numerosDisponiveis = data.disponiveis || [];
        numerosReservados = data.reservados || [];
        numerosPagos = data.pagos || [];
        renderizarMapaNumeros(data.total || 100);
    } catch (error) {
        grid.innerHTML = '<p class="error">Erro ao carregar números</p>';
    }
}

function renderizarMapaNumeros(total) {
    const grid = document.getElementById('numeros-grid');
    if (!grid) return;
    grid.innerHTML = '';
    
    for (let i = 1; i <= total; i++) {
        const div = document.createElement('div');
        div.className = 'numero';
        
        if (numerosPagos.includes(i)) {
            div.className += ' pago';
            div.textContent = '✓';
        } else if (numerosReservados.includes(i)) {
            div.className += ' reservado';
            div.textContent = '⏳';
        } else {
            div.className += ' disponivel';
            div.textContent = i;
            div.onclick = () => toggleNumero(i);
        }
        
        if (numerosSelecionados.includes(i)) div.className += ' selecionado';
        grid.appendChild(div);
    }
}

function toggleNumero(numero) {
    if (numerosSelecionados.includes(numero)) {
        numerosSelecionados = numerosSelecionados.filter(n => n !== numero);
        console.log('➖ Removido. Selecionados:', numerosSelecionados);
    } else {
        if (numerosPagos.includes(numero) || numerosReservados.includes(numero)) {
            mostrarMensagem('Número não disponível', 'warning');
            return;
        }
        numerosSelecionados.push(numero);
        console.log('➕ Adicionado. Selecionados:', numerosSelecionados);
    }
    
    atualizarCarrinho();
    const totalNumeros = numerosDisponiveis.length + numerosReservados.length + numerosPagos.length;
    renderizarMapaNumeros(totalNumeros);
}

function atualizarCarrinho() {
    const lista = document.getElementById('carrinho-lista');
    const totalSpan = document.getElementById('total-valor');
    const btn = document.getElementById('btn-reservar');
    
    if (!lista) return;
    
    if (numerosSelecionados.length === 0) {
        lista.innerHTML = '<li class="carrinho-vazio">Nenhum número selecionado</li>';
        totalSpan.textContent = formatarMoeda(0);
        btn.disabled = true;
        return;
    }
    
    const numerosOrd = [...numerosSelecionados].sort((a,b) => a-b);
    lista.innerHTML = numerosOrd.map(n => `
        <li>Nº ${n.toString().padStart(3,'0')} <button onclick="removerNumeroCarrinho(${n})" class="btn-icon">✕</button></li>
    `).join('');
    
    const total = numerosSelecionados.length * (window.valorBilhete || 0);
    totalSpan.textContent = formatarMoeda(total);
    btn.disabled = false;
}

function removerNumeroCarrinho(numero) {
    numerosSelecionados = numerosSelecionados.filter(n => n !== numero);
    atualizarCarrinho();
    renderizarMapaNumeros(100);
}

document.addEventListener('DOMContentLoaded', () => {
    const limparBtn = document.getElementById('limpar-carrinho');
    if (limparBtn) {
        limparBtn.onclick = () => {
            numerosSelecionados = [];
            atualizarCarrinho();
            renderizarMapaNumeros(100);
        };
    }
    
    const reservarBtn = document.getElementById('btn-reservar');
    if (reservarBtn && typeof window.reservarNumeros === 'function') {
        reservarBtn.onclick = () => window.reservarNumeros();
    }
});