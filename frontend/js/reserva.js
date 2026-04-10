let timerInterval = null;

async function reservarNumeros() {
    if (!numerosSelecionados || numerosSelecionados.length === 0) {
        mostrarMensagem('Selecione pelo menos um número', 'warning');
        return;
    }
    
    const token = localStorage.getItem('token');
    if (!token) {
        mostrarMensagem('Faça login para reservar', 'warning');
        setTimeout(() => window.location.href = 'login.html', 1500);
        return;
    }
    
    loading(true);
    
    try {
        const result = await API.criarReserva(rifaAtualId, numerosSelecionados);
        window.reservaAtual = result;
        abrirModalPagamento(result);
    } catch (error) {
        mostrarMensagem(error.message || 'Erro ao reservar', 'error');
        await carregarMapaNumeros(rifaAtualId);
    } finally {
        loading(false);
    }
}

function abrirModalPagamento(reserva) {
    const modal = document.getElementById('modal-pagamento');
    document.getElementById('reserva-numeros').textContent = reserva.numeros.join(', ');
    document.getElementById('reserva-total').textContent = formatarMoeda(reserva.valor_total);
    iniciarTimer(reserva.expira_em);
    modal.classList.remove('hidden');
}

function iniciarTimer(dataExpiracao) {
    const timerElement = document.getElementById('timer-display');
    if (timerInterval) clearInterval(timerInterval);
    
    timerInterval = setInterval(() => {
        const diff = new Date(dataExpiracao) - new Date();
        if (diff <= 0) {
            clearInterval(timerInterval);
            timerElement.textContent = '00:00';
            fecharModalPagamento();
            mostrarMensagem('Tempo esgotado!', 'warning');
            carregarMapaNumeros(rifaAtualId);
            numerosSelecionados = [];
            atualizarCarrinho();
        } else {
            const minutos = Math.floor(diff / 60000);
            const segundos = Math.floor((diff % 60000) / 1000);
            timerElement.textContent = `${minutos}:${segundos.toString().padStart(2, '0')}`;
        }
    }, 1000);
}

function pararTimer() {
    if (timerInterval) clearInterval(timerInterval);
}

window.reservarNumeros = reservarNumeros;
window.pararTimer = pararTimer;