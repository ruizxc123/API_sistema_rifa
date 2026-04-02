CREATE DATABASE rifa_online;

USE rifa_online;
GO

-- CRIANDO AS TABELAS DO SISTEMA --

BEGIN TRANSACTION

CREATE TABLE usuario(
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    telefone VARCHAR(20) NOT NULL,
    senha VARCHAR(200) NOT NULL,
    data_cadastro DATATIME DEFAULT CURRENT_TIMESTAMP,
    status TINYINT NOT NULL DEFAULT 1,

);

ROLLBACK TRANSACTION
COMMIT;


--------------------------
BEGIN TRANSACTION

CREATE TABLE rifa(
    id_rifa INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(150) NOT NULL,
    descricao TEXT(500) NOT NULL,
    imagem VARCHAR(500) NOT NULL,-- URL da imagem de divigação
    data_inicio DATATIME NOT NULL,
    data_sorteio DATATIME NOT NULL,
    valor_bilhete DECIMAL 10,2 NOT NULL,
    premio TEXT(500) NOT NULL,
    total_numeros INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ativa','inativa',
);

ROLLBACK TRANSACTION
COMMIT;

-----------------------------
BEGIN TRANSACTION

CREATE TABLE bilhete(
    id_bilhete INT PRIMARY KEY AUTO_INCREMENT,
    numero INT  NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'disponivel','reservado','paga','cancelado',
    senha VARCHAR(200) NOT NULL,
    data_cadastro DATATIME DEFAULT CURRENT_TIMESTAMP,
    status TINYINT NOT NULL DEFAULT 1,
    rifa_id INT NOT NULL,
    usuario_id INT NOT NULL ,
    FOREIGN KEY (rifa_id) REFERENCES rifa(id_rifa),
    FOREIGN KEY (usuario_id) REFERENCES usuario(id_usuario)
);

ROLLBACK TRANSACTION
COMMIT;

-------------------------------
BEGIN TRANSACTION

CREATE TABLE pagamento(
    id_pagamento INT PRIMARY KEY AUTO_INCREMENT,
    valor DECIMAL 10,2  NOT NULL ,-- VALOR TOTAL DO PAGAMENTO
    tipo_pagamento VARCHAR(20) NOT NULL,
    status_pagamento VARCHAR(20) NOT NULL DEFAULT 'pendente','pago','reembolsado',
    data DATATIME DEFAULT CURRENT_TIMESTAMP,
    data_confimação DATATIME CURRENT_TIMESTAMP,
    usuario_id INT,
    rifa_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id_usuario),
    FOREIGN key (rifa_id) REFERENCES rifa(id_rifa)
);

ROLLBACK TRANSACTION
COMMIT;

--------------------------------
BEGIN TRANSACTION

CREATE TABLE registro_pagamento(
    id_registro_pagamento INT PRIMARY KEY AUTO_INCREMENT,
    status_gateway VARCHAR(50), -- Esse atributo está desativado 
    resposta_gateway TEXT(500), -- Esse atributo está desativado 
    data DATATIME DEFAULT CURRENT_TIMESTAMP,
    pagamento_id INT,
    FOREIGN KEY (pagamento_id) REFERENCES pagamento(id_pagamento)
);

ROLLBACK TRANSACTION
COMMIT;

-------------------------------
BEGIN TRANSACTION

CREATE TABLE reembolso(
    id_reembolso INT PRIMARY KEY AUTO_INCREMENT,
    motivo TEXT(500),
    status VARCHAR(20) NOT NULL DEFAULT 'solicitado','aprovado','negado',
    data DATATIME DEFAULT CURRENT_TIMESTAMP,
    rifa_id INT,
    usuario_id INT,
    bilhete_id INT,
    FOREIGN KEY (rifa_id) REFERENCES rifa(id_rifa),
    FOREIGN KEY (usuario_id) REFERENCES usuario(id_usuario),
    FOREIGN KEY (bilhete_id) REFERENCES bilhete(id_bilhete)
);

ROLLBACK TRANSACTION
COMMIT;

---------------------------------
BEGIN TRANSACTION

CREATE TABLE sorteio(
    id_sorteio INT PRIMARY KEY AUTO_INCREMENT,
    data_sorteio DATATIME NOT NULL,
    metodo_sorteio VARCHAR 30 NOT NULL,
    resultado VARCHAR(100),
    vencedor_id INT,
    rifa_id INT,
    bilhete_id INT,
    FOREIGN KEY (vencedor_id) REFERENCES usuario(id_usuario),
    FOREIGN KEY (rifa_id) REFERENCES rifa(rifa_id),
    FOREIGN KEY (bilhete_id) REFERENCES bilhete(id_bilhete)
);

ROLLBACK TRANSACTION
COMMIT;

--------------------------------

BEGIN TRANSACTION

CREATE TABLE resultado_sorteio(
    Id_resultado_sorteio INT PRIMARY KEY AUTO_INCREMENT,
    detalhes TEXT(500) NOT NULL,
    comprovante_hash VARCHAR(300), -- Esse atributo está desativado
    sorteio_id INT,
    FOREIGN KEY (sorteio_id) REFERENCES sorteio(id_sorteio)
);

ROLLBACK TRANSACTION
COMMIT;

-------------------------------

BEGIN TRANSACTION

CREATE TABLE notificacao(
    id_notificacao INT PRIMARY KEY AUTO_INCREMENT,
    tipo VARCHAR(20) NOT NULL, -- email, sms e telefone
    titulo VARCHAR(200) NOT NULL,
    mensagem TEXT(500) NOT NULL,
    data_envio DATATIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'enviado','pendente',
    usuario_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id_usuario)

);

ROLLBACK TRANSACTION
COMMIT;

-------------------------------

BEGIN TRANSACTION

CREATE TABLE painel_admin(
    id_painel_admin INT PRIMARY KEY AUTO_INCREMENT,
    papel VARCHAR(100) NOT NULL,
    data_atribuicao DATATIME DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT,
    rifa_id INT,
    sorteio_id INT,
    pagamento_id INT,
    resultado_sorteio_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id_usuario),
    FOREIGN KEY (rifa_id) REFERENCES rifa(id_rifa),
    FOREIGN KEY (sorteio_id) REFERENCES sorteio(id_sorteio),
    FOREIGN KEY (pagamento_id) REFERENCES pagamento(id_pagamento),
    FOREIGN KEY (resultado_sorteio_id) REFERENCES resultado_sorteio(Id_resultado_sorteio)
);

ROLLBACK TRANSACTION
COMMIT;