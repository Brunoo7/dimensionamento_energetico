"""
calculos.py

Cálculos do sistema:
    Sprint 1
    - PB08: mês/ano de maior consumo
    - PB11: resumo energético (máximo, média e quantidade de meses analisados)
    Sprint FV
    - PB16: consumo de referência (média ou máximo)
    - PB25: energia mensal a gerar e potência FV necessária
    - PB26: quantidade de módulos e potência instalada
    - PB27: geração mensal estimada
    - PB30: dimensionamento de baterias (capacidade necessária)
    - PB31: quantidade de baterias

Todas as funções de cálculo abaixo são "puras": recebem números e devolvem
números, sem acessar banco de dados nem CSV. Isso facilita testar.
"""

import math

from consumo import nome_do_mes
import parametros


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



# ----------------------------------------------------------------------
# Sprint FV
# ----------------------------------------------------------------------

def consumo_de_referencia(historico_consumos, criterio="media"):
    """PB16 - Define o consumo de referência (C_m) em kWh/mês.

    criterio: "media" (padrão) ou "maximo".
    Retorna (True, dict) ou (False, mensagem). O dict tem:
        valor_kwh, criterio, meses_analisados e aviso (texto ou None).
    """
    if not historico_consumos:
        return False, "Não há consumo registrado para este imóvel."
    if criterio not in ("media", "maximo"):
        return False, "Critério inválido. Use 'media' ou 'maximo'."

    valores = [item["consumo_kwh"] for item in historico_consumos]
    valor = sum(valores) / len(valores) if criterio == "media" else max(valores)

    aviso = None
    if len(valores) < parametros.MESES_RECOMENDADOS:
        aviso = (
            f"Apenas {len(valores)} mês(es) de histórico; o recomendado é "
            f"{parametros.MESES_RECOMENDADOS}. O resultado pode não representar o ano todo."
        )

    return True, {
        "valor_kwh": valor,
        "criterio": criterio,
        "meses_analisados": len(valores),
        "aviso": aviso,
    }


def energia_fv_mensal(consumo_ref_kwh, fracao):
    """PB25 - E_FV = C_m × f   (kWh/mês). 'fracao' em fração: 100 % = 1,0."""
    return consumo_ref_kwh * fracao


def potencia_fv_kwp(energia_fv_kwh, hsp, eta, dias=parametros.DIAS_MES):
    """PB25 - P_FV = E_FV / (HSP × D × η)   (kWp)."""
    return energia_fv_kwh / (hsp * dias * eta)


def quantidade_modulos(potencia_fv_kwp_necessaria, potencia_modulo_wp):
    """PB26 - N = ⌈(P_FV × 1000) / P_módulo⌉.

    O round(..., 9) evita que um erro de ponto flutuante (ex.: 7.0000000001)
    some um módulo a mais sem necessidade.
    """
    return math.ceil(round(potencia_fv_kwp_necessaria * 1000 / potencia_modulo_wp, 9))


def potencia_instalada_kwp(n_modulos, potencia_modulo_wp):
    """PB26 - P_instalada = (N × P_módulo) / 1000   (kWp)."""
    return n_modulos * potencia_modulo_wp / 1000


def geracao_mensal_kwh(potencia_instalada, hsp, eta, dias=parametros.DIAS_MES):
    """PB27 - G = P_instalada × HSP × D × η   (kWh/mês)."""
    return potencia_instalada * hsp * dias * eta


def energia_diaria_kwh(consumo_ref_kwh):
    """PB30 - E_d = C_m / 30   (kWh/dia)."""
    return consumo_ref_kwh / 30


def energia_autonomia_kwh(consumo_ref_kwh, horas_autonomia):
    """PB30 - E_autonomia = E_d × (A / 24)   (kWh)."""
    return energia_diaria_kwh(consumo_ref_kwh) * (horas_autonomia / 24)


def capacidade_bateria_necessaria_kwh(e_autonomia_kwh, dod, eta_bat):
    """PB30 - C_bat = E_autonomia / (DoD × η_bat)   (kWh nominais).

    dod e eta_bat em fração (90 % = 0,90).
    """
    return e_autonomia_kwh / (dod * eta_bat)


def quantidade_baterias(c_bat_necessaria_kwh, capacidade_nominal_unitaria_kwh):
    """PB31 - N_bat = ⌈C_bat / C_nominal_unitária⌉.

    DECISÃO DE PROJETO: C_bat (acima) já inclui DoD e eficiência. Por isso
    dividimos pela capacidade NOMINAL da bateria. Dividir pela capacidade
    ÚTIL (nominal × DoD) aplicaria o DoD duas vezes e superdimensionaria.
    """
    return math.ceil(round(c_bat_necessaria_kwh / capacidade_nominal_unitaria_kwh, 9))
