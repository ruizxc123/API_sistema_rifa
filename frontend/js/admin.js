document.addEventListener('DOMContentLoaded', async () => {
    await verificarAutenticacao();
    
    const session = await API.getSession();
    if (session.usuario?.tipo !== 'admin') {
        mostrarMensagem('Acesso negado', 'error');
        window.location.href = 'index.html';
        return;
    }
    
    carregarStats();
    carregarRifasAdmin();
});

async function carregarStats() {
    try {
        const rifas = await API.listarRifas();
        document.getElementById('total-rifas').textContent = rifas.length;
        
        const vendidos = rifas.reduce((acc, r) => acc + (r.vendidos || 0), 0);
        document.getElementById('total-vendidos').textContent = vendidos;
        
        const finalizadas = rifas.filter(r => r.status === 'finalizada').length;
        document.getElementById('total-finalizadas').textContent = finalizadas;
        
        const usuarios = await fetch(`${CONFIG.API_URL}/admin/usuarios`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        }).then(r => r.json()).catch(() => []);
        document.getElementById('total-usuarios').textContent = usuarios.length || 0;
    } catch (error) {
        console.error('Erro ao carregar stats:', error);
    }
}

let sorteioRifaId = null;

async function abrirModalSorteio(id, nome, totalBilhetes) {
    console.log('Abrindo modal para rifa:', id);
    sorteioRifaId = id;
    document.getElementById('sorteio-rifa-nome').textContent = nome;
    document.getElementById('sorteio-total-bilhetes').textContent = totalBilhetes;
    document.getElementById('modal-sorteio').classList.remove('hidden');
}

function fecharModalSorteio() {
    document.getElementById('modal-sorteio').classList.add('hidden');
    // Não limpar o ID imediatamente
}

async function realizarSorteioConfirmado() {
    console.log('Realizando sorteio para rifa:', sorteioRifaId);
    
    if (!sorteioRifaId) {
        mostrarMensagem('Erro: ID da rifa não encontrado', 'error');
        return;
    }
    
    fecharModalSorteio();
    loading(true);
    
    try {
        const token = localStorage.getItem('token');
        console.log('Token:', token ? 'OK' : 'Não tem token');
        
        const response = await fetch(`${CONFIG.API_URL}/admin/rifas/${sorteioRifaId}/sorteio`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        
        console.log('Response status:', response.status);
        const result = await response.json();
        console.log('Resultado:', result);
        
        if (response.ok && result.sucesso) {
            mostrarMensagem(`🎉 Sorteio realizado! Número vencedor: ${result.vencedor.numero}`, 'success');
            carregarRifasAdmin();
            carregarStats();
        } else {
            mostrarMensagem(result.erro || 'Erro ao realizar sorteio', 'error');
        }
    } catch (error) {
        console.error('Erro detalhado:', error);
        mostrarMensagem('Erro ao conectar com o servidor', 'error');
    } finally {
        loading(false);
        sorteioRifaId = null;
    }
}


async function carregarRifasAdmin() {
    const tbody = document.getElementById('rifas-list');
    try {
        const rifas = await fetch(`${CONFIG.API_URL}/admin/rifas`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        }).then(r => r.json());
        
        if (!rifas || rifas.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7">Nenhuma rifa</td></tr>';
            return;
        }
        
        tbody.innerHTML = rifas.map(r => {
            const bilhetesVendidos = r.vendidos || 0;
            return `
            <tr>
                <td>${r.id_rifa}</td>
                <td>${r.nome}</td>
                <td>${r.premio?.substring(0, 30) || ''}...</td>
                <td>R$ ${parseFloat(r.valor_bilhete).toFixed(2)}</td>
                <td>${bilhetesVendidos}/${r.total_numeros}</td>
                <td><span class="status-badge status-${r.status}">${r.status}</span></td>
                <td>
                    <button class="btn-primary btn-sm" onclick="verRifa(${r.id_rifa})">Ver</button>
                    ${r.status === 'ativa' && bilhetesVendidos > 0 ? 
                        `<button class="btn-sm btn-sortear" onclick="abrirModalSorteio(${r.id_rifa}, '${r.nome}', ${bilhetesVendidos})">Sortear</button>` : 
                        (r.status === 'ativa' && bilhetesVendidos === 0 ? 
                            '<span class="badge-warning">Sem bilhetes</span>' : '')
                    }
                </td>
            </tr>
        `}).join('');
        
        // Adicionar evento ao botão confirmar
        document.getElementById('confirmar-sorteio-btn').onclick = realizarSorteioConfirmado;
        
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="7">Erro ao carregar</td></tr>';
    }
}

function verRifa(id) { window.location.href = `rifa-detalhe.html?id=${id}`; }

async function realizarSorteio(id) {
    if (!confirm('Realizar sorteio desta rifa?')) return;
    loading(true);
    try {
        const response = await fetch(`${CONFIG.API_URL}/admin/rifas/${id}/sorteio`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const result = await response.json();
        if (result.sucesso) {
            mostrarMensagem(`🎉 Número vencedor: ${result.vencedor?.numero || 'Sorteado'}`, 'success');
            carregarRifasAdmin();
            carregarStats();
        } else {
            mostrarMensagem(result.erro, 'error');
        }
    } catch (error) {
        mostrarMensagem('Erro ao sortear', 'error');
    } finally { loading(false); }
}