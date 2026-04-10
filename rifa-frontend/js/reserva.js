let reservaAtual = null;

async function reservarNumeros() {
    if (!numerosSelecionados || numerosSelecionados.length === 0) {
        mostrarMensagem('Selecione pelo menos um número', 'warning');
        return;
    }
    
    const token = localStorage.getItem('token');
    if (!token) {
        mostrarMensagem('Faça login para reservar números', 'warning');
        setTimeout(() => window.location.href = 'login.html', 1500);
        return;
    }
    
    loading(true);
    
    try {
        const result = await API.criarReserva(rifaAtualId, numerosSelecionados);
        reservaAtual = result;
        
        abrirModalPagamento(result);
        
    } catch (error) {
        mostrarMensagem(error.message || 'Erro ao reservar números', 'error');
        await carregarMapaNumeros(rifaAtualId);
    } finally {
        loading(false);
    }
}

function abrirModalPagamento(reserva) {
    const modal = document.getElementById('modal-pagamento');
    const reservaNumeros = document.getElementById('reserva-numeros');
    const reservaTotal = document.getElementById('reserva-total');
    
    if (!modal) return;
    
    const numerosOrdenados = reserva.numeros.sort((a, b) => a - b);
    reservaNumeros.textContent = numerosOrdenados.join(', ');
    reservaTotal.textContent = formatarMoeda(reserva.valor_total);
    
    iniciarTimer(reserva.expira_em, async () => {
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
    if (modal) modal.classList.add('hidden');
    if (typeof pararTimer === 'function') pararTimer();
}

async function cancelarReserva() {
    if (!reservaAtual) return;
    
    loading(true);
    
    try {
        await API.cancelarReserva(reservaAtual.reserva_id);
        mostrarMensagem('Reserva cancelada com sucesso', 'success');
        fecharModalPagamento();
        
        await carregarMapaNumeros(rifaAtualId);
        numerosSelecionados = [];
        atualizarCarrinho();
        
    } catch (error) {
        mostrarMensagem('Erro ao cancelar reserva', 'error');
    } finally {
        loading(false);
    }
}