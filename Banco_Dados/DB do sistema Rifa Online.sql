-- =============================================
-- SISTEMA DE RIFAS ONLINE - BANCO DE DADOS
-- =============================================

-- CRIAR BANCO DE DADOS
CREATE DATABASE IF NOT EXISTS rifa_online;
USE rifa_online;

-- =============================================
-- TABELA: USUARIO
-- =============================================
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

-- =============================================
-- TABELA: RIFA
-- =============================================
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

-- =============================================
-- TABELA: RESERVA
-- =============================================
CREATE TABLE reserva(
    id_reserva INT PRIMARY KEY AUTO_INCREMENT,
    data_reserva DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_expiracao DATETIME NOT NULL,
    status ENUM('ativa', 'expirada', 'convertida') NOT NULL DEFAULT 'ativa',
    usuario_id INT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id_usuario)
);

-- =============================================
-- TABELA: BILHETE
-- =============================================
CREATE TABLE bilhete(
    id_bilhete INT PRIMARY KEY AUTO_INCREMENT,
    numero INT NOT NULL,
    status ENUM('disponivel', 'reservado', 'pago') NOT NULL DEFAULT 'disponivel',
    reserva_id INT DEFAULT NULL,
    usuario_id INT DEFAULT NULL,
    rifa_id INT NOT NULL,
    data_compra DATETIME DEFAULT NULL,
    FOREIGN KEY (reserva_id) REFERENCES reserva(id_reserva) ON DELETE SET NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id_usuario) ON DELETE SET NULL,
    FOREIGN KEY (rifa_id) REFERENCES rifa(id_rifa) ON DELETE CASCADE,
    UNIQUE KEY unique_rifa_numero (rifa_id, numero)
);

-- =============================================
-- TABELA: PAGAMENTO
-- =============================================
CREATE TABLE pagamento(
    id_pagamento INT PRIMARY KEY AUTO_INCREMENT,
    valor DECIMAL(10,2) NOT NULL,
    metodo ENUM('pix', 'cartao_credito', 'cartao_debito', 'boleto') NOT NULL,
    status ENUM('pendente', 'aprovado', 'recusado') NOT NULL DEFAULT 'pendente',
    data_pagamento DATETIME DEFAULT CURRENT_TIMESTAMP,
    reserva_id INT NOT NULL,
    usuario_id INT NOT NULL,
    FOREIGN KEY (reserva_id) REFERENCES reserva(id_reserva) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id_usuario)
);

-- =============================================
-- TABELA: SORTEIO
-- =============================================
CREATE TABLE sorteio(
    id_sorteio INT PRIMARY KEY AUTO_INCREMENT,
    data_sorteio DATETIME NOT NULL,
    numero_sorteado INT NOT NULL,
    rifa_id INT NOT NULL,
    bilhete_vencedor_id INT NOT NULL,
    FOREIGN KEY (rifa_id) REFERENCES rifa(id_rifa) ON DELETE CASCADE,
    FOREIGN KEY (bilhete_vencedor_id) REFERENCES bilhete(id_bilhete)
);

-- =============================================
-- TABELA: NOTIFICACAO
-- =============================================
CREATE TABLE notificacao(
    id_notificacao INT PRIMARY KEY AUTO_INCREMENT,
    mensagem TEXT NOT NULL,
    data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    lida BOOLEAN DEFAULT FALSE,
    usuario_id INT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

-- =============================================
-- ÍNDICES PARA OTIMIZAÇÃO
-- =============================================

-- Índices para busca rápida
CREATE INDEX idx_bilhete_status ON bilhete(status);
CREATE INDEX idx_bilhete_rifa ON bilhete(rifa_id);
CREATE INDEX idx_reserva_usuario ON reserva(usuario_id);
CREATE INDEX idx_reserva_status ON reserva(status);
CREATE INDEX idx_pagamento_usuario ON pagamento(usuario_id);
CREATE INDEX idx_notificacao_usuario ON notificacao(usuario_id);
CREATE INDEX idx_rifa_status ON rifa(status);
CREATE INDEX idx_rifa_data_sorteio ON rifa(data_sorteio);

-- Índice para timeout (limpeza de reservas expiradas)
CREATE INDEX idx_reserva_expiracao ON reserva(data_expiracao, status);