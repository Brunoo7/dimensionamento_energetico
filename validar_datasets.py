"""
validar_datasets.py

Roda a validação (PB24) de modulos.csv, inversores.csv, baterias.csv e hsp.csv
e mostra os erros por arquivo e linha, além de conferir as quantidades mínimas.

Uso:  python validar_datasets.py
"""

import equipamentos
import solar


def main():
    houve_problema = False

    for tipo in ("modulos", "inversores", "baterias"):
        registros, erros = equipamentos.carregar_dataset(tipo)
        nome = equipamentos.ESQUEMAS[tipo]["arquivo"]
        print(f"{nome}: {len(registros)} linha(s) válida(s)")
        for erro in erros:
            print(f"  ERRO: {erro}")
        ok, mensagem = equipamentos.verificar_quantidade_minima(tipo, registros)
        if erros or not ok:
            houve_problema = True
        if not ok:
            print(f"  PENDENTE: {mensagem}")

    registros, erros = solar.carregar_hsp()
    print(f"hsp.csv: {len(registros)} cidade(s) válida(s)")
    for erro in erros:
        print(f"  ERRO: {erro}")
    if erros:
        houve_problema = True

    print("\nTudo certo!" if not houve_problema else "\nHá pendências a corrigir.")


if __name__ == "__main__":
    main()
