
# 🎲 Rifa Online - Sistema Completo de Sorteios e Rifas

Plataforma web completa para gerenciamento de rifas online, com área de clientes, painel administrativo, sorteios automatizados e simulação de pagamentos.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Execução](#instalação-e-execução)
  - [Backend (API)](#backend-api)
  - [Frontend (Interface)](#frontend-interface)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [API Endpoints](#api-endpoints)
- [Painel Administrativo](#painel-administrativo)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Documentação Completa](#documentação-completa)
- [Licença](#licença)

## 🚀 Sobre o Projeto

O **Rifa Online** é um sistema completo para criação e gerenciamento de rifas online. Desenvolvido com Flask no backend e HTML/CSS/JavaScript puro no frontend, oferece:

- Cadastro e autenticação de usuários com validação de CPF
- Compra de bilhetes numerados com reserva temporária
- Simulação de pagamentos (PIX, cartão, boleto)
- Sorteio automático com auditoria (hash público)
- Painel administrativo completo
- Histórico de compras e notificações

Ideal para organizadores de rifas que buscam uma solução profissional, transparente e escalável.

## ✨ Funcionalidades

### 👥 Área do Cliente
- Cadastro e login com sessão JWT
- Visualização de rifas ativas com contagem regressiva
- Seleção de números em grid interativo
- Carrinho de compras com reserva temporária (5 minutos)
- Simulação de pagamento (modo de demonstração)
- Histórico de compras com filtros e estatísticas
- Perfil do usuário com edição de dados e troca de senha
- Notificações sobre compras e resultados

### 👑 Painel Administrativo
- Login exclusivo para administradores
- Dashboard com métricas (rifas ativas, vendas, usuários, bilhetes)
- CRUD completo de rifas (criar, editar, listar)
- Gerenciamento manual de números (bloquear/desbloquear)
- Visualização de todas as vendas com filtros
- Processamento de solicitações de reembolso
- Realização de sorteios (aleatório com hash ou integração com loteria)
- Gestão de usuários (bloquear/desbloquear)
- Configurações gerais da plataforma
- Logs de ações dos administradores

## 🛠 Tecnologias Utilizadas

### Backend
- **Flask** - Framework web
- **MySQL** - Banco de dados relacional
- **JWT** - Autenticação stateless
- **Flask-CORS** - Compartilhamento de recursos entre origens
- **python-dotenv** - Gerenciamento de variáveis de ambiente

### Frontend
- **HTML5 / CSS3** - Estrutura e estilização
- **JavaScript (ES6+)** - Interatividade e consumo da API
- **Fetch API** - Comunicação com o backend

### Ferramentas de Desenvolvimento
- **MySQL Workbench** - Gerenciamento do banco de dados
- **VS Code** - IDE recomendada
- **Git** - Controle de versão

## 📦 Pré-requisitos

Antes de começar, você precisará ter instalado em sua máquina:

- [Python 3.8+](https://www.python.org/downloads/)
- [MySQL Server 8.0+](https://dev.mysql.com/downloads/mysql/) (ou XAMPP/WAMP)
- [Git](https://git-scm.com/) (opcional, para clonar o repositório)

## 🔧 Instalação e Execução

### Backend (API)

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/API_sistema_rifa.git
   cd API_sistema_rifa
   

2. **Crie e ative um ambiente virtual**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```
   Ou manualmente:
   ```bash
   pip install Flask flask-cors mysql-connector-python python-dotenv PyJWT
   ```

4. **Configure o banco de dados**
   - Abra o MySQL Workbench ou seu cliente MySQL preferido
   - Execute o script `DB do sistema Rifa Online.sql` (localizado na raiz do projeto)
   - Isso criará o banco `rifa_online` e todas as tabelas necessárias

5. **Configure as variáveis de ambiente**
   - Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:
   ```env
   SECRET_KEY=rifa-online-secret-key-2024
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=sua_senha_aqui
   MYSQL_DATABASE=rifa_online
   ```
   - Ajuste a senha do MySQL conforme sua instalação

6. **Crie um usuário administrador (opcional, mas recomendado)**
   ```sql
   INSERT INTO usuario (nome, email, cpf, telefone, senha, tipo) 
   VALUES ('Admin', 'admin@email.com', '12345678901', '11999999999', MD5('admin123'), 'admin');
   ```

7. **Execute a aplicação**
   ```bash
   python app.py
   ```
   O servidor será iniciado em `http://localhost:5000`

### Frontend (Interface)

O frontend é composto por arquivos HTML/CSS/JS estáticos. Você pode executá-los de duas formas:

#### Opção 1: Live Server (Recomendado)
- Instale a extensão **Live Server** no VS Code
- Abra a pasta do projeto no VS Code
- Clique com o botão direito em `index.html` e escolha "Open with Live Server"
- O site será aberto em `http://127.0.0.1:5500`

#### Opção 2: Acesso direto
- Navegue até a pasta do projeto e abra o arquivo `index.html` diretamente no navegador
- **Atenção:** Algumas funcionalidades podem não funcionar corretamente devido a restrições CORS. Prefira usar o Live Server.




## 👑 Painel Administrativo

Para acessar o painel administrativo, você pode:

1. **Via API** (recomendado para integração com frontend separado):
   - Use as rotas `/admin/*` enviando o token JWT obtido no login de admin no header `Authorization: Bearer <token>`.

2. **Via interface HTML (futuro)**:
   - Acesse `http://localhost:5000/admin/login` (se implementar render_template).

Crie um administrador manualmente no banco (já mostrado acima) e utilize ferramentas como Postman, Insomnia ou o próprio frontend (se adaptado) para consumir as rotas.

## 🔐 Variáveis de Ambiente

O projeto utiliza um arquivo `.env` para configurações sensíveis. Exemplo:

```env
# Chave secreta para JWT e sessões
SECRET_KEY=rifa-online-secret-key-2024

# Credenciais do MySQL
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DATABASE=rifa_online
```

**Nunca versione o arquivo `.env`** – adicione-o ao `.gitignore`.

## 📚 Documentação Completa

A documentação detalhada do sistema (requisitos, diagramas, regras de negócio) está disponível no Google Drive:

🔗 [Documentação do Sistema de Rifa Online](https://drive.google.com/drive/folders/14VfsC38d01n_55xWev6JXOGWtb5n2jm-?usp=sharing)

Nesta pasta você encontrará:
- Documento de Visão e Especificação de Requisitos
- Modelo Conceitual e Lógico do banco de dados
- Diagrama de classes e casos de uso
- Matriz de rastreabilidade

## 📄 Licença

Este projeto está sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais informações.

---

Desenvolvido com ❤️ por Rui Ferreira, Pedro Henrique , Michele Silva e João Celino.





