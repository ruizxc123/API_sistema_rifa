document.addEventListener('DOMContentLoaded', async () => {
    await verificarAutenticacao();
    await carregarPerfil();
    await carregarReservasAtivas();
    await carregarMeusBilhetes();
});

document.addEventListener('DOMContentLoaded', async () => {
    await verificarAutenticacao();
    
    // Verificar se é admin
    const session = await API.getSession();
    const isAdmin = session.usuario?.tipo === 'admin';
    
    // Esconder botões de reservas e bilhetes se for admin
    if (isAdmin) {
        const btnReservas = document.getElementById('btn-reservas');
        const btnBilhetes = document.getElementById('btn-bilhetes');
        if (btnReservas) btnReservas.style.display = 'none';
        if (btnBilhetes) btnBilhetes.style.display = 'none';
        
        // Mostrar apenas dados pessoais
        mostrarAba('dados');
    } else {
        // Usuário normal - mostrar tudo
        await carregarPerfil();
        await carregarReservasAtivas();
        await carregarMeusBilhetes();
    }
});

function mostrarAba(aba) {
    document.getElementById('aba-dados').style.display = aba === 'dados' ? 'block' : 'none';
    document.getElementById('aba-reservas').style.display = aba === 'reservas' ? 'block' : 'none';
    document.getElementById('aba-bilhetes').style.display = aba === 'bilhetes' ? 'block' : 'none';
}

async function carregarPerfil() {
    const session = await API.getSession();
    if (!session.usuario) return;
    
    document.getElementById('nome').value = session.usuario.nome || '';
    document.getElementById('email').value = session.usuario.email || '';
    document.getElementById('telefone').value = session.usuario.telefone || '';
    document.getElementById('cpf').value = session.usuario.cpf || '';
    
    const iniciais = (session.usuario.nome || 'U').split(' ').map(n => n[0]).join('').substring(0, 2);
    document.getElementById('avatar-iniciais').textContent = iniciais.toUpperCase();
    document.getElementById('perfil-nome').textContent = session.usuario.nome;
    document.getElementById('perfil-email').textContent = session.usuario.email;
}

async function carregarReservasAtivas() {
    const container = document.getElementById('reservas-container');
    try {
        const reservas = await API.getReservasAtivas();
        if (!reservas || reservas.length === 0) {
            container.innerHTML = '<p>Nenhuma reserva ativa</p>';
            return;
        }
        
        container.innerHTML = reservas.map(r => `
            <div class="reserva-card" style="border:1px solid var(--warning); border-radius:12px; padding:15px; margin-bottom:15px;">
                <p><strong>${r.rifa_nome}</strong></p>
                <p>Números: ${r.numeros.join(', ')}</p>
                <p>Total: ${formatarMoeda(r.valor_total)}</p>
                <p>Expira: ${formatarDataHora(r.data_expiracao)}</p>
                <button onclick="finalizarCompra(${r.id_reserva})" class="btn-primary">Finalizar Compra</button>
                <button onclick="cancelarReserva(${r.id_reserva})" class="btn-outline">Cancelar</button>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = '<p>Erro ao carregar reservas</p>';
    }
}

async function carregarMeusBilhetes() {
    const container = document.getElementById('bilhetes-container');
    
    try {
        const bilhetes = await API.getMeusBilhetes();
        
        if (!bilhetes || bilhetes.length === 0) {
            container.innerHTML = '<p>🎫 Você ainda não tem bilhetes. <a href="index.html#rifas">Compre agora!</a></p>';
            return;
        }
        
        container.innerHTML = bilhetes.map(b => `
            <div style="border: 1px solid #e5e7eb; border-radius: 12px; padding: 15px; margin-bottom: 15px; ${b.premiado ? 'background: #fef3c7; border-left: 4px solid #f59e0b;' : 'background: white;'}">
                <div style="display: flex; justify-content: space-between;">
                    <strong>${b.rifa_nome}</strong>
                    ${b.premiado ? '<span style="background: #f59e0b; color: white; padding: 2px 10px; border-radius: 20px; font-size: 12px;">🏆 PREMIADO</span>' : ''}
                </div>
                <div style="font-size: 20px; font-weight: bold; margin: 10px 0;">Nº ${b.numero.toString().padStart(3, '0')}</div>
                ${b.premiado ? `<div style="background: #fff; padding: 10px; border-radius: 8px; margin: 10px 0;"><strong>🎉 Você ganhou!</strong> ${b.premio}</div>` : ''}
                <div style="display: flex; gap: 15px; font-size: 12px; color: #666;">
                    <span>💰 ${formatarMoeda(b.valor)}</span>
                    <span>📅 ${formatarDataHora(b.data_compra)}</span>
                </div>
            </div>
        `).join('');
        
        const premiados = bilhetes.filter(b => b.premiado).length;
        if (premiados > 0) {
            mostrarMensagem(`🎉 Parabéns! Você tem ${premiados} bilhete(s) premiado(s)!`, 'success');
        }
        
    } catch (error) {
        console.error(error);
        container.innerHTML = '<p>Erro ao carregar bilhetes</p>';
    }
}

async function finalizarCompra(reservaId) {
    loading(true);
    try {
        const result = await API.simularPagamento(reservaId, 'pix');
        if (result.sucesso) {
            mostrarMensagem('✅ Compra finalizada!', 'success');
            await carregarReservasAtivas();
            await carregarMeusBilhetes();
        }
    } catch (error) {
        mostrarMensagem('Erro ao finalizar', 'error');
    } finally { loading(false); }
}

async function cancelarReserva(reservaId) {
    if (!confirm('Cancelar esta reserva?')) return;
    loading(true);
    try {
        await API.cancelarReserva(reservaId);
        mostrarMensagem('Reserva cancelada', 'success');
        await carregarReservasAtivas();
    } catch (error) {
        mostrarMensagem('Erro ao cancelar', 'error');
    } finally { loading(false); }
}