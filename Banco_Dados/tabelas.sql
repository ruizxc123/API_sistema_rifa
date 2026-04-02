CREATE DATABASE rifa_online;
USE rifa_online;

-- USUARIO
CREATE TABLE usuario(
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    telefone VARCHAR(20) NOT NULL,
    senha VARCHAR(200) NOT NULL,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TINYINT NOT NULL DEFAULT 1
);

-- RIFA
CREATE TABLE rifa(
    id_rifa INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(150) NOT NULL,
    descricao TEXT NOT NULL,
    imagem VARCHAR(500) NOT NULL,
    data_inicio DATETIME NOT NULL,
    data_sorteio DATETIME NOT NULL,
    valor_bilhete DECIMAL(10,2) NOT NULL,
    premio TEXT NOT NULL,
    total_numeros INT NOT NULL,
    status ENUM('ativa', 'inativa', 'finalizada') NOT NULL DEFAULT 'ativa'
);

-- BILHETE
CREATE TABLE bilhete(
    id_bilhete INT PRIMARY KEY AUTO_INCREMENT,
    numero INT NOT NULL,
    status ENUM('disponivel', 'reservado', 'pago', 'cancelado') NOT NULL DEFAULT 'disponivel',
    data_compra DATETIME DEFAULT NULL,
    rifa_id INT NOT NULL,
    usuario_id INT DEFAULT NULL,
    FOREIGN KEY (rifa_id) REFERENCES rifa(id_rifa),
    FOREIGN KEY (usuario_id) REFERENCES usuario(id_usuario),
    UNIQUE KEY unique_rifa_numero (rifa_id, numero)
);

-- PAGAMENTO
CREATE TABLE pagamento(
    id_pagamento INT PRIMARY KEY AUTO_INCREMENT,
    valor DECIMAL(10,2) NOT NULL,
    tipo_pagamento VARCHAR(20) NOT NULL,
    status_pagamento ENUM('pendente', 'pago', 'reembolsado', 'falhou') NOT NULL DEFAULT 'pendente',
    data_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_confirmacao DATETIME DEFAULT NULL,
    usuario_id INT NOT NULL,
    bilhete_id INT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id_usuario),
    FOREIGN KEY (bilhete_id) REFERENCES bilhete(id_bilhete)
);

-- REGISTRO_PAGAMENTO (logs do gateway)
CREATE TABLE registro_pagamento(
    id_registro_pagamento INT PRIMARY KEY AUTO_INCREMENT,
    status_gateway VARCHAR(50),
    resposta_gateway TEXT,
    data_transacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    pagamento_id INT NOT NULL,
    FOREIGN KEY (pagamento_id) REFERENCES pagamento(id_pagamento)
);

-- REEMBOLSO
CREATE TABLE reembolso(
    id_reembolso INT PRIMARY KEY AUTO_INCREMENT,
    motivo TEXT NOT NULL,
    status ENUM('solicitado', 'aprovado', 'negado', 'processado') NOT NULL DEFAULT 'solicitado',
    data_solicitacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_processamento DATETIME DEFAULT NULL,
    pagamento_id INT NOT NULL,
    FOREIGN KEY (pagamento_id) REFERENCES pagamento(id_pagamento)
);

-- SORTEIO
CREATE TABLE sorteio(
    id_sorteio INT PRIMARY KEY AUTO_INCREMENT,
    data_sorteio DATETIME NOT NULL,
    metodo_sorteio VARCHAR(30) NOT NULL,
    resultado VARCHAR(100),
    numero_sorteado INT,
    rifa_id INT NOT NULL,
    bilhete_vencedor_id INT DEFAULT NULL,
    FOREIGN KEY (rifa_id) REFERENCES rifa(id_rifa),
    FOREIGN KEY (bilhete_vencedor_id) REFERENCES bilhete(id_bilhete)
);

-- NOTIFICACAO
CREATE TABLE notificacao(
    id_notificacao INT PRIMARY KEY AUTO_INCREMENT,
    tipo ENUM('email', 'sms', 'push') NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    mensagem TEXT NOT NULL,
    data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pendente', 'enviado', 'falhou') NOT NULL DEFAULT 'pendente',
    usuario_id INT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id_usuario)
);
