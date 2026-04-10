async function carregarRifas() {
    const container = document.getElementById('rifas-grid');
    if (!container) return;
    
    try {
        const rifas = await API.listarRifas();
        if (rifas.length === 0) {
            container.innerHTML = '<p class="empty-state">Nenhuma rifa ativa no momento</p>';
            return;
        }
        
        container.innerHTML = rifas.map(rifa => `
            <div class="rifa-card">
                <img src="${rifa.imagem || 'assets/img/placeholder.jpg'}" alt="${rifa.nome}">
                <div class="rifa-info">
                    <h3>${rifa.nome}</h3>
                    <p class="descricao">${rifa.descricao.substring(0, 100)}...</p>
                    <div class="rifa-detalhes">
                        <span>🏆 ${rifa.premio.substring(0, 50)}</span>
                        <span>💰 ${formatarMoeda(rifa.valor_bilhete)}</span>
                        <span>🎲 ${rifa.total_numeros} números</span>
                        <span>📅 Sorteio: ${formatarData(rifa.data_sorteio)}</span>
                    </div>
                    <a href="rifa-detalhe.html?id=${rifa.id_rifa}" class="btn-primary">Comprar Números</a>
                </div>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = '<p class="error">Erro ao carregar rifas</p>';
    }
}