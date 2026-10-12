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
| modulos.csv | 8 (Canadian Solar, Ronma, Osda, TCL, Honor, Jinko, Trina, LONGi) | 10 |
| inversores.csv | 8 (Growatt MIC3000TL-X; Deye SUN-5K-G; BelEnergy BEL3KG; Deye SUN-3K-G04; híbridos Deye SG04LP1 de 3, 5 e 6 kW e SG02LP2 de 5 kW) | 8 |
| baterias.csv | 6 (Deye SE-G5.1 Pro-B, Deye SE-F5, MUST LP16, Livoltek BLF-B51100, GetPower GPLIFE48-100TS, Unipower UPLFP48) | 6 |

Faltam também `hsp.csv` (consulta ao CRESESB/SunData, que é um formulário interativo) e `outros_custos.csv`.
Com estes candidatos, os dois cenários (sem e com bateria) já rodam no sistema usando um HSP de exemplo.

## Dica para completar a lista
As páginas de produto da Minha Casa Solar (minhacasasolar.com.br) trazem ficha elétrica e preço na mesma página, e têm datasheet em PDF.
Escolham os itens que faltam nestas categorias e repitam o método acima:
painéis em /painel-solar/acima-de-370w, inversores string em /inversor/inversor-on-grid/inversor-string,
híbridos em /inversor-hibrido e baterias em /baterias/bateria-estacionaria/bateria-solar/bateria-de-litio.
Cuidado com lojas estrangeiras (preço em euro ou dólar) e com valores que diferem entre lojas: sempre confira o datasheet do fabricante.
