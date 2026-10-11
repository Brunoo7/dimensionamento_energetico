"""
selecao.py

Seleção e validação técnica dos equipamentos (PB28, PB29, PB31).

    configurar_strings   - PB29: valida a ligação módulos-inversor (tensão e corrente)
    selecionar_inversor  - PB28: filtra os inversores válidos e escolhe o mais barato
    selecionar_bateria   - PB31: escolhe a bateria/quantidade de menor custo

Pré-dimensionamento: não substitui projeto elétrico (ver README).
"""

import math

import calculos
import parametros


def _divisores_decrescentes(n):
    return [d for d in range(n, 0, -1) if n % d == 0]


def configurar_strings(modulo, inversor, n_modulos):
    """PB29 - Procura uma ligação em strings que respeite o inversor.

    Testa dividir os N módulos em strings iguais (começando pelas mais longas).
    Regras verificadas para cada divisão:
        Voc_frio  = n_série × Voc × FATOR_VOC_FRIO  ≤ tensão máxima de entrada
        Vmp_quente = n_série × Vmp × FATOR_VMP_QUENTE ≥ início da faixa MPPT
        Vmp (STC)  = n_série × Vmp                   ≤ fim da faixa MPPT
        Isc × strings_em_paralelo_por_MPPT ≤ corrente máxima de curto-circuito (por MPPT)
        Imp × strings_em_paralelo_por_MPPT ≤ corrente máxima de entrada (por MPPT)
    (strings distribuídas igualmente entre os MPPTs).

    Como cada limite é tratado:
      - Se o dataset informa a corrente máxima de curto-circuito do inversor, ela é a regra de
        SEGURANÇA (reprova se a Isc passar). Já a Imp acima da corrente máxima de entrada não
        danifica o inversor: ele limita a corrente e há só perda de geração. Nesse caso a
        combinação é aceita e a configuração traz um aviso.
      - Se o dataset NÃO informa o limite de curto-circuito, o sistema é conservador e reprova
        quando a Imp passar da corrente máxima de entrada.

    Retorna (True, configuração) ou (False, lista_de_motivos).
    """
    motivos = []
    for n_serie in _divisores_decrescentes(n_modulos):
        n_strings = n_modulos // n_serie
        voc_frio = n_serie * modulo["voc_v"] * parametros.FATOR_VOC_FRIO
        vmp_quente = n_serie * modulo["vmp_v"] * parametros.FATOR_VMP_QUENTE
        vmp_stc = n_serie * modulo["vmp_v"]
        paralelos = math.ceil(n_strings / inversor["numero_mppt"])
        corrente = modulo["imp_a"] * paralelos
        corrente_curto = modulo["isc_a"] * paralelos
        limite_curto = inversor.get("corrente_max_curto_circuito_a")

        problemas, avisos = [], []
        if voc_frio > inversor["tensao_max_entrada_v"]:
            problemas.append(
                f"{n_serie} em série: Voc a frio {voc_frio:.0f} V acima do máximo "
                f"do inversor ({inversor['tensao_max_entrada_v']:.0f} V)")
        if vmp_quente < inversor["faixa_mppt_min_v"]:
            problemas.append(
                f"{n_serie} em série: Vmp a quente {vmp_quente:.0f} V abaixo do início "
                f"da faixa MPPT ({inversor['faixa_mppt_min_v']:.0f} V)")
        if vmp_stc > inversor["faixa_mppt_max_v"]:
            problemas.append(
                f"{n_serie} em série: Vmp {vmp_stc:.0f} V acima do fim "
                f"da faixa MPPT ({inversor['faixa_mppt_max_v']:.0f} V)")
        if corrente > inversor["corrente_max_entrada_a"]:
            texto = (f"{n_serie} em série: corrente {corrente:.1f} A acima do máximo "
                     f"do inversor ({inversor['corrente_max_entrada_a']:.1f} A)")
            if limite_curto is None:
                problemas.append(texto)
            else:
                avisos.append(
                    f"Corrente de operação dos módulos ({corrente:.1f} A por MPPT) acima da corrente máxima de "
                    f"entrada do inversor ({inversor['corrente_max_entrada_a']:.1f} A): o inversor limita a "
                    f"corrente e pode haver pequena perda de geração.")
        if limite_curto is not None and corrente_curto > limite_curto:
            problemas.append(
                f"{n_serie} em série: corrente de curto-circuito {corrente_curto:.1f} A acima do "
                f"limite do inversor ({limite_curto:.1f} A)")

        if not problemas:
            return True, {
                "modulos_em_serie": n_serie,
                "strings": n_strings,
                "strings_em_paralelo_por_mppt": paralelos,
                "voc_frio_v": round(voc_frio, 1),
                "vmp_quente_v": round(vmp_quente, 1),
                "corrente_por_mppt_a": round(corrente, 2),
                "avisos": avisos,
            }
        motivos += problemas
    return False, motivos


def selecionar_inversor(modulo, n_modulos, inversores, exigir_bateria=False):
    """PB28 - Escolhe o inversor tecnicamente válido de menor preço.

    Filtros: (1) compatível com bateria, se pedido; (2) potência FV instalada
    ≤ potencia_max_fv_w; (3) razão FV/CA dentro da faixa configurada;
    (4) ligação em strings válida (PB29).

    Retorna (inversor, configuração_strings, rejeicoes). Se nenhum servir,
    inversor e configuração são None e 'rejeicoes' (id -> motivos) explica por quê.
    """
    p_inst_w = n_modulos * modulo["potencia_wp"]
    validos, rejeicoes = [], {}

    for inv in inversores:
        motivos = []
        if exigir_bateria and inv["compativel_bateria"] != "sim":
            motivos.append("não é compatível com bateria")
        if p_inst_w > inv["potencia_max_fv_w"]:
            motivos.append(
                f"potência FV {p_inst_w:.0f} W acima do máximo do inversor ({inv['potencia_max_fv_w']:.0f} W)")
        razao = p_inst_w / inv["potencia_nominal_w"]
        if not (parametros.RAZAO_FV_CA_MIN <= razao <= parametros.RAZAO_FV_CA_MAX):
            motivos.append(
                f"razão FV/CA {razao:.2f} fora da faixa "
                f"{parametros.RAZAO_FV_CA_MIN}–{parametros.RAZAO_FV_CA_MAX}")
        if not motivos:
            ok, resultado = configurar_strings(modulo, inv, n_modulos)
            if ok:
                validos.append((inv, resultado))
            else:
                motivos += resultado
        if motivos:
            rejeicoes[inv["id"]] = motivos

    if not validos:
        return None, None, rejeicoes
    inversor, configuracao = min(validos, key=lambda item: item[0]["preco_brl"])
    return inversor, configuracao, rejeicoes


def selecionar_bateria(e_autonomia_kwh, baterias, inversor, eta_bat=parametros.ETA_BATERIA_PADRAO):
    """PB31 - Escolhe a bateria (e a quantidade) de menor custo total.

    Para cada bateria do dataset:
      - se o inversor informa a faixa de tensão de bateria, a tensão nominal
        da bateria precisa estar dentro dela (senão 'tensao_verificada' = False);
      - C_bat usa o DoD DAQUELA bateria: C_bat = E_autonomia / (DoD × η_bat);
      - N_bat = ⌈C_bat / capacidade nominal unitária⌉.

    Retorna (escolha, motivos). 'escolha' é None se nenhuma bateria servir.
    """
    t_min, t_max = inversor.get("tensao_bateria_min_v"), inversor.get("tensao_bateria_max_v")
    tensao_conhecida = t_min is not None and t_max is not None
    candidatas, motivos = [], []

    for bat in baterias:
        if tensao_conhecida and not (t_min <= bat["tensao_nominal_v"] <= t_max):
            motivos.append(
                f"{bat['id']}: tensão {bat['tensao_nominal_v']:.1f} V fora da faixa do inversor "
                f"({t_min:.0f}–{t_max:.0f} V)")
            continue
        dod = bat["dod_pct"] / 100
        c_bat = calculos.capacidade_bateria_necessaria_kwh(e_autonomia_kwh, dod, eta_bat)
        n = calculos.quantidade_baterias(c_bat, bat["capacidade_kwh"])
        candidatas.append({
            "bateria": bat,
            "quantidade": n,
            "capacidade_necessaria_kwh": round(c_bat, 3),
            "capacidade_instalada_kwh": round(n * bat["capacidade_kwh"], 3),
            "capacidade_util_kwh": round(n * bat["capacidade_kwh"] * dod, 3),
            "custo": round(n * bat["preco_brl"], 2),
            "eta_bateria": eta_bat,
            "tensao_verificada": tensao_conhecida,
        })

    if not candidatas:
        return None, motivos or ["nenhuma bateria no dataset"]
    escolha = min(candidatas, key=lambda c: (c["custo"], c["quantidade"]))
    return escolha, motivos
