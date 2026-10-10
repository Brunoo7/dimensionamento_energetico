"""
usuario.py

Cadastro (PB01) e login (PB02) de usuários.

Segurança da senha: a senha nunca é gravada em texto puro. Ela é armazenada com
PBKDF2-HMAC-SHA256, um "sal" aleatório por usuário e muitas iterações, no formato:

    pbkdf2_sha256$<iterações>$<sal em hex>$<hash em hex>

Contas criadas antes desta versão usam SHA-256 simples (64 caracteres hex, sem sal).
Elas continuam funcionando e são atualizadas para o formato novo no primeiro login.
"""

import hashlib
import hmac
import os
import re
import sqlite3

from dados import conectar

REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

ALGORITMO = "pbkdf2_sha256"
ITERACOES = 200_000
TAMANHO_MINIMO_SENHA = 8


def _hash_legado(senha):
    """Formato antigo (SHA-256 sem sal). Mantido só para contas antigas."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def _hash_senha(senha, sal=None, iteracoes=ITERACOES):
    """Gera o hash seguro (PBKDF2 + sal aleatório)."""
    sal = sal if sal is not None else os.urandom(16)
    derivado = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), sal, iteracoes)
    return f"{ALGORITMO}${iteracoes}${sal.hex()}${derivado.hex()}"


def _verificar_senha(senha, armazenado):
    """Confere a senha contra o hash armazenado (novo ou legado) sem vazar tempo de comparação."""
    if armazenado.startswith(ALGORITMO + "$"):
        try:
            _, iteracoes, sal_hex, hash_hex = armazenado.split("$")
            esperado = _hash_senha(senha, bytes.fromhex(sal_hex), int(iteracoes))
        except ValueError:
            return False
        return hmac.compare_digest(esperado, armazenado)
    return hmac.compare_digest(_hash_legado(senha), armazenado)


def validar_dados_usuario(nome, email, senha):
    """PB13 - Validações básicas do cadastro de usuário.
    Retorna (True, "") se estiver tudo certo, ou (False, mensagem) se houver erro.
    """
    if not nome or not nome.strip():
        return False, "O nome não pode ficar em branco."
    if not email or not REGEX_EMAIL.match(email.strip()):
        return False, "Informe um e-mail válido."
    if not senha or len(senha) < TAMANHO_MINIMO_SENHA:
        return False, f"A senha deve ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres."
    return True, ""


def cadastrar_usuario(nome, email, senha):
    """Cadastra um novo usuário. Retorna (True, id) ou (False, mensagem)."""
    valido, mensagem = validar_dados_usuario(nome, email, senha)
    if not valido:
        return False, mensagem

    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
            (nome.strip(), email.strip().lower(), _hash_senha(senha)),
        )
        conexao.commit()
        return True, cursor.lastrowid
    except sqlite3.IntegrityError:
        return False, "Já existe um usuário cadastrado com esse e-mail."
    finally:
        conexao.close()


def login(email, senha):
    """Valida e-mail e senha. Retorna (True, dados_usuario) ou (False, mensagem)."""
    if not email or not senha:
        return False, "Informe e-mail e senha."

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, nome, email, senha_hash FROM usuarios WHERE email = ?",
        (email.strip().lower(),),
    )
    resultado = cursor.fetchone()

    if resultado is None or not _verificar_senha(senha, resultado[3]):
        conexao.close()
        return False, "E-mail ou senha incorretos."

    # Atualiza contas antigas (SHA-256 sem sal) para o formato seguro.
    if not resultado[3].startswith(ALGORITMO + "$"):
        cursor.execute("UPDATE usuarios SET senha_hash = ? WHERE id = ?", (_hash_senha(senha), resultado[0]))
        conexao.commit()
    conexao.close()

    return True, {"id": resultado[0], "nome": resultado[1], "email": resultado[2]}
