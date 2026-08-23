"""
imovel.py

Cadastro de imóvel (PB03), sempre associado a um usuário já autenticado.
"""

from dados import conectar


def validar_dados_imovel(nome):
    """PB13 - Validação básica do cadastro de imóvel."""
    if not nome or not nome.strip():
        return False, "O nome/apelido do imóvel não pode ficar em branco."
    return True, ""


def cadastrar_imovel(usuario_id, nome, endereco=""):
    """Cadastra um imóvel vinculado ao usuário logado."""
    valido, mensagem = validar_dados_imovel(nome)
    if not valido:
        return False, mensagem

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO imoveis (usuario_id, nome,