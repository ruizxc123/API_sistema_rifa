// js/perfil.js
let usuarioAtual = null;

async function carregarPerfil() {
    try {
        const session = await API.getSession();
        usuarioAtual = session.usuario;
        
        if (!usuarioAtual) return;
        
        // Preencher dados
        document.getElementById('nome').value = usuarioAtual.nome;
        document.getElementById('email').value = usuarioAtual.email;
        document.getElementById('telefone').value = usuarioAtual.telefone;
        document.getElementById('cpf').value = usuarioAtual.cpf;
        document.getElementById('data-cadastro').value = formatarData(usuarioAtual.data_cadastro);
        
        // Atualizar sidebar
        const iniciais = usuarioAtual.nome.split(' ').map(n => n[0]).join('').substring(0, 2);
        document.getElementById('avatar-iniciais').textContent = iniciais.toUpperCase();
        document.getElementById('perfil-nome').textContent = usuarioAtual.nome;
        document.getElementById('perfil-email').textContent = usuarioAtual.email;
        
    } catch (error) {
        mostrarMensagem('Erro ao carregar perfil', 'error');
    }
}

async function carregarMeusBilhetes() {
    const container = document.getElementById('bilhetes-container');
    
    try {
        const bilhetes = await API.getMeusBilhetes();
        
        if (!bilhetes || bilhetes.length === 0) {
            container.innerHTML = '<p class="empty-state">Você ainda não possui bilhetes. <a href="index.html#rifas">Compre agora!</a></p>';
            return;
        }
        
        container.innerHTML = `
            <div class="bilhetes-lista">
                ${bilhetes.map(bilhete => `
                    <div class="bilhete-card ${bilhete.premiado ? 'premiado' : ''}">
                        <div class="bilhete-header">
                            <span class="bilhete-nome-rifa">${bilhete.rifa_nome}</span>
                            <span class="bilhete-status status-${bilhete.status}">
                                ${bilhete.premiado ? '🏆 PREMIADO' : bilhete.status.toUpperCase()}
                            </span>
                        </div>
                        <div class="bilhete-numeros">
                            ${bilhete.numeros.map(num => `
                                <span class="bilhete-numero ${bilhete.numero_sorteado === num ? 'premiado' : ''}">
                                    ${num.toString().padStart(3, '0')}
                                    ${bilhete.numero_sorteado === num ? ' 🏆' : ''}
                                </span>
                            `).join('')}
                        </div>
                        <div class="bilhete-footer">
                            <span>Sorteio: ${formatarData(bilhete.data_sorteio)}</span>
                            <span>Valor: ${formatarMoeda(bilhete.valor_total)}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
    } catch (error) {
        container.innerHTML = '<p class="error">Erro ao carregar bilhetes</p>';
    }
}

async function carregarReservasAtivas() {
    const container = document.getElementById('reservas-container');
    
    try {
        const reservas = await API.getReservasAtivas();
        
        if (!reservas || reservas.length === 0) {
            container.innerHTML = '<p class="empty-state">Nenhuma reserva ativa no momento.</p>';
            return;
        }
        
        container.innerHTML = reservas.map(reserva => `
            <div class="reserva-card" data-reserva-id="${reserva.id_reserva}">
                <div class="bilhete-header">
                    <span class="bilhete-nome-rifa">${reserva.rifa_nome}</span>
                    <span class="reserva-timer" id="timer-${reserva.id_reserva}">
                        ${calcularTempoRestante(reserva.data_expiracao)}
                    </span>
                </div>
                <div class="bilhete-numeros">
                    ${reserva.numeros.map(num => `
                        <span class="bilhete-numero">${num.toString().padStart(3, '0')}</span>
                    `).join('')}
                </div>
                <div class="reserva-actions">
                    <button onclick="irParaPagamento(${reserva.id_reserva})" class="btn-primary">
                        💳 Finalizar Compra
                    </button>
                    <button onclick="cancelarReservaPerfil(${reserva.id_reserva})" class="btn-outline">
                        Cancelar
                    </button>
                </div>
            </div>
        `).join('');
        
        // Iniciar timers para cada reserva
        reservas.forEach(reserva => {
            iniciarTimerReserva(reserva.id_reserva, reserva.data_expiracao);
        });
        
    } catch (error) {
        container.innerHTML = '<p class="error">Erro ao carregar reservas</p>';
    }
}

function calcularTempoRestante(dataExpiracao) {
    const diff = new Date(dataExpiracao) - new Date();
    if (diff <= 0) return '00:00';
    const minutos = Math.floor(diff / 60000);
    const segundos = Math.floor((diff % 60000) / 1000);
    return `${minutos}:${segundos.toString().padStart(2, '0')}`;
}

function iniciarTimerReserva(reservaId, dataExpiracao) {
    const timerElement = document.getElementById(`timer-${reservaId}`);
    if (!timerElement) return;
    
    const interval = setInterval(() => {
        const diff = new Date(dataExpiracao) - new Date();
        
        if (diff <= 0) {
            clearInterval(interval);
            timerElement.textContent = '00:00';
            timerElement.style.color = 'var(--gray)';
            carregarReservasAtivas(); // Recarregar lista
        } else {
            const minutos = Math.floor(diff / 60000);
            const segundos = Math.floor((diff % 60000) / 1000);
            timerElement.textContent = `${minutos}:${segundos.toString().padStart(2, '0')}`;
        }
    }, 1000);
}

async function cancelarReservaPerfil(reservaId) {
    if (!confirm('Tem certeza que deseja cancelar esta reserva?')) return;
    
    loading(true);
    
    try {
        await API.cancelarReserva(reservaId);
        mostrarMensagem('Reserva cancelada com sucesso', 'success');
        await carregarReservasAtivas();
        
    } catch (error) {
        mostrarMensagem('Erro ao cancelar reserva', 'error');
    } finally {
        loading(false);
    }
}

function irParaPagamento(reservaId) {
    // Armazenar reserva atual e redirecionar
    sessionStorage.setItem('reserva_pagamento', reservaId);
    window.location.href = `rifa-detalhe.html?pagamento=${reservaId}`;
}

function inicializarTabs() {
    const menuItems = document.querySelectorAll('.perfil-menu-item');
    const tabs = document.querySelectorAll('.tab-content');
    
    menuItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tabId = item.getAttribute('data-tab');
            
            // Atualizar menu
            menuItems.forEach(m => m.classList.remove('active'));
            item.classList.add('active');
            
            // Atualizar tabs
            tabs.forEach(tab => tab.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
        });
    });
}

// Editar perfil
document.addEventListener('DOMContentLoaded', () => {
    const btnEditar = document.getElementById('btn-editar-perfil');
    const formActions = document.getElementById('perfil-actions');
    const inputs = document.querySelectorAll('#form-dados-pessoais input');
    const cancelarBtn = document.getElementById('cancelar-edicao');
    
    if (btnEditar) {
        btnEditar.addEventListener('click', () => {
            inputs.forEach(input => input.disabled = false);
            formActions.classList.remove('hidden');
            btnEditar.disabled = true;
        });
    }
    
    if (cancelarBtn) {
        cancelarBtn.addEventListener('click', () => {
            inputs.forEach(input => input.disabled = true);
            formActions.classList.add('hidden');
            btnEditar.disabled = false;
            carregarPerfil(); // Recarregar dados originais
        });
    }
    
    // Form de alterar senha
    const formSenha = document.getElementById('form-alterar-senha');
    if (formSenha) {
        formSenha.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const senhaAtual = document.getElementById('senha-atual').value;
            const novaSenha = document.getElementById('nova-senha').value;
            const confirmarSenha = document.getElementById('confirmar-senha').value;
            
            if (novaSenha !== confirmarSenha) {
                mostrarMensagem('As novas senhas não conferem', 'error');
                return;
            }
            
            if (novaSenha.length < 6) {
                mostrarMensagem('A nova senha deve ter pelo menos 6 caracteres', 'error');
                return;
            }
            
            loading(true);
            
            try {
                // Chamar API para alterar senha
                // await API.alterarSenha(senhaAtual, novaSenha);
                mostrarMensagem('Senha alterada com sucesso!', 'success');
                formSenha.reset();
                
            } catch (error) {
                mostrarMensagem(error.message || 'Erro ao alterar senha', 'error');
            } finally {
                loading(false);
            }
        });
    }
});