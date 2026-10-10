# Datasets de equipamentos e HSP

Arquivos desta pasta: `hsp.csv`, `modulos.csv`, `inversores.csv`, `baterias.csv`.
Eles estão **só com o cabeçalho**: os dados precisam ser reais e pesquisados pela equipe.

## Regras
- Apenas produtos reais comercializados no Brasil. **Não use dados fictícios.**
- Especificações técnicas: datasheet do fabricante. Preços: loja/fornecedor brasileiro.
- Ponto como separador decimal (`550.0`), sem unidade nem `R$` nas células.
- Unidades: W, Wp, V, A, kWh, Ah, % (0 a 100), BRL.
- `compativel_bateria` em inversores: `sim` ou `nao`. `tipo`: por exemplo `string` ou `hibrido`.
- Preencha `fornecedor`, `data_coleta` (AAAA-MM-DD) e `url_fonte` em todas as linhas.
- Quantidades mínimas: 10 módulos, 8 inversores (pelo menos 2 híbridos), 6 baterias.

## Como conferir
`python -m unittest discover -s tests -t .` roda os testes automáticos.
`python validar_datasets.py` valida os CSVs e mostra erros por arquivo e linha.

## Fontes (preencha ao coletar)
| Dataset | Fonte | Data da coleta | Observação |
|---|---|---|---|
| hsp.csv | (CRESESB/SunData ou Atlas Brasileiro de Energia Solar) | | |
| modulos.csv | | | |
| inversores.csv | | | |
| baterias.csv | | | |
