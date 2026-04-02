const API = {
    async request(endpoint, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            credentials: 'include', // Importante para session
            ...options
        };
        
        try {
            const response = await fetch(`${CONFIG.API_URL}${endpoint}`, config);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.mensagem || 'Erro na requisição');
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Erro na API (${endpoint}):`, error);
            throw error;
        }
    },
    
    // Usuário
    login(email, senha) {
        return this.request('/login', {
            method: 'POST',
            body: JSON.stringify({ email, senha })
        });
    },
    
    logout() {
        return this.request('/logout', { method: 'POST' });
    },
    
    registrar(usuario) {
        return this.request('/usuarios/registrar', {
            method: 'POST',
            body: JSON.stringify(usuario)
        });
    },
    
    getSession() {
        return this.request('/session');
    },
    
    // Rifas
    listarRifas() {
        return this.request('/rifas');
    },
    
    getRifa(id) {
        return this.request(`/rifas/${id}`);
    },
    
    getNumerosRifa(id) {
        return this.request(`/rifas/${id}/numeros`);
    },
    
    // Reservas
    criarReserva(rifaId, numeros) {
        return this.request('/reservas/criar', {
            method: 'POST',
            body: JSON.stringify({ rifa_id: rifaId, numeros })
        });
    },
    
    getReservasAtivas() {
        return this.request('/reservas/ativas');
    },
    
    cancelarReserva(reservaId) {
        return this.request(`/reservas/${reservaId}/cancelar`, {
            method: 'DELETE'
        });
    },
    
    // Pagamento
    simularPagamento(reservaId, metodo) {
        return this.request('/pagamentos/simular', {
            method: 'POST',
            body: JSON.stringify({ reserva_id: reservaId, metodo })
        });
    },
    
    // Usuário
    getMeusBilhetes() {
        return this.request('/meus-bilhetes');
    },
    
    getHistoricoCompras() {
        return this.request('/historico-compras');
    },
    
    getNotificacoes() {
        return this.request('/notificacoes');
    },
    
    marcarNotificacaoLida(id) {
        return this.request(`/notificacoes/${id}/lida`, {
            method: 'PUT'
        });
    }
};