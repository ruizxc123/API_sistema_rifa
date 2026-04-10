let isAdmin = false;

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🔍 Iniciando admin...');
    
    // Verificar se está logado
    const session = await API.getSession();
    console.log('📦 Sessão:', session);
    
    if (!session || !session.usuario_id) {
        console.log('❌ Não logado, redirecionando para login');
        window.location.href = 'login.html';
        return;
    }
    
    // Verificar se é admin
    const token = localStorage.getItem('token');
    console.log('🔑 Token existe?', !!token);
    
    try {
        const response = await fetch(`${CONFIG.API_URL}/session`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const sessionData = await response.json();
        console.log('📡 Dados da sessão:', sessionData);
        
        const userType = sessionData.usuario?.tipo;
        console.log('👤 Tipo do usuário:', userType);
        
        if (userType === 'admin') {
            isAdmin = true;
            console.log('✅ Usuário é admin!');
            
            // Atualizar menu com nome do admin
            atualizarUILogado({ nome: sessionData.usuario?.nome || 'Admin' });
            
            // Carregar dados do admin
            carregarStats();
            carregarRifasAdmin();
        } else {
            console.log('❌ Usuário não é admin, redirecionando');
            mostrarMensagem('Acesso negado. Área restrita para administradores.', 'error');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 2000);
        }
    } catch (error) {
        console.error('❌ Erro ao verificar admin:', error);
        window.location.href = 'index.html';
    }
});

async function carregarStats() {
    const token = localStorage.getItem('token');
    
    try {
        // Buscar rifas
        const rifas = await API.listarRifas();
        
        // Buscar usuários
        const usuariosResponse = await fetch(`${CONFIG.API_URL}/admin/usuarios`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const usuarios = await usuariosResponse.json();
        
        const vendidos = rifas.reduce((acc, r) => acc + (r.vendidos || 0), 0);
        const finalizadas = rifas.filter(r => r.status === 'finalizada').length;
        
        document.getElementById('total-rifas').textContent = rifas.length || 0;
        document.getElementById('total-vendidos').textContent = vendidos;
        document.getElementById('total-usuarios').textContent = usuarios.length || 0;
        document.getElementById('total-finalizadas').textContent = finalizadas;
    } catch (error) {
        console.error('Erro ao carregar stats:', error);
    }
}

async function carregarRifasAdmin() {
    const tbody = document.getElementById('rifas-list');
    const token = localStorage.getItem('token');
    
    if (!tbody) return;
    
    try {
        const rifas = await fetch(`${CONFIG.API_URL}/admin/rifas`, {
            headers: { 'Authorization': `Bearer ${token}` }
        }).then(r => r.json());
        
        if (!rifas || rifas.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7">Nenhuma rifa cadastrada</td></tr>';
            return;
        }
        
        tbody.innerHTML = rifas.map(rifa => `
            <tr>
                <td>${rifa.id_rifa}</td>
                <td>${rifa.nome}</td>
                <td>${rifa.premio?.substring(0, 30) || ''}...</td>
                <td>R$ ${parseFloat(rifa.valor_bilhete).toFixed(2)}</td>
                <td>${rifa.vendidos || 0}/${rifa.total_numeros}</td>
                <td>
                    <span class="status-badge status-${rifa.status}">${rifa.status}</span>
                </td>
                <td>
                    <button class="btn-primary btn-sm" onclick="verRifa(${rifa.id_rifa})">Ver</button>
                    ${rifa.status === 'ativa' ? `<button class="btn-sm btn-sortear" onclick="realizarSorteio(${rifa.id_rifa})">Sortear</button>` : ''}
                </td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Erro ao carregar rifas:', error);
        tbody.innerHTML = '<tr><td colspan="7">Erro ao carregar dados</td></tr>';
    }
}

function verRifa(id) {
    window.location.href = `rifa-detalhe.html?id=${id}`;
}

async function realizarSorteio(id) {
    if (!confirm('Tem certeza que deseja realizar o sorteio desta rifa?')) return;
    
    loading(true);
    const token = localStorage.getItem('token');
    
    try {
        const response = await fetch(`${CONFIG.API_URL}/admin/rifas/${id}/sorteio`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        
        const result = await response.json();
        
        if (result.sucesso) {
            mostrarMensagem(`🎉 Sorteio realizado! Número vencedor: ${result.vencedor.numero}`, 'success');
            carregarRifasAdmin();
            carregarStats();
        } else {
            mostrarMensagem(result.erro, 'error');
        }
    } catch (error) {
        mostrarMensagem('Erro ao realizar sorteio', 'error');
    } finally {
        loading(false);
    }
}