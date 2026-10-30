-- Schema inicial do Rifa Online.
-- Compatibilidade: MySQL 8.0.16+ (CHECK constraints ativos).
-- Este script cria tabelas ausentes; não migra tabelas já existentes.
-- Faça backup antes de qualquer alteração em um banco que já contenha dados.
-- Senhas são hasheadas pela aplicação (Werkzeug scrypt); não criar triggers de senha.

CREATE DATABASE IF NOT EXISTS rifa_online
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE rifa_online;
SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;
SET time_zone = '+00:00';

CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(200) NOT NULL,
    cpf VARCHAR(14) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    tipo ENUM('admin', 'normal') NOT NULL DEFAULT 'normal',
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TINYINT UNSIGNED NOT NULL DEFAULT 1,
    PRIMARY KEY (id_usuario),
    UNIQUE KEY uq_usuario_email (email),
    UNIQUE KEY uq_usuario_cpf (cpf),
    KEY idx_usuario_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS rifa (
    id_rifa INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(150) NOT NULL,
    descricao TEXT NOT NULL,
    imagem VARCHAR(500) NOT NULL DEFAULT '',
    data_inicio DATETIME NOT NULL,
    data_sorteio DATETIME NOT NULL,
    valor_bilhete DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    premio TEXT NOT NULL,
    total_numeros INT UNSIGNED NOT NULL,
    status ENUM('ativa', 'inativa', 'finalizada') NOT NULL DEFAULT 'inativa',
    PRIMARY KEY (id_rifa),
    KEY idx_rifa_status_data (status, data_sorteio),
    CONSTRAINT chk_rifa_valor CHECK (valor_bilhete >= 0),
    CONSTRAINT chk_rifa_total_numeros CHECK (total_numeros > 0),
    CONSTRAINT chk_rifa_datas CHECK (data_sorteio > data_inicio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS reserva (
    id_reserva INT UNSIGNED NOT NULL AUTO_INCREMENT,
    data_reserva DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_expiracao DATETIME NOT NULL,
    status ENUM('ativa', 'expirada', 'convertida') NOT NULL DEFAULT 'ativa',
    usuario_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (id_reserva),
    KEY idx_reserva_usuario_status_expiracao (usuario_id, status, data_expiracao),
    KEY idx_reserva_status_expiracao (status, data_expiracao),
    CONSTRAINT fk_reserva_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuario (id_usuario)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT chk_reserva_expiracao CHECK (data_expiracao > data_reserva)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS bilhete (
    id_bilhete INT UNSIGNED NOT NULL AUTO_INCREMENT,
    numero INT UNSIGNED NOT NULL,
    status ENUM('disponivel', 'reservado', 'pago') NOT NULL DEFAULT 'disponivel',
    reserva_id INT UNSIGNED DEFAULT NULL,
    usuario_id INT UNSIGNED DEFAULT NULL,
    rifa_id INT UNSIGNED NOT NULL,
    data_compra DATETIME DEFAULT NULL,
    PRIMARY KEY (id_bilhete),
    UNIQUE KEY uq_bilhete_rifa_numero (rifa_id, numero),
    UNIQUE KEY uq_bilhete_rifa_id (rifa_id, id_bilhete),
    KEY idx_bilhete_rifa_status (rifa_id, status),
    KEY idx_bilhete_usuario_status_compra (usuario_id, status, data_compra),
    KEY idx_bilhete_reserva (reserva_id),
    CONSTRAINT fk_bilhete_reserva
        FOREIGN KEY (reserva_id) REFERENCES reserva (id_reserva)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_bilhete_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuario (id_usuario)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_bilhete_rifa
        FOREIGN KEY (rifa_id) REFERENCES rifa (id_rifa)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT chk_bilhete_numero CHECK (numero > 0),
    CONSTRAINT chk_bilhete_venda CHECK (
        (status = 'disponivel' AND reserva_id IS NULL AND usuario_id IS NULL AND data_compra IS NULL)
        OR (status = 'reservado' AND reserva_id IS NOT NULL AND usuario_id IS NULL AND data_compra IS NULL)
        OR (status = 'pago' AND reserva_id IS NOT NULL AND usuario_id IS NOT NULL AND data_compra IS NOT NULL)
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS pagamento (
    id_pagamento INT UNSIGNED NOT NULL AUTO_INCREMENT,
    valor DECIMAL(10,2) NOT NULL,
    metodo ENUM('pix', 'cartao_credito', 'cartao_debito', 'boleto') NOT NULL,
    status ENUM('pendente', 'aprovado', 'recusado') NOT NULL DEFAULT 'pendente',
    data_pagamento DATETIME DEFAULT NULL,
    reserva_id INT UNSIGNED NOT NULL,
    usuario_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (id_pagamento),
    KEY idx_pagamento_reserva_status (reserva_id, status),
    KEY idx_pagamento_usuario_data (usuario_id, data_pagamento),
    CONSTRAINT fk_pagamento_reserva
        FOREIGN KEY (reserva_id) REFERENCES reserva (id_reserva)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_pagamento_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuario (id_usuario)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT chk_pagamento_valor CHECK (valor >= 0),
    CONSTRAINT chk_pagamento_data CHECK (
        (status = 'aprovado' AND data_pagamento IS NOT NULL)
        OR (status IN ('pendente', 'recusado'))
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS sorteio (
    id_sorteio INT UNSIGNED NOT NULL AUTO_INCREMENT,
    data_sorteio DATETIME NOT NULL,
    numero_sorteado INT UNSIGNED NOT NULL,
    rifa_id INT UNSIGNED NOT NULL,
    bilhete_vencedor_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (id_sorteio),
    KEY idx_sorteio_rifa_data (rifa_id, data_sorteio),
    UNIQUE KEY uq_sorteio_bilhete_vencedor (bilhete_vencedor_id),
    CONSTRAINT fk_sorteio_rifa
        FOREIGN KEY (rifa_id) REFERENCES rifa (id_rifa)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_sorteio_bilhete
        FOREIGN KEY (rifa_id, bilhete_vencedor_id)
        REFERENCES bilhete (rifa_id, id_bilhete)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT chk_sorteio_numero CHECK (numero_sorteado > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS notificacao (
    id_notificacao INT UNSIGNED NOT NULL AUTO_INCREMENT,
    mensagem TEXT NOT NULL,
    data_envio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lida BOOLEAN NOT NULL DEFAULT FALSE,
    usuario_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (id_notificacao),
    KEY idx_notificacao_usuario_lida_data (usuario_id, lida, data_envio),
    CONSTRAINT fk_notificacao_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuario (id_usuario)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
