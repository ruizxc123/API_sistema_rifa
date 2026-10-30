# Rifa Online — protótipo experimental

Protótipo de aplicação Flask com frontend estático. **Não está pronto para produção nem para operar campanhas.** Nesta branch, operações de venda/reserva, pagamento simulado e sorteio ficam deliberadamente bloqueadas até validação jurídica, técnica e de segurança.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

## Tecnologias

O backend usa Flask, MySQL, JWT e Flask-CORS. O frontend usa HTML, CSS e JavaScript sem framework.

## Instalação local

1. Clone o repositório e crie um ambiente virtual:

   ```bash
   git clone https://github.com/ruizxc123/API_sistema_rifa.git
   cd API_sistema_rifa
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

2. Crie uma configuração local. Copie `backend/.env.example` para `backend/.env`, gere uma chave aleatória com `python -c "import secrets; print(secrets.token_urlsafe(48))"` e configure uma conta MySQL dedicada com senha forte. Nunca use a conta administrativa do MySQL para a aplicação.

3. Crie o banco e as tabelas executando `Banco_Dados/DB do sistema Rifa Online.sql` no MySQL.

4. Inicie a API a partir da pasta `backend`:

   ```bash
   cd backend
   python app.py
   ```

   Por padrão, a API local responde em `http://127.0.0.1:5000`. Sirva os arquivos da pasta `frontend` separadamente e ajuste `CORS_ORIGINS` em `backend/.env` conforme a origem local usada.

5. Para criar o primeiro administrador, registre um usuário pela rota `/api/usuarios/registrar` com senha forte de pelo menos 12 caracteres. Em instalação local controlada, promova somente esse usuário pelo banco:

   ```sql
   UPDATE usuario SET tipo = 'admin' WHERE email = 'seu-email@exemplo.com';
   ```

   Não use senha padrão, não grave hashes MD5 e não exponha o banco à internet. Restrinja ou feche o cadastro aberto antes de disponibilizar o serviço.

**Nunca versione `backend/.env`.** Se algum segredo já esteve no GitHub, revogue e troque-o. Removê-lo num commit novo não apaga o histórico do Git.

Para executar os testes de fumaça locais, entre em `backend` e rode `python -m unittest discover -s tests`. Os testes não conectam ao banco.

## Limitações desta branch

Pagamentos simulados, reservas/venda de números e sorteios estão desativados. A aplicação ainda precisa de autorização por campanha, validação regulatória, integração real de pagamento, apuração auditável, testes automatizados, revisão de privacidade e testes de segurança antes de qualquer piloto real.

## Documentação do projeto

A documentação complementar fornecida pelo projeto está [nesta pasta do Google Drive](https://drive.google.com/drive/folders/14VfsC38d01n_55xWev6JXOGWtb5n2jm-?usp=sharing).

## Licença

O README original declarava licença MIT, mas o repositório não inclui arquivo `LICENSE`. Defina e adicione uma licença antes de redistribuir ou comercializar o software.

---

Desenvolvido por Rui Ferreira, Pedro Henrique, Michele Silva e João Celino.
