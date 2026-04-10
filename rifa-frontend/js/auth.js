// js/auth.js
async function verificarAutenticacao() {
    try {
        const session = await API.getSession();
        
        if (!session.usuario_id) {
            const paginaAtual = window.location.pathname;
            if (!paginaAtual.includes('login.html') && 
                !paginaAtual.includes('cadastro.html')) {
                window.location.href = 'login.html';
            }
            return false;
        }
        
        atualizarUILogado(session.usuario);
        return true;
    } catch (error) {
        console.error('Erro ao verificar sessão:', error);
        return false;
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
        const result = await API.registrar(usuario);
        
        if (result.sucesso) {
            mostrarMensagem('Cadastro realizado com sucesso! Faça login.');
            window.location.href = 'login.html';
        } else {
            mostrarMensagem(result.erro || 'Erro ao cadastrar', 'error');
        }
    } catch (error) {
        console.error('Erro no cadastro:', error);
        mostrarMensagem(error.message || 'Erro ao cadastrar', 'error');
    } finally {
        loading(false);
    }
}

async function fazerLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;
    
    loading(true);
    
    try {
        const result = await API.login(email, senha);
        
        if (result.sucesso) {
            mostrarMensagem('Login realizado com sucesso!');
            window.location.href = 'index.html';
        }
    } catch (error) {
        mostrarMensagem(error.message, 'error');
    } finally {
        loading(false);
    }
}

async function logout() {
    await API.logout();
    window.location.href = 'index.html';
}

function atualizarUILogado(usuario) {
    const userMenu = document.getElementById('user-menu');
    if (userMenu) {
        userMenu.innerHTML = `
            <div class="dropdown">
                <button class="dropdown-btn">👤 ${usuario.nome.split(' ')[0]}</button>
                <div class="dropdown-content">
                    <a href="meu-perfil.html">Meu Perfil</a>
                    <a href="minhas-compras.html">Minhas Compras</a>
                    <a href="#" onclick="logout()">Sair</a>
                </div>
            </div>
        `;
    }
}