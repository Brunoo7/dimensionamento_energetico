"""
usuario.py

Cadastro (PB01) e login (PB02) de usuários.
A senha nunca é gravada em texto puro: é armazenada como hash SHA-256.
"""

import hashlib
import re
from dados import conectar

REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def validar_dados_usuario(nome, email, senha):
    """PB13 - Validações básicas do cadastro de usuário.
    Retorna (True, "") se estiver tudo certo, ou (False, mensagem) se houver erro.
    """
    if not nome or not nome.strip():
        return False, "O nome não pode ficar em branco."
    if not email or not REGEX_EMAIL.match(email.strip()):
        return False, "Informe um e-mail válido."
    if not senha or len(senha) < 4:
        return False, "A senha deve ter pelo menos 4 caracteres."
    return True, ""


def cadastrar_usuario(nome, email, senha):
    """Cadastra um novo usuário. Retorna (True, id_ou_mensagem)."""
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
        novo_id = cursor.lastrowid
        return True, novo_id
    except Exception:
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
        "SELECT id, nome, email FROM usuarios WHERE email = ? AND senha_hash = ?",
        (email.strip().lower(), _hash_senha(senha)),
    )
    resultado = cursor.fetchone()
    conexao.close()

    if resultado is None:
        return False, "E-mail ou senha incorretos."

    usuario = {"id": resultado[0], "nome": resultado[1], "email": resultado[2]}
    return True, usuario
