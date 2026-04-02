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

CREATE TABLE bilhete(
    id_bilhete INT PRIMARY KEY AUTO_INCREMENT,
    numero INT  NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'disponivel','reservado',
    senha VARCHAR(200) NOT NULL,
    data_cadastro DATATIME DEFAULT CURRENT_TIMESTAMP,
    status TINYINT NOT NULL DEFAULT 1,
    rifa_id INT NOT NULL,
    usuario_id INT NOT NULL ,
    FOREIGN KEY (rifa_id) REFERENCES rifa(id_rifa) 

);
