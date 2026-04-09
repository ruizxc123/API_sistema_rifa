// js/rifa.js
async function carregarRifas() {
    const container = document.getElementById('rifas-grid');
    if (!container) return;
    
    try {
        const rifas = await API.listarRifas();
        
        if (rifas.length === 0) {
            container.innerHTML = '<p class="sem-rifas">Nenhuma rifa ativa no momento</p>';
            return;
        }
        
        container.innerHTML = rifas.map(rifa => `
            <div class="rifa-card">
                <img src="${rifa.imagem || 'assets/img/placeholder.jpg'}" alt="${rifa.nome}">
                <div class="rifa-info">
                    <h3>${rifa.nome}</h3>
                    <p class="descricao">${rifa.descricao.substring(0, 100)}...</p>
                    <div class="rifa-detalhes">
                        <span class="premio">🏆 ${rifa.premio.substring(0, 50)}</span>
                        <span class="valor">${formatarMoeda(rifa.valor_bilhete)}</span>
                        <span class="numeros">🎲 ${rifa.total_numeros} números</span>
                        <span class="sorteio">📅 Sorteio: ${formatarData(rifa.data_sorteio)}</span>
                    </div>
                    <a href="rifa-detalhe.html?id=${rifa.id_rifa}" class="btn-primary">Comprar Números</a>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        container.innerHTML = '<p class="error">Erro ao carregar rifas. Tente novamente.</p>';
        console.error(error);
    }
}

async function carregarDetalheRifa() {
    const urlParams = new URLSearchParams(window.location.search);
    const rifaId = urlParams.get('id');
    
    if (!rifaId) {
        window.location.href = 'index.html';
        return;
    }
    
    try {
        const rifa = await API.getRifa(rifaId);
        
        // Preencher informações da rifa
        document.getElementById('rifa-nome').textContent = rifa.nome;
        document.getElementById('rifa-imagem').src = rifa.imagem;
        document.getElementById('rifa-descricao').textContent = rifa.descricao;
        document.getElementById('rifa-premio').textContent = rifa.premio;
        document.getElementById('rifa-valor').textContent = formatarMoeda(rifa.valor_bilhete);
        document.getElementById('rifa-sorteio').textContent = formatarDataHora(rifa.data_sorteio);
        
        // Carregar mapa de números
        await carregarMapaNumeros(rifaId);
        
    } catch (error) {
        mostrarMensagem('Erro ao carregar rifa', 'error');
    }
}