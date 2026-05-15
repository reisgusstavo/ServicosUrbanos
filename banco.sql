-- Criação do banco
CREATE DATABASE ServicosUrbanos;
GO

USE ServicosUrbanos;
GO

-- Criação da tabela de usuários
CREATE TABLE Usuarios (
    email VARCHAR(100) PRIMARY KEY,
    senha VARCHAR(100) NOT NULL,
    tipo VARCHAR(20) NOT NULL
);
GO

-- Criação da tabela de solicitações
CREATE TABLE Solicitacoes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario_email VARCHAR(100) FOREIGN KEY REFERENCES Usuarios(email),
    nome VARCHAR(100) NOT NULL,
    endereco VARCHAR(200) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    descricao TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    data_criacao DATETIME DEFAULT GETDATE(),
    imagem VARCHAR(255) NULL
);
GO

-- Criação do usuário admin padrão
INSERT INTO Usuarios (email, senha, tipo)
VALUES ('admin@admin.com', 'admin123', 'admin');
GO