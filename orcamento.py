"""
orcamento.py

Orçamento do pré-dimensionamento (PB32, PB33).

    C_equipamentos = C_módulos + C_inversor + C_baterias
    C_total        = C_equipamentos + outros custos

"Outros custos" (estrutura, cabos, proteções, instalação...) NÃO são inventados
pelo sistema: vêm de data/outros_custos.csv, onde a equipe registra cada item
com a fonte da premissa. Se o arquivo estiver vazio, outros custos = 0 e a
proposta avisa isso.

Colunas de outros_custos.csv:
    item, tipo, valor, fonte, data_coleta, url_fonte
    tipo = percentual (valor em % do custo dos equipamentos)
         | por_kwp    (valor em R$ por kWp instalado)
         | fixo       (valor em R$)
"""

import csv
import os

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CAMINHO_OUTROS = os.path.join(PASTA_DADOS, "outros_custos.csv")
COLUNAS_OUTROS = ["item", "tipo", "valor", "fonte", "data_coleta", "url_fonte"]
TIPOS_OUTROS = ("percentual", "por_kwp", "fixo")


def carregar_outros_custos(caminho=CAMINHO_OUTROS):
    """Lê outros_custos.csv. Retorna (lista, erros). Arquivo ausente/vazio -> ([], [])."""
    if not os.path.exists(caminho):
        return [], []

    lista, erros = [], []
    with open(caminho, newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        faltando = [c for c in COLUNAS_OUTROS if c not in (leitor.fieldnames or [])]
        if faltando:
            return [], [f"outros_custos.csv: colunas ausentes: {', '.join(faltando)}"]
        for numero, linha in enumerate(leitor, start=2):
            item = (linha["item"] or "").strip()
            tipo = (linha["tipo"] or "").strip().lower()
            fonte = (linha["fonte"] or "").strip()
            try:
                valor = float(linha["valor"])
            except (TypeError, ValueError):
                erros.append(f"outros_custos.csv linha {numero}: valor não numérico (use ponto decimal).")
                continue
            if not item or tipo not in TIPOS_OUTROS or valor < 0 or not fonte:
                erros.append(
                    f"outros_custos.csv linha {numero}: item e fonte obrigatórios, valor ≥ 0 e "
                    f"tipo em {', '.join(TIPOS_OUTROS)}.")
                continue
            lista.append({"item": item, "tipo": tipo, "valor": valor, "fonte": fonte})
    return lista, erros


def calcular_orcamento(modulo, n_modulos, inversor, p_instalada_kwp, armazenamento=None, outros_custos=None):
    """Monta o orçamento a partir dos equipamentos selecionados.

    'armazenamento' é o dicionário devolvido por selecao.selecionar_bateria
    (ou None quando não há bateria: custo das baterias = 0).
    """
    itens = [
        {"descricao": f"Módulo {modulo['fabricante']} {modulo['modelo']} ({modulo['id']})",
         "quantidade": n_modulos, "preco_unitario": modulo["preco_brl"],
         "subtotal": round(n_modulos * modulo["preco_brl"], 2)},
        {"descricao": f"Inversor {inversor['fabricante']} {inversor['modelo']} ({inversor['id']})",
         "quantidade": 1, "preco_unitario": inversor["preco_brl"],
         "subtotal": round(inversor["preco_brl"], 2)},
    ]
    custo_baterias = 0.0
    if armazenamento is not None:
        bat = armazenamento["bateria"]
        custo_baterias = round(armazenamento["quantidade"] * bat["preco_brl"], 2)
        itens.append({
            "descricao": f"Bateria {bat['fabricante']} {bat['modelo']} ({bat['id']})",
            "quantidade": armazenamento["quantidade"], "preco_unitario": bat["preco_brl"],
            "subtotal": custo_baterias})

    custo_modulos = itens[0]["subtotal"]
    custo_inversor = itens[1]["subtotal"]
    custo_equipamentos = round(custo_modulos + custo_inversor + custo_baterias, 2)

    outros = []
    for oc in (outros_custos or []):
        if oc["tipo"] == "percentual":
            custo = custo_equipamentos * oc["valor"] / 100
        elif oc["tipo"] == "por_kwp":
            custo = oc["valor"] * p_instalada_kwp
        else:
            custo = oc["valor"]
        outros.append({**oc, "custo": round(custo, 2)})
    custo_outros = round(sum(o["custo"] for o in outros), 2)

    return {
        "itens": itens,
        "custo_modulos": custo_modulos,
        "custo_inversor": custo_inversor,
        "custo_baterias": custo_baterias,
        "custo_equipamentos": custo_equipamentos,
        "outros": outros,
        "custo_outros": custo_outros,
        "outros_considerados": bool(outros),
        "custo_total": round(custo_equipamentos + custo_outros, 2),
    }
