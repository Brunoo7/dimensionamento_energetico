"""
consumo.py

Registro (PB05) e consulta (PB06) do histórico de consumo mensal
de energia elétrica (em kWh) de um imóvel.
"""

from dados import conectar

NOMES_MES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def nome_do_mes(numero_mes):
    if 1 <= numero_mes <= 12:
        return NOMES_MES[numero_mes - 1]
    return str(numero_mes)


def validar_dados_consumo(mes, ano, consumo_kwh):
    """PB13 - Validações do lançamento de consumo mensal."""
    if not isinstance(mes, int) or not (1 <= mes <= 12):
        return False, "O mês deve ser um número entre 1 e 12."
    if not isinstance(ano, int) or ano < 2000 or ano > 2100:
        return False, "Informe um ano válido (ex.: 2026)."
    if not isinstance(consumo_kwh, (int, float)) or consumo_kwh < 0:
        return False, "O consumo em kWh não pode ser negativo."
    return True, ""


def registrar_consumo(imovel_id, mes, ano, consumo_kwh):
    """Registra (ou atualiza, se já existir) o consumo de um mês/ano para o imóvel."""
    valido, mensagem = validar_dados_consumo(mes, ano, consumo_kwh)
    if not valido:
        return False, mensagem

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        """
        INSERT INTO consumos (imovel_id, mes, ano, consumo_kwh)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(imovel_id, mes, ano)
        DO UPDATE SET consumo_kwh = excluded.consumo_kwh
        """,
        (imovel_id, mes, ano, consumo_kwh),
    )
    conexao.commit()
    conexao.close()
    return True, "Consumo registrado com sucesso."


def listar_consumos_imovel(imovel_id):
    """Retorna todo o histórico de consumo (vários meses) de um imóvel, em ordem cronológica."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        """
        SELECT mes, ano, consumo_kwh FROM consumos
        WHERE imovel_id = ?
        ORDER BY ano, mes
        """,
        (imovel_id,),
    )
    resultado = cursor.fetchall()
    conexao.close()

    return [{"mes": r[0], "ano": r[1], "consumo_kwh": r[2]} for r in resultado]
