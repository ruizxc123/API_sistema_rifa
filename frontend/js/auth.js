// js/auth.js
async function verificarAutenticacao() {
    try {
        const session = await API.getSession();
        
        if (!session || !session.usuario_id) {
            // Se não estiver logado, mostrar menu de deslogado
            atualizarUIDeslogado();
            return false;
        }
        
        // Se estiver logado, atualizar menu
        atualizarUILogado(session.usuario);
        return true;
    } catch (error) {
        console.error('Erro ao verificar sessão:', error);
        atualizarUIDeslogado();
        return false;
    }
}

function atualizarUILogado(usuario) {
    const userMenu = document.getElementById('user-menu');
    if (!userMenu) return;
    
    const isAdmin = usuario.tipo === 'admin';
   userMenu.innerHTML = `
    <div class="dropdown">
        <button class="btn-user">
            <span class="user-avatar">${usuario.nome.charAt(0).toUpperCase()}</span>
            <span class="user-name">${usuario.nome.split(' ')[0]}</span>
            <span class="user-arrow">▼</span>
        </button>
        <div class="dropdown-content">
            ${isAdmin ? '<a href="admin.html">📊 Admin</a>' : ''}
            <a href="meu-perfil.html">👤 Meu Perfil</a>
            ${!isAdmin ? '<a href="minhas-compras.html">🎫 Meus Bilhetes' : ''}
            <hr>
            <a href="#" onclick="logout()">🚪 Sair</a>
        </div>
    </div>
`;
}

function atualizarUIDeslogado() {
    const userMenu = document.getElementById('user-menu');
    if (!userMenu) return;
    
    userMenu.innerHTML = `
        <a href="login.html" class="btn-outline">Entrar</a>
        <a href="cadastro.html" class="btn-primary">Cadastrar</a>
    `;
}

async function fazerLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;
    
    loading(true);
    
    try {
        const result = await API.login(email, senha);
        
        if (result.sucesso && result.token) {
            localStorage.setItem('token', result.token);
            mostrarMensagem('Login realizado com sucesso!');
            window.location.href = 'index.html';
        } else {
            mostrarMensagem(result.erro || 'Erro ao fazer login', 'error');
        }
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

async function logout() {
    localStorage.removeItem('token');
    window.location.href = 'index.html';
}