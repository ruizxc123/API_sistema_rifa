function atualizarCarrinho() {
    const lista = document.getElementById('carrinho-lista');
    const totalValor = document.getElementById('total-valor');
    const btnReservar = document.getElementById('btn-reservar');
    
    if (!lista) return;
    
    if (numerosSelecionados.length === 0) {
        lista.innerHTML = '<li class="carrinho-vazio">Nenhum número selecionado</li>';
        totalValor.textContent = formatarMoeda(0);
        if (btnReservar) btnReservar.disabled = true;
        return;
    }
    
    const numerosOrdenados = [...numerosSelecionados].sort((a, b) => a - b);
    
    lista.innerHTML = numerosOrdenados.map(numero => `
        <li>
            <span class="numero-item">Nº ${numero.toString().padStart(3, '0')}</span>
            <button class="remover-numero" onclick="removerNumeroCarrinho(${numero})">✕</button>
        </li>
    `).join('');
    
    const total = numerosSelecionados.length * (window.valorBilhete || 0);
    totalValor.textContent = formatarMoeda(total);
    if (btnReservar) btnReservar.disabled = false;
}

function removerNumeroCarrinho(numero) {
    numerosSelecionados = numerosSelecionados.filter(n => n !== numero);
    atualizarCarrinho();
    renderizarMapaNumeros(100);
}

// Inicializar carrinho
document.addEventListener('DOMContentLoaded', () => {
    const limparBtn = document.getElementById('limpar-carrinho');
    if (limparBtn) {
        limparBtn.onclick = () => {
            numerosSelecionados = [];
            atualizarCarrinho();
            if (typeof renderizarMapaNumeros === 'function') {
                renderizarMapaNumeros(100);
            }
            mostrarMensagem('Carrinho limpo', 'success');
        };
    }
    
    const reservarBtn = document.getElementById('btn-reservar');
    if (reservarBtn) {
        reservarBtn.onclick = () => {
            if (typeof reservarNumeros === 'function') {
                reservarNumeros();
            }
        };
    }
});