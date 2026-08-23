"""
imovel.py

Cadastro de imóvel (PB03), sempre associado a um usuário já autenticado.
"""

from dados import conectar

TIPOS_VALIDOS = ["Casa", "Apartamento", "Sobrado", "Comercial", "Outro"]


def validar_dados_imovel(nome, tipo):
    """PB13 - Validação básica do cadastro de imóvel."""
    if not nome or not nome.strip():
        return False, "O nome/apelido do imóvel não pode ficar em branco."
    if not tipo or not tipo.strip():
        return False, "O tipo do imóvel não pode ficar em branco."
    return True, ""


def cadastrar_imovel(usuario_id, nome, tipo, endereco=""):
    """Cadastra um imóvel vinculado ao usuário logado."""
    valido, mensagem = validar_dados_imovel(nome, tipo)
    if not valido:
        return False, mensagem

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO imoveis (usuario_id, nome, endereco, tipo) VALUES (?, ?, ?, ?)",
        (usuario_id, nome.strip(), (endereco or "").strip(), tipo.strip()),
    )
    conexao.commit()
    novo_id = cursor.lastrowid
    conexao.close()
    return True, novo_id


def listar_imoveis_usuario(usuario_id):
    """Retorna todos os imóveis cadastrados pelo usuário logado."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, nome, endereco, tipo FROM imoveis WHERE usuario_id = ? ORDER BY nome",
        (usuario_id,),
    )
    resultado = cursor.fetchall()
    conexao.close()

    return [{"id": r[0], "nome": r[1], "endereco": r[2], "tipo": r[3]} for r in resultado]


def buscar_imovel_por_id(imovel_id):
    """Retorna os dados do imóvel (incluindo o usuario_id dono) ou None se não existir."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, usuario_id, nome, endereco, tipo FROM imoveis WHERE id = ?",
        (imovel_id,),
    )
    resultado = cursor.fetchone()
    conexao.close()

    if resultado is None:
        return None
    return {
        "id": resultado[0],
        "usuario_id": resultado[1],
        "nome": resultado[2],
        "endereco": resultado[3],
        "tipo": resultado[4],
    }


def imovel_pertence_ao_usuario(imovel_id, usuario_id):
    """PB15 - Confirma se o imóvel pertence ao usuário informado.
    Usado como checagem de segurança antes de ler/gravar consumo de um imóvel.
    """
    imovel_encontrado = buscar_imovel_por_id(imovel_id)
    return imovel_encontrado is not None and imovel_encontrado["usuario_id"] == usuario_id