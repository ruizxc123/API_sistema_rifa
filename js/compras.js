// js/compras.js
let todasCompras = [];
let comprasFiltradas = [];
let paginaAtual = 1;
let itensPorPagina = 10;

async function carregarHistoricoCompras() {
    const container = document.getElementById('compras-lista');
    
    try {
        const compras = await API.getHistoricoCompras();
        todasCompras = compras;
        comprasFiltradas = [...todasCompras];
        
        atualizarStats();
        renderizarCompras();
        
    } catch (error) {
        container.innerHTML = '<p class="error">Erro ao carregar histórico de compras</p>';
    }
}

function atualizarStats() {
    const totalGasto = comprasFiltradas.reduce((sum, compra) => sum + compra.valor_total, 0);
    const totalBilhetes = comprasFiltradas.reduce((sum, compra) => sum + compra.quantidade, 0);
    const totalPremios = comprasFiltradas.filter(c => c.premiado).length;
    const taxaAcerto = totalBilhetes > 0 ? (totalPremios / totalBilhetes * 100).toFixed(1) : 0;
    
    document.getElementById('total-gasto').textContent = formatarMoeda(totalGasto);
    document.getElementById('total-bilhetes').textContent = totalBilhetes;
    document.getElementById('total-premios').textContent = totalPremios;
    document.getElementById('taxa-acerto').textContent = `${taxaAcerto}%`;
}

function renderizarCompras() {
    const container = document.getElementById('compras-lista');
    const start = (paginaAtual - 1) * itensPorPagina;
    const end = start + itensPorPagina;
    const comprasPagina = comprasFiltradas.slice(start, end);
    
    if (comprasPagina.length === 0) {
        container.innerHTML = '<p class="empty-state">Nenhuma compra encontrada</p>';
        document.getElementById('pagination').style.display = 'none';
        return;
    }
    
    container.innerHTML = comprasPagina.map(compra => `
        <div class="compra-item">
            <div class="compra-header">
                <span class="compra-data">${formatarDataHora(compra.data_compra)}</span>
                <span class="compra-status ${compra.status}">
                    ${compra.premiado ? '🏆 PREMIADO' : compra.status.toUpperCase()}
                </span>
            </div>
            <div class="compra-body">
                <div class="compra-rifa-info">
                    <div class="compra-rifa-nome">${compra.rifa_nome}</div>
                    <div class="compra-rifa-premio">🎁 ${compra.premio}</div>
                </div>
                <div class="compra-numeros">
                    ${compra.numeros.map(num => `
                        <span class="compra-numero ${compra.numero_sorteado === num ? 'premiado' : ''}">
                            ${num.toString().padStart(3, '0')}
                            ${compra.numero_sorteado === num ? ' 🏆' : ''}
                        </span>
                    `).join('')}
                </div>
                <div class="compra-footer">
                    <div class="compra-total">
                        Total: <strong>${formatarMoeda(compra.valor_total)}</strong>
                    </div>
                    <a href="rifa-detalhe.html?id=${compra.rifa_id}" class="compra-link">
                        Ver rifa →
                    </a>
                </div>
            </div>
        </div>
    `).join('');
    
    // Atualizar paginação
    const totalPaginas = Math.ceil(comprasFiltradas.length / itensPorPagina);
    document.getElementById('page-info').textContent = `Página ${paginaAtual} de ${totalPaginas}`;
    document.getElementById('prev-page').disabled = paginaAtual === 1;
    document.getElementById('next-page').disabled = paginaAtual === totalPaginas;
    document.getElementById('pagination').style.display = 'flex';
}

function aplicarFiltros() {
    const searchTerm = document.getElementById('search-compras').value.toLowerCase();
    const statusFiltro = document.getElementById('filtro-status').value;
    const periodoFiltro = document.getElementById('filtro-periodo').value;
    
    comprasFiltradas = todasCompras.filter(compra => {
        // Busca
        if (searchTerm) {
            const matchRifa = compra.rifa_nome.toLowerCase().includes(searchTerm);
            const matchNumero = compra.numeros.some(n => n.toString().includes(searchTerm));
            if (!matchRifa && !matchNumero) return false;
        }
        
        // Status
        if (statusFiltro !== 'todos') {
            if (statusFiltro === 'premiado' && !compra.premiado) return false;
            if (statusFiltro === 'perdido' && compra.premiado) return false;
            if (statusFiltro === 'pago' && compra.status !== 'pago') return false;
            if (statusFiltro === 'pendente' && compra.status !== 'pendente') return false;
        }
        
        // Período
        if (periodoFiltro !== 'todos') {
            const dataCompra = new Date(compra.data_compra);
            const agora = new Date();
            
            if (periodoFiltro === '30') {
                const dias30 = new Date(agora.setDate(agora.getDate() - 30));
                if (dataCompra < dias30) return false;
            } else if (periodoFiltro === '90') {
                const dias90 = new Date(agora.setDate(agora.getDate() - 90));
                if (dataCompra < dias90) return false;
            } else if (periodoFiltro === '2024') {
                if (dataCompra.getFullYear() !== 2024) return false;
            }
        }
        
        return true;
    });
    
    paginaAtual = 1;
    atualizarStats();
    renderizarCompras();
}

function inicializarFiltros() {
    const searchInput = document.getElementById('search-compras');
    const statusSelect = document.getElementById('filtro-status');
    const periodoSelect = document.getElementById('filtro-periodo');
    const exportBtn = document.getElementById('exportar-compras');
    
    if (searchInput) searchInput.addEventListener('input', aplicarFiltros);
    if (statusSelect) statusSelect.addEventListener('change', aplicarFiltros);
    if (periodoSelect) periodoSelect.addEventListener('change', aplicarFiltros);
    
    if (exportBtn) {
        exportBtn.addEventListener('click', exportarCompras);
    }
    
    // Paginação
    document.getElementById('prev-page')?.addEventListener('click', () => {
        if (paginaAtual > 1) {
            paginaAtual--;
            renderizarCompras();
        }
    });
    
    document.getElementById('next-page')?.addEventListener('click', () => {
        const totalPaginas = Math.ceil(comprasFiltradas.length / itensPorPagina);
        if (paginaAtual < totalPaginas) {
            paginaAtual++;
            renderizarCompras();
        }
    });
}

function exportarCompras() {
    if (comprasFiltradas.length === 0) {
        mostrarMensagem('Nenhum dado para exportar', 'warning');
        return;
    }
    
    // Criar CSV
    const headers = ['Data', 'Rifa', 'Números', 'Total', 'Status', 'Prêmio'];
    const rows = comprasFiltradas.map(compra => [
        formatarDataHora(compra.data_compra),
        compra.rifa_nome,
        compra.numeros.join(', '),
        compra.valor_total,
        compra.premiado ? 'Premiado' : compra.status,
        compra.premiado ? compra.premio : '-'
    ]);
    
    const csvContent = [headers, ...rows].map(row => row.join(';')).join('\n');
    const blob = new Blob(["\uFEFF" + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.href = url;
    link.setAttribute('download', `minhas_compras_${formatarData(new Date())}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    mostrarMensagem('Exportação concluída!', 'success');
}