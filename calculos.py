"""
calculos.py

Cálculos sobre o histórico de consumo de um imóvel:
    - PB08: mês/ano de maior consumo
    - PB11: resumo energético (máximo, média e quantidade de meses analisados)
"""

from consumo import nome_do_mes


def calcular_resumo(historico_consumos):
    """
    Recebe a lista de consumos de um imóvel (retornada por
    consumo.listar_consumos_imovel) e devolve um dicionário com o resumo
    energético, ou None se não houver nenhum consumo registrado.
    """
    if not historico_consumos:
        return None

    valores = [item["consumo_kwh"] for item in historico_consumos]

    consumo_maximo = max(historico_consumos, key=lambda item: item["consumo_kwh"])
    media = sum(valores) / len(valores)

    return {
        "consumo_maximo_kwh": consumo_maximo["consumo_kwh"],
        "mes_maior_consumo": nome_do_mes(consumo_maximo["mes"]),
        "ano_maior_consumo": consumo_maximo["ano"],
        "consumo_medio_kwh": media,
        "meses_analisados": len(historico_consumos),
    }


def formatar_resumo(resumo):
    """Formata o dicionário de resumo como texto pronto para exibição."""
    if resumo is None:
        return "Nenhum consumo registrado para este imóvel ainda."

    linhas = [
        "===== RESUMO ENERGÉTICO =====",
        f"Meses analisados: {resumo['meses_analisados']}",
        f"Consumo médio: {resumo['consumo_medio_kwh']:.2f} kWh/mês",
        f"Consumo máximo: {resumo['consumo_maximo_kwh']:.2f} kWh/mês "
        f"({resumo['mes_maior_consumo']}/{resumo['ano_maior_consumo']})",
    ]
    return "\n".join(linhas)
