// numeros.js
console.log('✅ numeros.js carregado com sucesso!');

let numerosSelecionados = [];
let numerosDisponiveis = [];
let numerosReservados = [];
let numerosPagos = [];

async function carregarMapaNumeros(rifaId) {
    console.log('🔄 carregarMapaNumeros chamada para rifa:', rifaId);
    const grid = document.getElementById('numeros-grid');
    if (!grid) {
        console.error('❌ Grid não encontrado');
        return;
    }
    
    grid.innerHTML = '<div class=\"loading-spinner\">Carregando números...</div>';
    
    try {
        const data = await API.getNumerosRifa(rifaId);
        console.log('📦 Dados recebidos:', data);
        
        numerosDisponiveis = data.disponiveis || [];
        numerosReservados = data.reservados || [];
        numerosPagos = data.pagos || [];
        
        renderizarMapaNumeros(data.total || 100);
    } catch (error) {
        console.error('❌ Erro:', error);
        grid.innerHTML = '<p class=\"error\">Erro ao carregar números</p>';
    }
}

function renderizarMapaNumeros(totalNumeros) {
    console.log('🎨 Renderizando', totalNumeros, 'números');
    const grid = document.getElementById('numeros-grid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    for (let i = 1; i <= totalNumeros; i++) {
        const div = document.createElement('div');
        div.className = 'numero';
        
        if (numerosPagos.includes(i)) {
            div.className += ' pago';
            div.textContent = '✓';
            div.title = 'Vendido';
        } else if (numerosReservados.includes(i)) {
            div.className += ' reservado';
            div.textContent = '⏳';
            div.title = 'Reservado';
        } else {
            div.className += ' disponivel';
            div.textContent = i;
            div.title = 'Clique para selecionar';
            div.onclick = (function(num) {
                return function() { toggleNumero(num); };
            })(i);
        }
        
        if (numerosSelecionados.includes(i)) {
            div.className += ' selecionado';
        }
        
        grid.appendChild(div);
    }
    console.log('✅ Grid renderizado com', grid.children.length, 'números');
}

function toggleNumero(numero) {
    console.log('🖱️ Número clicado:', numero);
    
    if (numerosSelecionados.includes(numero)) {
        numerosSelecionados = numerosSelecionados.filter(n => n !== numero);
    } else {
        numerosSelecionados.push(numero);
    }
    
    if (typeof atualizarCarrinho === 'function') {
        atualizarCarrinho();
    }
    renderizarMapaNumeros(100);
}
