// js/reserva.js
let reservaAtual = null;

async function reservarNumeros() {
    if (numerosSelecionados.length === 0) {
        mostrarMensagem('Selecione pelo menos um número', 'warning');
        return;
    }
    
    // Verificar se está logado
    try {
        const session = await API.getSession();
        if (!session.usuario_id) {
            mostrarMensagem('Faça login para reservar números', 'warning');
            setTimeout(() => window.location.href = 'login.html', 1500);
            return;
        }
    } catch (error) {
        mostrarMensagem('Faça login para reservar números', 'warning');
        window.location.href = 'login.html';
        return;
    }
    
    loading(true);
    
    try {
        const result = await API.criarReserva(rifaAtualId, numerosSelecionados);
        reservaAtual = result;
        
        // Abrir modal de pagamento
        abrirModalPagamento(result);
        
    } catch (error) {
        mostrarMensagem(error.message || 'Erro ao reservar números', 'error');
        // Recarregar números para atualizar disponibilidade
        await carregarMapaNumeros(rifaAtualId);
    } finally {
        loading(false);
    }
}

function abrirModalPagamento(reserva) {
    const modal = document.getElementById('modal-pagamento');
    const reservaNumeros = document.getElementById('reserva-numeros');
    const reservaTotal = document.getElementById('reserva-total');
    
    // Mostrar números reservados
    const numerosOrdenados = reserva.numeros.sort((a, b) => a - b);
    reservaNumeros.textContent = numerosOrdenados.join(', ');
    reservaTotal.textContent = formatarMoeda(reserva.valor_total);
    
    // Iniciar timer
    iniciarTimer(reserva.expira_em, async () => {
        // Callback quando expirar
        fecharModalPagamento();
        mostrarMensagem('⏰ Tempo esgotado! Sua reserva foi cancelada.', 'warning');
        await carregarMapaNumeros(rifaAtualId);
        numerosSelecionados = [];
        atualizarCarrinho();
    });
    
    modal.classList.remove('hidden');
}

function fecharModalPagamento() {
    const modal = document.getElementById('modal-pagamento');
    modal.classList.add('hidden');
    pararTimer();
}

async function cancelarReserva() {
    if (!reservaAtual) return;
    
    loading(true);
    
    try {
        await API.cancelarReserva(reservaAtual.reserva_id);
        mostrarMensagem('Reserva cancelada com sucesso', 'success');
        fecharModalPagamento();
        
        // Recarregar números
        await carregarMapaNumeros(rifaAtualId);
        numerosSelecionados = [];
        atualizarCarrinho();
        
    } catch (error) {
        mostrarMensagem('Erro ao cancelar reserva', 'error');
    } finally {
        loading(false);
    }
}