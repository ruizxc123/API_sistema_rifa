async function verificarAutenticacao() {
    try {
        const session = await API.getSession();
        if (!session.usuario_id) {
            // Redirecionar para login se não estiver autenticado
            if (!window.location.pathname.includes('login.html') && 
                !window.location.pathname.includes('cadastro.html')) {
                window.location.href = 'login.html';
            }
            return false;
        }
        
        // Atualizar UI com dados do usuário
        atualizarUILogado(session.usuario);
        return true;
    } catch (error) {
        console.error('Erro ao verificar sessão:', error);
        return false;
    }
}

function atualizarUILogado(usuario) {
    const userMenu = document.getElementById('user-menu');
    if (userMenu) {
        userMenu.innerHTML = `
            <div class="dropdown">
                <button class="dropdown-btn">
                    👤 ${usuario.nome.split(' ')[0]}
                </button>
                <div class="dropdown-content">
                    <a href="meu-perfil.html">Meu Perfil</a>
                    <a href="minhas-compras.html">Minhas Compras</a>
                    <a href="notificacoes.html">Notificações</a>
                    <hr>
                    <a href="#" onclick="logout()">Sair</a>
                </div>
            </div>
        `;
    }
}

function atualizarUIDeslogado() {
    const userMenu = document.getElementById('user-menu');
    if (userMenu) {
        userMenu.innerHTML = `
            <a href="login.html" class="btn-outline">Entrar</a>
            <a href="cadastro.html" class="btn-primary">Cadastrar</a>
        `;
    }
}

async function logout() {
    try {
        await API.logout();
        window.location.href = 'index.html';
    } catch (error) {
        mostrarMensagem('Erro ao sair', 'error');
    }
}

async function fazerLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;
    
    loading(true);
    
    try {
        const result = await API.login(email, senha);
        mostrarMensagem('Login realizado com sucesso!');
        window.location.href = 'index.html';
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        loading(false);
    }
}

async function fazerCadastro(event) {
    event.preventDefault();
    
    const usuario = {
        nome: document.getElementById('nome').value,
        email: document.getElementById('email').value,
        cpf: document.getElementById('cpf').value,
        telefone: document.getElementById('telefone').value,
        senha: document.getElementById('senha').value
    };
    
    const senhaConfirm = document.getElementById('senha-confirm').value;
    
    if (usuario.senha !== senhaConfirm) {
        mostrarMensagem('Senhas não conferem', 'error');
        return;
    }
    
    loading(true);
    
    try {
        await API.registrar(usuario);
        mostrarMensagem('Cadastro realizado! Faça login.');
        window.location.href = 'login.html';
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        loading(false);
    }
}