"""
cenarios.py

Gera as evidências exigidas (PB37): um cenário SEM bateria e um COM bateria,
usando os datasets de data/. Salva os resultados em evidencias/.

Exemplo:
    python cenarios.py --consumo 346 --hsp 4.5 --fonte-hsp "CRESESB/SunData, Campinas/SP" \
        --cidade Campinas --uf SP --percentual 100 --autonomia 12

Use o consumo e o HSP reais do imóvel de teste e registre a fonte do HSP.
"""

import argparse
import os

import dimensionamento
import equipamentos
import orcamento
import parametros
import proposta

PASTA_EVIDENCIAS = "evidencias"


def main():
    ap = argparse.ArgumentParser(description="Gera os cenários sem e com bateria.")
    ap.add_argument("--consumo", type=float, required=True, help="consumo de referência (kWh/mês)")
    ap.add_argument("--hsp", type=float, required=True, help="HSP médio (kWh/m²/dia)")
    ap.add_argument("--fonte-hsp", required=True, help="origem do HSP (ex.: CRESESB/SunData)")
    ap.add_argument("--cidade", default="")
    ap.add_argument("--uf", default="")
    ap.add_argument("--percentual", type=float, default=100.0, help="% do consumo a atender")
    ap.add_argument("--eta", type=float, default=parametros.ETA_PADRAO)
    ap.add_argument("--autonomia", type=float, default=12.0, help="horas de autonomia (cenário com bateria)")
    ap.add_argument("--pasta", default=equipamentos.PASTA_DADOS, help="pasta com os CSVs")
    args = ap.parse_args()

    modulos, e1 = equipamentos.carregar_modulos(args.pasta)
    inversores, e2 = equipamentos.carregar_inversores(args.pasta)
    baterias, e3 = equipamentos.carregar_baterias(args.pasta)
    outros, e4 = orcamento.carregar_outros_custos(os.path.join(args.pasta, "outros_custos.csv"))
    for erro in e1 + e2 + e3 + e4:
        print(f"Aviso (dataset): {erro}")

    os.makedirs(PASTA_EVIDENCIAS, exist_ok=True)
    imovel_teste = {"id": None, "nome": "Cenário de teste", "cidade": args.cidade, "uf": args.uf}

    for nome, com_bateria in (("sem_bateria", False), ("com_bateria", True)):
        ok, resultado = dimensionamento.dimensionar(
            args.consumo, args.hsp, args.percentual / 100, args.eta, modulos, inversores,
            baterias=baterias, outros_custos=outros, com_bateria=com_bateria,
            autonomia_h=args.autonomia if com_bateria else None)
        caminho = os.path.join(PASTA_EVIDENCIAS, f"cenario_{nome}.txt")
        if ok:
            p = proposta.montar_proposta(imovel_teste, "informado", None, args.fonte_hsp, resultado)
            texto = proposta.formatar_proposta(p)
        else:
            texto = "Não foi possível dimensionar:\n" + "\n".join(resultado)
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
        print(f"\n##### Cenário {nome.replace('_', ' ')} -> {caminho}\n{texto}")


if __name__ == "__main__":
    main()
