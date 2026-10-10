"""
equipamentos.py

Datasets de equipamentos fotovoltaicos (PB21, PB22, PB23) e validação deles (PB24).

Arquivos (na pasta data/):
    modulos.csv     - mínimo de 10 módulos
    inversores.csv  - mínimo de 8 inversores
    baterias.csv    - mínimo de 6 baterias

Regras:
    - Só produtos REAIS, com especificação do datasheet e preço de fornecedor
      brasileiro (campos fornecedor, data_coleta e url_fonte).
    - Unidades padronizadas, ponto como separador decimal, sem símbolo de moeda.
    - As funções carregar_* devolvem (registros, erros). Se "erros" não estiver
      vazio, o arquivo tem linhas inválidas (a mensagem diz arquivo e linha).
"""

import csv
import os

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Campos de texto (obrigatórios em todos os arquivos)
_TEXTO_COMUM = ["id", "fabricante", "modelo", "fornecedor", "data_coleta", "url_fonte"]

ESQUEMAS = {
    "modulos": {
        "arquivo": "modulos.csv",
        "minimo": 10,
        "texto": _TEXTO_COMUM,
        "numericos": ["potencia_wp", "voc_v", "isc_a", "vmp_v", "imp_a", "eficiencia_pct", "preco_brl"],
        "colunas": ["id", "fabricante", "modelo", "potencia_wp", "voc_v", "isc_a", "vmp_v", "imp_a",
                    "eficiencia_pct", "preco_brl", "fornecedor", "data_coleta", "url_fonte"],
    },
    "inversores": {
        "arquivo": "inversores.csv",
        "minimo": 8,
        "texto": _TEXTO_COMUM + ["tipo", "compativel_bateria"],
        "numericos": ["potencia_nominal_w", "potencia_max_fv_w", "tensao_max_entrada_v",
                      "faixa_mppt_min_v", "faixa_mppt_max_v", "corrente_max_entrada_a",
                      "numero_mppt", "preco_brl"],
        "colunas": ["id", "fabricante", "modelo", "tipo", "potencia_nominal_w", "potencia_max_fv_w",
                    "tensao_max_entrada_v", "faixa_mppt_min_v", "faixa_mppt_max_v",
                    "corrente_max_entrada_a", "numero_mppt", "compativel_bateria",
                    "preco_brl", "fornecedor", "data_coleta", "url_fonte"],
    },
    "baterias": {
        "arquivo": "baterias.csv",
        "minimo": 6,
        "texto": _TEXTO_COMUM + ["tecnologia"],
        "numericos": ["tensao_nominal_v", "capacidade_ah", "capacidade_kwh", "dod_pct", "ciclos", "preco_brl"],
        "colunas": ["id", "fabricante", "modelo", "tecnologia", "tensao_nominal_v", "capacidade_ah",
                    "capacidade_kwh", "dod_pct", "ciclos", "preco_brl", "fornecedor",
                    "data_coleta", "url_fonte"],
    },
}

VALORES_COMPATIVEL_BATERIA = ("sim", "nao")
TOLERANCIA_KWH = 0.05   # 5 % entre capacidade_kwh e tensão × Ah / 1000


def _validar_regras_especificas(tipo, registro):
    """Regras extras por tipo de equipamento. Retorna lista de mensagens de erro."""
    erros = []
    if registro["preco_brl"] <= 0:
        erros.append("preco_brl deve ser maior que zero.")
    if not registro["url_fonte"].lower().startswith("http"):
        erros.append("url_fonte deve ser um link (http/https).")

    if tipo == "modulos":
        if registro["potencia_wp"] <= 0:
            erros.append("potencia_wp deve ser maior que zero.")
        if not (0 < registro["eficiencia_pct"] <= 100):
            erros.append("eficiencia_pct deve estar entre 0 e 100.")
    elif tipo == "inversores":
        if registro["compativel_bateria"] not in VALORES_COMPATIVEL_BATERIA:
            erros.append("compativel_bateria deve ser 'sim' ou 'nao'.")
        if registro["faixa_mppt_min_v"] >= registro["faixa_mppt_max_v"]:
            erros.append("faixa_mppt_min_v deve ser menor que faixa_mppt_max_v.")
        if registro["potencia_nominal_w"] <= 0 or registro["numero_mppt"] < 1:
            erros.append("potencia_nominal_w e numero_mppt devem ser positivos.")
    elif tipo == "baterias":
        if not (0 < registro["dod_pct"] <= 100):
            erros.append("dod_pct deve estar entre 0 e 100.")
        esperado = registro["tensao_nominal_v"] * registro["capacidade_ah"] / 1000
        if registro["capacidade_kwh"] <= 0 or abs(registro["capacidade_kwh"] - esperado) > TOLERANCIA_KWH * esperado:
            erros.append(
                f"capacidade_kwh ({registro['capacidade_kwh']}) não confere com "
                f"tensão × Ah / 1000 ({esperado:.2f}); diferença máxima aceita: 5%."
            )
    return erros


def carregar_dataset(tipo, pasta=PASTA_DADOS):
    """Lê e valida um dataset. tipo: 'modulos', 'inversores' ou 'baterias'.
    Retorna (registros_validos, erros).
    """
    esquema = ESQUEMAS[tipo]
    caminho = os.path.join(pasta, esquema["arquivo"])
    nome = esquema["arquivo"]

    if not os.path.exists(caminho):
        return [], [f"{nome}: arquivo não encontrado em {pasta}."]

    registros, erros, ids_vistos = [], [], set()
    with open(caminho, newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        faltando = [c for c in esquema["colunas"] if c not in (leitor.fieldnames or [])]
        if faltando:
            return [], [f"{nome}: colunas ausentes: {', '.join(faltando)}"]

        for numero, linha in enumerate(leitor, start=2):
            problemas = []
            registro = {}

            for campo in esquema["texto"]:
                valor = (linha[campo] or "").strip()
                if not valor:
                    problemas.append(f"campo '{campo}' vazio.")
                registro[campo] = valor.lower() if campo == "compativel_bateria" else valor

            for campo in esquema["numericos"]:
                try:
                    registro[campo] = float(linha[campo])
                except (TypeError, ValueError):
                    problemas.append(f"campo '{campo}' não é numérico (use ponto decimal, sem unidade).")

            if not problemas:
                problemas += _validar_regras_especificas(tipo, registro)
                if registro["id"] in ids_vistos:
                    problemas.append(f"id '{registro['id']}' duplicado.")

            if problemas:
                erros.append(f"{nome} linha {numero}: " + " ".join(problemas))
            else:
                ids_vistos.add(registro["id"])
                registros.append(registro)

    return registros, erros


def carregar_modulos(pasta=PASTA_DADOS):
    return carregar_dataset("modulos", pasta)


def carregar_inversores(pasta=PASTA_DADOS):
    return carregar_dataset("inversores", pasta)


def carregar_baterias(pasta=PASTA_DADOS):
    return carregar_dataset("baterias", pasta)


def verificar_quantidade_minima(tipo, registros):
    """PB21-PB23 - Confere se o dataset atingiu o mínimo exigido. Retorna (ok, mensagem)."""
    minimo = ESQUEMAS[tipo]["minimo"]
    if len(registros) < minimo:
        return False, f"{ESQUEMAS[tipo]['arquivo']}: {len(registros)} válido(s); mínimo exigido: {minimo}."
    return True, ""


def selecionar_modulo_mais_barato(modulos):
    """PB26 - Critério de seleção documentado: menor custo por Wp (R$/Wp).
    Retorna o módulo escolhido ou None se a lista estiver vazia.
    """
    if not modulos:
        return None
    return min(modulos, key=lambda m: m["preco_brl"] / m["potencia_wp"])
