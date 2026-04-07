# API do Sistema de Rifa Online

# 🎲Como rodar Rifa Online - Sistema de Rifas

## 📋 Pré-requisitos

- Python 3.8+
- MySQL (Workbench)
- VS Code (opcional)

## Como rodar o projeto

### 1. Backend (API)

```bash
# Entrar na pasta do backend
cd backend-rifa

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install Flask flask-cors mysql-connector-python python-dotenv PyJWT

# Criar banco de dados no MySQL Workbench
# Executar o script: database.sql

# Configurar .env (ajustar senha do MySQL)
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=rifa_online

# Rodar o servidor
python app.py
```
----------------------------------------------------------------------------------------------------

## Documentação do Projeto

A documentação completa da API do Sistema de Rifa Online está disponível no link abaixo:

🔗 [https://drive.google.com/drive/folders/14VfsC38d01n_55xWev6JXOGWtb5n2jm-?usp=sharing](https://drive.google.com/drive/folders/14VfsC38d01n_55xWev6JXOGWtb5n2jm-?usp=sharing)

Neste repositório, você encontrará:

* Documentação do sistema em **SIR (Sistema de Informação de Requisitos)**
* Modelos **Lógico** e **Conceitual** do banco de dados
* Estrutura e organização do projeto

Esses materiais fornecem uma visão completa do funcionamento, arquitetura e modelagem do sistema.


