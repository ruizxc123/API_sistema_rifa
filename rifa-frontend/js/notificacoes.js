// js/notificacoes.js
let todasNotificacoes = [];
let filtroAtual = 'todas';

async function carregarNotificacoes() {
    const container = document.getElementById('notificacoes-lista');
    
    try {
        const notificacoes = await API.getNotificacoes();
        todasNotificacoes = notificacoes;
        
        const naoLidas = todasNotificacoes.filter(n => !n.lida).length;
        document.getElementById('unread-count').textContent = naoLidas;
        document.getElementById('unread-count').style.display = naoLidas > 0 ? 'inline-block' : 'none';
        
        aplicarFiltroNotificacoes();
        
    } catch (error) {
        container.innerHTML = '<p class="error">Erro ao carregar notificações</p>';
    }
}

function aplicarFiltroNotificacoes() {
    let notificacoesFiltradas = [...todasNotificacoes];
    
    switch(filtroAtual) {
        case 'nao-lidas':
            notificacoesFiltradas = notificacoesFiltradas.filter(n => !n.lida);
            break;
        case 'compras':
            notificacoesFiltradas = notificacoesFiltradas.filter(n => n.tipo === 'compra');
            break;
        case 'sorteios':
            notificacoesFiltradas = notificacoesFiltradas.filter(n => n.tipo === 'sorteio');
            break;
        case 'sistema':
            notificacoesFiltradas = notificacoesFiltradas.filter(n => n.tipo === 'sistema');
            break;
    }
    
    renderizarNotificacoes(notificacoesFiltradas);
}

function renderizarNotificacoes(notificacoes) {
    const container = document.getElementById('notificacoes-lista');
    const emptyState = document.getElementById('empty-state');
    
    if (notificacoes.length === 0) {
        container.innerHTML = '';
        emptyState.classList.remove('hidden');
        return;
    }
    
    emptyState.classList.add('hidden');
    
    container.innerHTML = notificacoes.map(notif => `
        <div class="notificacao-item ${!notif.lida ? 'nao-lida' : ''}" data-id="${notif.id_notificacao}">
            <div class="notificacao-icon">${getIconeNotificacao(notif.tipo)}</div>
            <div class="notificacao-conteudo">
                <p class="notificacao-mensagem">${notif.mensagem}</p>
                <span class="notificacao-data">${formatarDataHora(notif.data_envio)}</span>
            </div>
            <div class="notificacao-actions">
                ${!notif.lida ? `
                    <button class="btn-marcar-lida" onclick="marcarComoLida(${notif.id_notificacao})" title="Marcar como lida">
                        ✓
                    </button>
                ` : ''}
                <button class="btn-excluir" onclick="excluirNotificacao(${notif.id_notificacao})" title="Excluir">
                    ✕
                </button>
            </div>
        </div>
    `).join('');
}

function getIconeNotificacao(tipo) {
    switch(tipo) {
        case 'compra': return '💰';
        case 'sorteio': return '🏆';
        case 'sistema': return '⚙️';
        default: return '🔔';
    }
}

async function marcarComoLida(id) {
    try {
        await API.marcarNotificacaoLida(id);
        
        // Atualizar localmente
        const notif = todasNotificacoes.find(n => n.id_notificacao === id);
        if (notif) notif.lida = true;
        
        // Recarregar
        await carregarNotificacoes();
        
    } catch (error) {
        mostrarMensagem('Erro ao marcar como lida', 'error');
    }
}

async function excluirNotificacao(id) {
    if (!confirm('Tem certeza que deseja excluir esta notificação?')) return;
    
    try {
        // Chamar API para excluir
        // await API.excluirNotificacao(id);
        
        // Remover localmente
        todasNotificacoes = todasNotificacoes.filter(n => n.id_notificacao !== id);
        
        // Recarregar
        aplicarFiltroNotificacoes();
        
        const naoLidas = todasNotificacoes.filter(n => !n.lida).length;
        document.getElementById('unread-count').textContent = naoLidas;
        
        mostrarMensagem('Notificação excluída', 'success');
        
    } catch (error) {
        mostrarMensagem('Erro ao excluir notificação', 'error');
    }
}

async function marcarTodasComoLidas() {
    const naoLidas = todasNotificacoes.filter(n => !n.lida);
    
    if (naoLidas.length === 0) {
        mostrarMensagem('Não há notificações não lidas', 'warning');
        return;
    }
    
    loading(true);
    
    try {
        for (const notif of naoLidas) {
            await API.marcarNotificacaoLida(notif.id_notificacao);
            notif.lida = true;
        }
        
        await carregarNotificacoes();
        mostrarMensagem('Todas notificações marcadas como lidas', 'success');
        
    } catch (error) {
        mostrarMensagem('Erro ao marcar notificações', 'error');
    } finally {
        loading(false);
    }
}

async function limparTodasNotificacoes() {
    if (!confirm('Tem certeza que deseja excluir TODAS as notificações? Esta ação não pode ser desfeita.')) return;
    
    loading(true);
    
    try {
        // Chamar API para limpar todas
        // await API.limparNotificacoes();
        
        todasNotificacoes = [];
        aplicarFiltroNotificacoes();
        document.getElementById('unread-count').textContent = 0;
        
        mostrarMensagem('Todas notificações foram removidas', 'success');
        
    } catch (error) {
        mostrarMensagem('Erro ao limpar notificações', 'error');
    } finally {
        loading(false);
    }
}

function inicializarFiltrosNotificacoes() {
    const tabs = document.querySelectorAll('.filtro-tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            filtroAtual = tab.getAttribute('data-filtro');
            aplicarFiltroNotificacoes();
        });
    });
    
    document.getElementById('marcar-todas-lidas')?.addEventListener('click', marcarTodasComoLidas);
    document.getElementById('limpar-todas')?.addEventListener('click', limparTodasNotificacoes);
}