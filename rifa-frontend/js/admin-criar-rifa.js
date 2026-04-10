document.addEventListener('DOMContentLoaded', async () => {
    // Verificar se está logado e é admin
    const token = localStorage.getItem('token');
    
    if (!token) {
        mostrarMensagem('Faça login para acessar', 'error');
        setTimeout(() => window.location.href = 'login.html', 1500);
        return;
    }
    
    try {
        const response = await fetch(`${CONFIG.API_URL}/session`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const session = await response.json();
        
        if (!session.usuario_id || session.usuario?.tipo !== 'admin') {
            mostrarMensagem('Acesso negado. Área restrita para administradores.', 'error');
            setTimeout(() => window.location.href = 'index.html', 1500);
            return;
        }
        
        // Atualizar menu com nome do admin
        if (session.usuario) {
            atualizarUILogado({ nome: session.usuario.nome || 'Admin' });
        }
        
        // Inicializar preview
        initPreview();
        
    } catch (error) {
        console.error('Erro ao verificar autenticação:', error);
        window.location.href = 'login.html';
    }
    
    // Configurar data mínima para sorteio (hoje + 7 dias)
    const dataInput = document.getElementById('data_sorteio');
    if (dataInput) {
        const minDate = new Date();
        minDate.setDate(minDate.getDate() + 7);
        dataInput.min = minDate.toISOString().slice(0, 16);
    }
    
    // Submit do formulário
    const form = document.getElementById('criar-rifa-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await criarRifa();
    });
});

function initPreview() {
    const inputs = ['nome', 'premio', 'valor_bilhete', 'data_sorteio', 'imagem'];
    
    inputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('input', () => updatePreview());
        }
    });
    
    updatePreview();
}

function updatePreview() {
    const nome = document.getElementById('nome')?.value || 'Nome da Rifa';
    const premio = document.getElementById('premio')?.value || 'Prêmio da rifa';
    const valor = parseFloat(document.getElementById('valor_bilhete')?.value) || 0;
    const dataSorteio = document.getElementById('data_sorteio')?.value;
    const imagem = document.getElementById('imagem')?.value || '';
    
    document.getElementById('preview-nome').textContent = nome;
    document.getElementById('preview-premio').textContent = `🎁 ${premio}`;
    document.getElementById('preview-valor').textContent = `💰 ${formatarMoeda(valor)}`;
    
    if (dataSorteio) {
        const dataFormatada = new Date(dataSorteio).toLocaleDateString('pt-BR');
        document.getElementById('preview-sorteio').textContent = `📅 Sorteio: ${dataFormatada}`;
    }
    
    if (imagem) {
        const previewImg = document.getElementById('preview-img');
        previewImg.src = imagem;
        previewImg.onerror = () => {
            previewImg.src = 'assets/img/placeholder.jpg';
        };
        document.getElementById('preview-area').style.display = 'block';
    } else {
        document.getElementById('preview-area').style.display = 'none';
    }
}

async function criarRifa() {
    const formData = {
        nome: document.getElementById('nome').value,
        descricao: document.getElementById('descricao').value,
        premio: document.getElementById('premio').value,
        valor_bilhete: parseFloat(document.getElementById('valor_bilhete').value),
        total_numeros: parseInt(document.getElementById('total_numeros').value),
        data_sorteio: document.getElementById('data_sorteio').value,
        imagem: document.getElementById('imagem').value || ''
    };
    
    // Validações
    if (!formData.nome || !formData.descricao || !formData.premio || !formData.valor_bilhete || !formData.total_numeros || !formData.data_sorteio) {
        mostrarMensagem('Preencha todos os campos obrigatórios', 'error');
        return;
    }
    
    if (formData.valor_bilhete <= 0) {
        mostrarMensagem('Valor do bilhete deve ser maior que zero', 'error');
        return;
    }
    
    if (formData.total_numeros < 1 || formData.total_numeros > 1000) {
        mostrarMensagem('Total de números deve ser entre 1 e 1000', 'error');
        return;
    }
    
    const dataSorteio = new Date(formData.data_sorteio);
    const hoje = new Date();
    if (dataSorteio <= hoje) {
        mostrarMensagem('Data do sorteio deve ser no futuro', 'error');
        return;
    }
    
    loading(true);
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${CONFIG.API_URL}/admin/rifas`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok && result.sucesso) {
            mostrarMensagem('✅ Rifa criada com sucesso!', 'success');
            
            // Limpar formulário
            document.getElementById('criar-rifa-form').reset();
            updatePreview();
            
            // Perguntar se quer criar outra ou ir para lista
            setTimeout(() => {
                if (confirm('Rifa criada com sucesso! Deseja criar outra rifa?')) {
                    document.getElementById('nome').focus();
                } else {
                    window.location.href = 'admin.html';
                }
            }, 500);
        } else {
            mostrarMensagem(result.erro || 'Erro ao criar rifa', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao conectar com o servidor', 'error');
    } finally {
        loading(false);
    }
}