"""
imovel.py

Cadastro de imóvel (PB03), sempre associado a um usuário já autenticado.
PB04 - editar e excluir imóvel.
PB18 - o imóvel agora tem cidade e UF (necessárias para buscar o HSP).
"""

from dados import conectar

TIPOS_VALIDOS = ["Casa", "Apartamento", "Sobrado", "Comercial", "Outro"]

UFS_VALIDAS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]


def validar_localizacao(cidade, uf):
    """PB18 - cidade e UF obrigatórias; UF deve ser uma das 27 válidas."""
    if not cidade or not cidade.strip():
        return False, "A cidade não pode ficar em branco."
    if not uf or uf.strip().upper() not in UFS_VALIDAS:
        return False, "Informe uma UF válida (ex.: SP)."
    return True, ""


def validar_dados_imovel(nome, tipo, cidade, uf):
    """PB13 - Validação básica do cadastro de imóvel."""
    if not nome or not nome.strip():
        return False, "O nome/apelido do imóvel não pode ficar em branco."
    if not tipo or not tipo.strip():
        return False, "O tipo do imóvel não pode ficar em branco."
    return validar_localizacao(cidade, uf)


def cadastrar_imovel(usuario_id, nome, tipo, cidade, uf, endereco=""):
    """Cadastra um imóvel vinculado ao usuário logado."""
    valido, mensagem = validar_dados_imovel(nome, tipo, cidade, uf)
    if not valido:
        return False, mensagem

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO imoveis (usuario_id, nome, endereco, tipo, cidade, uf) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (usuario_id, nome.strip(), (endereco or "").strip(), tipo.strip(),
         cidade.strip(), uf.strip().upper()),
    )
    conexao.commit()
    novo_id = cursor.lastrowid
    conexao.close()
    return True, novo_id


def _linha_para_dict(r):
    return {
        "id": r[0], "usuario_id": r[1], "nome": r[2], "endereco": r[3],
        "tipo": r[4], "cidade": r[5], "uf": r[6],
    }


def listar_imoveis_usuario(usuario_id):
    """Retorna todos os imóveis cadastrados pelo usuário logado."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, usuario_id, nome, endereco, tipo, cidade, uf "
        "FROM imoveis WHERE usuario_id = ? ORDER BY nome",
        (usuario_id,),
    )
    resultado = cursor.fetchall()
    conexao.close()
    return [_linha_para_dict(r) for r in resultado]


def buscar_imovel_por_id(imovel_id):
    """Retorna os dados do imóvel (incluindo o usuario_id dono) ou None se não existir."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, usuario_id, nome, endereco, tipo, cidade, uf FROM imoveis WHERE id = ?",
        (imovel_id,),
    )
    resultado = cursor.fetchone()
    conexao.close()

    if resultado is None:
        return None
    return _linha_para_dict(resultado)


def imovel_pertence_ao_usuario(imovel_id, usuario_id):
    """PB15 - Confirma se o imóvel pertence ao usuário informado.
    Usado como checagem de segurança antes de ler/gravar consumo de um imóvel.
    """
    imovel_encontrado = buscar_imovel_por_id(imovel_id)
    return imovel_encontrado is not None and imovel_encontrado["usuario_id"] == usuario_id


def atualizar_localizacao(usuario_id, imovel_id, cidade, uf):
    """PB18 - Define cidade e UF de um imóvel (ex.: imóveis cadastrados antes da Sprint FV)."""
    if not imovel_pertence_ao_usuario(imovel_id, usuario_id):
        return False, "Imóvel não encontrado ou não pertence a este usuário."

    valido, mensagem = validar_localizacao(cidade, uf)
    if not valido:
        return False, mensagem

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "UPDATE imoveis SET cidade = ?, uf = ? WHERE id = ? AND usuario_id = ?",
        (cidade.strip(), uf.strip().upper(), imovel_id, usuario_id),
    )
    conexao.commit()
    conexao.close()
    return True, "Localização atualizada."



def editar_imovel(usuario_id, imovel_id, nome, tipo, cidade, uf, endereco=""):
    """PB04 - Altera os dados de um imóvel (somente se for do usuário - PB15)."""
    if not imovel_pertence_ao_usuario(imovel_id, usuario_id):
        return False, "Imóvel não encontrado ou não pertence a este usuário."

    valido, mensagem = validar_dados_imovel(nome, tipo, cidade, uf)
    if not valido:
        return False, mensagem

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "UPDATE imoveis SET nome = ?, tipo = ?, cidade = ?, uf = ?, endereco = ? "
        "WHERE id = ? AND usuario_id = ?",
        (nome.strip(), tipo.strip(), cidade.strip(), uf.strip().upper(),
         (endereco or "").strip(), imovel_id, usuario_id),
    )
    conexao.commit()
    conexao.close()
    return True, "Imóvel atualizado."


def excluir_imovel(usuario_id, imovel_id):
    """PB04 - Exclui o imóvel e tudo que depende dele (consumos e propostas).
    A confirmação com o usuário é feita na tela (main.py) antes de chamar esta função.
    """
    if not imovel_pertence_ao_usuario(imovel_id, usuario_id):
        return False, "Imóvel não encontrado ou não pertence a este usuário."

    conexao = conectar()
    try:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM propostas WHERE imovel_id = ?", (imovel_id,))
        cursor.execute("DELETE FROM consumos WHERE imovel_id = ?", (imovel_id,))
        cursor.execute("DELETE FROM imoveis WHERE id = ? AND usuario_id = ?", (imovel_id, usuario_id))
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()
    return True, "Imóvel excluído."
