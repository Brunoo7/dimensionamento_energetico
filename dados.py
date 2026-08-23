"""
dados.py

Responsável por toda a conexão com o banco de dados SQLite e pela
criação das tabelas usadas pelo sistema.

Tabelas:
    usuarios  -> PB01 (cadastro de usuário)
    imoveis   -> PB03 (cadastro de imóvel), associado a um usuário
    consumos  -> PB05 / PB06 (histórico de consumo mensal), associado a um imóvel
"""

import sqlite3

NOME_BANCO = "dimensionamento.db"


def conectar():
    """Abre e retorna uma conexão com o banco de dados SQLite."""
    conexao = sqlite3.connect(NOME_BANCO)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_tabelas():
    """Cria as tabelas do sistema caso ainda não existam."""
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS imoveis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            endereco TEXT,
            tipo TEXT NOT NULL DEFAULT 'Não informado',
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consumos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imovel_id INTEGER NOT NULL,
            mes INTEGER NOT NULL,
            ano INTEGER NOT NULL,
            consumo_kwh REAL NOT NULL,
            FOREIGN KEY (imovel_id) REFERENCES imoveis (id),
            UNIQUE (imovel_id, mes, ano)
        )
    """)

    conexao.commit()
    conexao.close()