"""
proposta.py

Proposta preliminar ao cliente (PB34) e propostas salvas (PB35).

A proposta é salva como JSON no SQLite com os valores usados naquele momento
(ids, preços, parâmetros). Assim, reabrir a proposta mostra os mesmos números
mesmo que os CSVs mudem depois.
"""

import json

from dados import conectar
import imovel

AVISO = ("Pré-dimensionamento acadêmico e estimativa de custos. Não substitui projeto elétrico "
         "executivo, responsabilidade técnica ou análise de profissional habilitado "
         "(área disponível, orientação, sombreamento, proteções, aterramento, normas e "
         "requisitos da distribuidora precisam ser verificados).")


def formatar_brl(valor):
    """1234.5 -> 'R$ 1.234,50'."""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def montar_proposta(imovel_dados, criterio, meses_analisados, hsp_fonte, resultado):
    """Junta o contexto (imóvel, critério do consumo, fonte do HSP) ao resultado do cálculo."""
    return {
        "imovel": {k: imovel_dados.get(k) for k in ("id", "nome", "cidade", "uf")},
        "criterio_consumo": criterio,
        "meses_analisados": meses_analisados,
        "hsp_fonte": hsp_fonte,
        **resultado,
    }


def formatar_proposta(p):
    """Texto com todos os itens exigidos na seção 12 da atividade."""
    mod, inv, orc = p["modulo"], p["inversor"], p["orcamento"]
    st, arm = p["strings"], p["armazenamento"]
    local = f"{p['imovel']['cidade']}/{p['imovel']['uf']}" if p["imovel"].get("cidade") else "local não informado"
    nomes_criterio = {"media": "média", "maximo": "maior consumo"}
    criterio = nomes_criterio.get(p["criterio_consumo"], "valor informado")
    meses = f", {p['meses_analisados']} mês(es)" if p["meses_analisados"] else ""

    linhas = [
        "===== PROPOSTA PRELIMINAR DE SISTEMA FOTOVOLTAICO =====",
        f"Imóvel: {p['imovel']['nome']} ({local})",
        f"Consumo de referência utilizado: {p['consumo_referencia_kwh']:.2f} kWh/mês "
        f"({criterio}{meses})",
        f"Percentual de atendimento solicitado: {p['fracao'] * 100:.0f}%",
        f"Energia mensal que se pretende gerar: {p['energia_fv_kwh']:.2f} kWh/mês",
        f"HSP utilizado: {p['hsp']:.2f} kWh/m²/dia (fonte: {p['hsp_fonte']})",
        f"Fator de desempenho (η): {p['eta']:.2f} | dias considerados: {p['dias']}",
        f"Potência FV calculada: {p['potencia_fv_kwp']:.3f} kWp",
        f"Potência FV instalada: {p['potencia_instalada_kwp']:.3f} kWp",
        f"Módulos: {p['n_modulos']} × {mod['fabricante']} {mod['modelo']} ({mod['potencia_wp']:.0f} Wp)",
        f"Ligação: {st['strings']} string(s) de {st['modulos_em_serie']} módulo(s) em série "
        f"(Voc a frio {st['voc_frio_v']:.0f} V, Vmp a quente {st['vmp_quente_v']:.0f} V)",
        f"Inversor: {inv['fabricante']} {inv['modelo']} ({inv['potencia_nominal_w']:.0f} W, tipo {inv['tipo']})",
    ]

    if arm is None:
        linhas.append("Armazenamento: não (sistema sem baterias)")
    else:
        bat = arm["bateria"]
        linhas += [
            f"Armazenamento: sim, autonomia de {arm['autonomia_h']:.0f} h",
            f"  Capacidade calculada: {arm['capacidade_necessaria_kwh']:.2f} kWh (nominal)",
            f"  Baterias: {arm['quantidade']} × {bat['fabricante']} {bat['modelo']} "
            f"({bat['capacidade_kwh']:.2f} kWh, {bat['tecnologia']})",
            f"  Capacidade instalada: {arm['capacidade_instalada_kwh']:.2f} kWh nominais "
            f"({arm['capacidade_util_kwh']:.2f} kWh úteis)",
        ]
        if not arm["tensao_verificada"]:
            linhas.append("  Aviso: a faixa de tensão de bateria do inversor não consta no dataset; "
                          "compatibilidade de tensão NÃO verificada.")

    linhas += [
        f"Geração mensal estimada: {p['geracao_mensal_kwh']:.1f} kWh/mês "
        f"({p['cobertura_pct']:.1f}% do consumo de referência)",
        "",
        "--- Orçamento ---",
    ]
    for item in orc["itens"]:
        linhas.append(f"  {item['quantidade']} × {item['descricao']}: "
                      f"{formatar_brl(item['preco_unitario'])} un. = {formatar_brl(item['subtotal'])}")
    linhas.append(f"Custo dos equipamentos: {formatar_brl(orc['custo_equipamentos'])}")
    if orc["outros_considerados"]:
        for o in orc["outros"]:
            linhas.append(f"  Outros custos - {o['item']}: {formatar_brl(o['custo'])}")
        linhas.append(f"Outros custos (total): {formatar_brl(orc['custo_outros'])}")
    else:
        linhas.append("Outros custos: não considerados (data/outros_custos.csv vazio)")
    linhas += [f"CUSTO TOTAL ESTIMADO: {formatar_brl(orc['custo_total'])}", "", AVISO]
    return "\n".join(linhas)


def salvar_proposta(usuario_id, imovel_id, proposta):
    """PB35 - Grava a proposta (somente em imóvel do próprio usuário - PB15)."""
    if not imovel.imovel_pertence_ao_usuario(imovel_id, usuario_id):
        return False, "Imóvel não encontrado ou não pertence a este usuário."

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO propostas (usuario_id, imovel_id, dados_json) VALUES (?, ?, ?)",
        (usuario_id, imovel_id, json.dumps(proposta, ensure_ascii=False)),
    )
    conexao.commit()
    novo_id = cursor.lastrowid
    conexao.close()
    return True, novo_id


def listar_propostas(usuario_id):
    """PB35 - Lista só as propostas do usuário logado (mais recentes primeiro)."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, imovel_id, criada_em, dados_json FROM propostas "
        "WHERE usuario_id = ? ORDER BY id DESC",
        (usuario_id,),
    )
    linhas = cursor.fetchall()
    conexao.close()

    resultado = []
    for id_, imovel_id, criada_em, dados_json in linhas:
        dados = json.loads(dados_json)
        resultado.append({
            "id": id_, "imovel_id": imovel_id, "criada_em": criada_em,
            "imovel_nome": dados["imovel"]["nome"],
            "potencia_instalada_kwp": dados["potencia_instalada_kwp"],
            "custo_total": dados["orcamento"]["custo_total"],
            "com_bateria": dados["armazenamento"] is not None,
        })
    return resultado


def carregar_proposta(usuario_id, proposta_id):
    """PB35 - Reabre uma proposta salva. Devolve None se não existir ou for de outro usuário."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT dados_json FROM propostas WHERE id = ? AND usuario_id = ?",
        (proposta_id, usuario_id),
    )
    linha = cursor.fetchone()
    conexao.close()
    return json.loads(linha[0]) if linha else None
