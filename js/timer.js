// js/timer.js
let timerInterval = null;

function iniciarTimer(dataExpiracao, onExpire) {
    const timerElement = document.getElementById('timer-display');
    if (!timerElement) return;
    
    // Parar timer existente
    pararTimer();
    
    timerInterval = setInterval(() => {
        const agora = new Date();
        const expiracao = new Date(dataExpiracao);
        const diff = expiracao - agora;
        
        if (diff <= 0) {
            pararTimer();
            timerElement.textContent = '00:00';
            timerElement.classList.add('timer-warning');
            
            if (onExpire) onExpire();
        } else {
            const minutos = Math.floor(diff / 60000);
            const segundos = Math.floor((diff % 60000) / 1000);
            timerElement.textContent = `${minutos.toString().padStart(2, '0')}:${segundos.toString().padStart(2, '0')}`;
            
            // Aviso quando faltar 1 minuto
            if (diff <= 60000 && diff > 59000) {
                timerElement.classList.add('timer-warning');
                mostrarMensagem('⚠️ Sua reserva expira em 1 minuto!', 'warning');
            }
        }
    }, 1000);
}

function pararTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}