let TOKEN = localStorage.getItem('token');

function setToken(token) {
    TOKEN = token;
    if (token) {
        localStorage.setItem('token', token);
    } else {
        localStorage.removeItem('token');
    }
}

const API = {
    async request(endpoint, options = {}) {
        const headers = { 'Content-Type': 'application/json' };
        if (TOKEN) headers['Authorization'] = `Bearer ${TOKEN}`;
        
        const response = await fetch(`${CONFIG.API_URL}${endpoint}`, {
            ...options,
            headers: { ...headers, ...options.headers }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.erro || 'Erro na requisição');
        }
        return response.json();
    },
    
    async login(email, senha) {
        const response = await fetch(`${CONFIG.API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, senha })
        });
        const data = await response.json();
        if (data.token) setToken(data.token);
        return data;
    },
    
    logout() { setToken(null); return Promise.resolve({ sucesso: true }); },
    
    async getSession() {
    if (!TOKEN) {
        return { usuario_id: null };
    }
    
    try {
        const response = await fetch(`${CONFIG.API_URL}/session`, {
            headers: { 'Authorization': `Bearer ${TOKEN}` }
        });
        const data = await response.json();
        return data;
    } catch (error) {
        return { usuario_id: null };
    }
},
    
    registrar(usuario) {
        return this.request('/usuarios/registrar', { method: 'POST', body: JSON.stringify(usuario) });
    },
    
    listarRifas() { return this.request('/rifas'); },
    getRifa(id) { return this.request(`/rifas/${id}`); },
    getNumerosRifa(id) { return this.request(`/rifas/${id}/numeros`); },
    
    criarReserva(rifaId, numeros) {
        return this.request('/reservas/criar', {
            method: 'POST',
            body: JSON.stringify({ rifa_id: rifaId, numeros })
        });
    },
    
    getReservasAtivas() { return this.request('/reservas/ativas'); },
    cancelarReserva(reservaId) { return this.request(`/reservas/${reservaId}/cancelar`, { method: 'DELETE' }); },
    simularPagamento(reservaId, metodo) {
        return this.request('/pagamentos/simular', {
            method: 'POST',
            body: JSON.stringify({ reserva_id: reservaId, metodo })
        });
    },
    getMeusBilhetes() { return this.request('/meus-bilhetes'); }
};