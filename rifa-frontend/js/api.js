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
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // Adicionar token se existir
        if (TOKEN) {
            headers['Authorization'] = `Bearer ${TOKEN}`;
        }
        
        const config = {
            headers: headers,
            ...options
        };
        
        try {
            const response = await fetch(`${CONFIG.API_URL}${endpoint}`, config);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.erro || error.mensagem || 'Erro na requisição');
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Erro na API (${endpoint}):`, error);
            throw error;
        }
    },
    
    // Login - guarda o token
    async login(email, senha) {
        const response = await fetch(`${CONFIG.API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, senha })
        });
        
        const data = await response.json();
        
        if (data.sucesso && data.token) {
            setToken(data.token);
        }
        
        if (!response.ok) {
            throw new Error(data.erro || 'Erro no login');
        }
        
        return data;
    },
    
    logout() {
        setToken(null);
        return Promise.resolve({ sucesso: true });
    },
    
    async getSession() {
        if (!TOKEN) {
            return { usuario_id: null };
        }
        
        try {
            const response = await fetch(`${CONFIG.API_URL}/session`, {
                headers: { 'Authorization': `Bearer ${TOKEN}` }
            });
            return await response.json();
        } catch {
            return { usuario_id: null };
        }
    },
    
    registrar(usuario) {
        return this.request('/usuarios/registrar', {
            method: 'POST',
            body: JSON.stringify(usuario)
        });
    },
    
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
        body: JSON.stringify({ rifa_id: rifaId, numeros: numeros })
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
        body: JSON.stringify({ reserva_id: reservaId, metodo: metodo })
    });
},

getMeusBilhetes() {
    return this.request('/meus-bilhetes');
},
};

