# Candidatos pesquisados (CONFERIR ANTES DE USAR)

Estes CSVs têm o mesmo formato dos de `data/`, mais duas colunas extras (`fonte_especificacao` e `observacao`).
Cada linha vem de páginas de lojas brasileiras consultadas em **2026-10-11**; o `url_fonte` aponta para a página do produto.

**Não são dados finais.** Preço e estoque mudam, algumas páginas divergem entre lojas e uma delas bloqueou a leitura automática.
Antes de copiar uma linha para `data/*.csv`:

1. Abra o `url_fonte` e confirme o preço e a disponibilidade. Atualize `preco_brl` e `data_coleta` se mudaram.
2. Confira os valores elétricos no datasheet do fabricante (a coluna `fonte_especificacao` diz de onde vieram).
3. Leia a coluna `observacao`, que registra divergências encontradas.
4. Copie a linha para o CSV de `data/` (as colunas extras podem ficar ou ser removidas) e rode `python validar_datasets.py`.

## O que há aqui

| Arquivo | Linhas | Mínimo exigido |
|---|---|---|
| modulos.csv | 3 (Canadian Solar CS6W-550MS, Ronma RM-585W-182M/144TB, Osda ODA585-144MHD) | 10 |
| inversores.csv | 3 (Growatt MIC3000TL-X; híbridos Deye SUN-5K-SG04LP1-EU e SUN-5K-SG02LP2-US-AM2) | 8 |
| baterias.csv | 1 (Deye SE-G5.1 Pro-B) | 6 |

Faltam também `hsp.csv` (consulta ao CRESESB/SunData, que é um formulário interativo) e `outros_custos.csv`.
Com estes candidatos, os dois cenários (sem e com bateria) já rodam no sistema usando um HSP de exemplo.
