"""
solar.py

Recurso solar (PB19): busca o HSP (Horas de Sol Pleno) da cidade do imóvel
em data/hsp.csv. Cada linha do arquivo deve ter a fonte do dado.

Colunas de hsp.csv:
    cidade, uf, hsp_kwh_m2_dia, fonte, data_coleta, url_fonte

hsp_kwh_m2_dia = média anual de irradiação no plano (kWh/m²/dia), usando ponto
como separador decimal. Preencha com dados de CRESESB (SunData) ou do Atlas
Brasileiro de Energia Solar e registre qual foi a fonte.
"""

import csv
import os
import unicodedata

import parametros

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CAMINHO_HSP = os.path.join(PASTA_DADOS, "hsp.csv")
COLUNAS_HSP = ["cidade", "uf", "hsp_kwh_m2_dia", "fonte", "data_coleta", "url_fonte"]


def _normalizar(texto):
    """Minúsculas, sem acentos e sem espaços nas pontas (para comparar cidades)."""
    texto = unicodedata.normalize("NFKD", (texto or "").strip().lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def carregar_hsp(caminho=CAMINHO_HSP):
    """Lê o CSV de HSP. Retorna (registros, erros).
    Se o arquivo não existir ou estiver só com o cabeçalho, devolve ([], []).
    """
    if not os.path.exists(caminho):
        return [], []

    registros, erros = [], []
    with open(caminho, newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        faltando = [c for c in COLUNAS_HSP if c not in (leitor.fieldnames or [])]
        if faltando:
            return [], [f"hsp.csv: colunas ausentes: {', '.join(faltando)}"]

        for numero, linha in enumerate(leitor, start=2):
            cidade = (linha["cidade"] or "").strip()
            uf = (linha["uf"] or "").strip().upper()
            try:
                hsp = float(linha["hsp_kwh_m2_dia"])
            except (TypeError, ValueError):
                erros.append(f"hsp.csv linha {numero}: HSP não numérico (use ponto decimal).")
                continue
            ok, mensagem = parametros.validar_hsp(hsp)
            if not ok:
                erros.append(f"hsp.csv linha {numero}: {mensagem}")
                continue
            if not cidade or not uf:
                erros.append(f"hsp.csv linha {numero}: cidade e uf são obrigatórias.")
                continue
            if not (linha["fonte"] or "").strip():
                erros.append(f"hsp.csv linha {numero}: informe a fonte do dado.")
                continue
            registros.append({
                "cidade": cidade, "uf": uf, "hsp": hsp,
                "fonte": linha["fonte"].strip(),
                "data_coleta": (linha["data_coleta"] or "").strip(),
                "url_fonte": (linha["url_fonte"] or "").strip(),
            })
    return registros, erros


def buscar_hsp(cidade, uf, caminho=CAMINHO_HSP):
    """Retorna o registro de HSP da cidade/UF, ou None se não estiver no arquivo."""
    registros, _ = carregar_hsp(caminho)
    for registro in registros:
        if _normalizar(registro["cidade"]) == _normalizar(cidade) and registro["uf"] == (uf or "").strip().upper():
            return registro
    return None
