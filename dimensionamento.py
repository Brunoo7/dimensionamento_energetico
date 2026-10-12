"""
dimensionamento.py

Pipeline completo do pré-dimensionamento (junta os módulos anteriores):

    consumo de referência -> P_FV -> módulo -> inversor (strings) -> bateria -> orçamento

Funciona só com números e listas (sem banco e sem input), então serve tanto para
o menu (main.py) quanto para gerar cenários (cenarios.py) e para os testes.
"""

import calculos
import orcamento
import parametros
import selecao


def dimensionar(consumo_ref_kwh, hsp, fracao, eta, modulos, inversores,
                baterias=None, outros_custos=None, com_bateria=False, autonomia_h=None):
    """Retorna (True, resultado) ou (False, lista_de_mensagens)."""
    # --- validações de entrada (PB13 / PB20) ---
    erros = []
    if not isinstance(consumo_ref_kwh, (int, float)) or consumo_ref_kwh <= 0:
        erros.append("O consumo de referência deve ser maior que zero.")
    for validar, valor in ((parametros.validar_hsp, hsp), (parametros.validar_fracao, fracao),
                           (parametros.validar_eta, eta)):
        ok, mensagem = validar(valor)
        if not ok:
            erros.append(mensagem)
    if com_bateria:
        ok, mensagem = parametros.validar_autonomia(autonomia_h)
        if not ok:
            erros.append(mensagem)
    if erros:
        return False, erros

    if not modulos:
        return False, ["Não há módulos válidos em data/modulos.csv."]
    if not inversores:
        return False, ["Não há inversores válidos em data/inversores.csv."]
    if com_bateria and not baterias:
        return False, ["Não há baterias válidas em data/baterias.csv."]

    # --- geração necessária (PB25) ---
    energia_fv = calculos.energia_fv_mensal(consumo_ref_kwh, fracao)
    p_fv = calculos.potencia_fv_kwp(energia_fv, hsp, eta)

    # --- módulo + inversor (PB26, PB28, PB29) ---
    # Primeiro tenta todos os módulos (do mais barato em R$/Wp ao mais caro) com a quantidade
    # necessária. Se nenhum tiver inversor compatível (por exemplo, a tensão das strings fica
    # abaixo da faixa MPPT), acrescenta módulos, um a um, até MODULOS_EXTRAS_MAX.
    modulos_ordenados = sorted(modulos, key=lambda m: m["preco_brl"] / m["potencia_wp"])
    escolhido = None
    motivos_inversor = []
    for extras in range(0, parametros.MODULOS_EXTRAS_MAX + 1):
        for modulo in modulos_ordenados:
            n = calculos.quantidade_modulos(p_fv, modulo["potencia_wp"]) + extras
            p_inst = calculos.potencia_instalada_kwp(n, modulo["potencia_wp"])
            inversor, strings, rejeicoes = selecao.selecionar_inversor(
                modulo, n, inversores, exigir_bateria=com_bateria)
            if inversor is not None:
                escolhido = (modulo, n, p_inst, inversor, strings, extras)
                break
            if extras == 0 and not motivos_inversor:   # guarda o motivo do módulo mais barato
                for id_inv, motivos in rejeicoes.items():
                    motivos_inversor.append(f"{id_inv}: " + "; ".join(motivos))
        if escolhido is not None:
            break

    if escolhido is None:
        quem = "com bateria (inversor híbrido) " if com_bateria else ""
        return False, ([f"Nenhum inversor {quem}compatível com os módulos do dataset. Motivos (módulo mais barato):"]
                       + motivos_inversor)

    modulo, n_modulos, p_instalada, inversor, strings, modulos_extras = escolhido
    geracao = calculos.geracao_mensal_kwh(p_instalada, hsp, eta)

    # --- baterias (PB30, PB31) ---
    armazenamento = None
    if com_bateria:
        e_autonomia = calculos.energia_autonomia_kwh(consumo_ref_kwh, autonomia_h)
        armazenamento, motivos = selecao.selecionar_bateria(e_autonomia, baterias, inversor)
        if armazenamento is None:
            return False, ["Nenhuma bateria compatível com o inversor escolhido:"] + motivos
        armazenamento["energia_autonomia_kwh"] = round(e_autonomia, 3)
        armazenamento["autonomia_h"] = autonomia_h

    # --- orçamento (PB32, PB33) ---
    orc = orcamento.calcular_orcamento(modulo, n_modulos, inversor, p_instalada, armazenamento, outros_custos)

    return True, {
        "consumo_referencia_kwh": consumo_ref_kwh,
        "fracao": fracao,
        "eta": eta,
        "hsp": hsp,
        "dias": parametros.DIAS_MES,
        "energia_fv_kwh": energia_fv,
        "potencia_fv_kwp": p_fv,
        "modulo": modulo,
        "n_modulos": n_modulos,
        "modulos_extras": modulos_extras,
        "potencia_instalada_kwp": p_instalada,
        "strings": strings,
        "inversor": inversor,
        "armazenamento": armazenamento,
        "geracao_mensal_kwh": geracao,
        "cobertura_pct": geracao / consumo_ref_kwh * 100,
        "orcamento": orc,
    }
