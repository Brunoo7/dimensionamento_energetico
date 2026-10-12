# Candidatos de equipamentos — conferir antes de usar em orçamento real

Este diretório mantém opções pesquisadas que ainda exigem confirmação comercial e/ou técnica. Os CSVs de `data/` são a base usada nos cenários do programa; a aprovação do validador confirma apenas estrutura, tipos e quantidades, não garante estoque, preço atual nem compatibilidade certificada.

## Conteúdo e quantidade mínima

| Arquivo | Registros em `data/` | Mínimo exigido | Observação |
|---|---:|---:|---|
| `modulos.csv` | 10 | 10 | M09 e M10 completam a quantidade. As páginas consultadas indicavam indisponibilidade; M10 tinha compra mínima de 12 unidades. |
| `inversores.csv` | 8 | 8 | A base inclui inversores string e híbridos. Verifique a coluna `observacao` para disponibilidade e diferenças de especificação. |
| `baterias.csv` | 6 | 6 | Alguns modelos estavam em pré-venda ou indisponíveis na consulta. |
| `hsp.csv` | 1 localidade | 1 | HSP de São Paulo/SP transcrito de consulta ao CRESESB/SunData; evidência em `evidencias/`. |
| `outros_custos.csv` | preenchido | — | Inclui estimativas e respectivas fontes; mão de obra não é cotação formal. |

## Conferência antes de uma instalação real

1. Abra `url_fonte` de cada equipamento e confirme preço, estoque, frete, variante exata e quantidade mínima.
2. Confira parâmetros elétricos no datasheet oficial do fabricante e compare modelo/variante com o registro comercial.
3. Atualize `preco_brl`, `data_coleta`, `fornecedor` e `observacao` sem apagar o histórico de divergências relevantes.
4. Rode `python validar_datasets.py` e `python -m unittest discover -s tests -t .`.
5. Não trate o orçamento gerado como proposta comercial final ou projeto elétrico executivo.

As datas registradas nos CSVs representam a consulta documentada em outubro de 2026, não uma garantia de que os links e preços continuem válidos.
