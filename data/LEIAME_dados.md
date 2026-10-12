# Datasets de equipamentos e HSP

A pasta contém `hsp.csv`, `modulos.csv`, `inversores.csv`, `baterias.csv` e `outros_custos.csv`. Os dados foram reunidos a partir de fontes públicas e são destinados a um exercício acadêmico de pré-dimensionamento.

## Regras de formato

- CSV em UTF-8, separador vírgula e ponto como separador decimal (por exemplo, `550.0`); não inclua unidades nem `R$` nos campos numéricos.
- Unidades esperadas: Wp, V, A, kWh, Ah, porcentagem de 0 a 100 e BRL.
- `compativel_bateria` deve ser `sim` ou `nao`; `tipo` identifica, por exemplo, inversor `string` ou `hibrido`.
- Cada equipamento deve ter identificador, fabricante/modelo, especificações, preço, fornecedor, data de coleta e URL da fonte.
- Quantidades mínimas: 10 módulos, 8 inversores (pelo menos 2 híbridos) e 6 baterias.

## Validação

Execute na raiz do projeto:

```bash
python validar_datasets.py
python -m unittest discover -s tests -t .
```

O validador verifica estrutura, campos, valores e quantidades; ele não verifica automaticamente a veracidade das especificações, o estoque, o preço atual ou a adequação de um equipamento a uma instalação real.

## Fontes e limitações

- HSP: consulta ao CRESESB/SunData para São Paulo/SP; transcrição e data da consulta em `evidencias/sundata_sao_paulo_2026-10-11.txt` e `data/hsp.csv`.
- Módulos, inversores e baterias: cada registro traz `url_fonte`; quando disponível, `fonte_especificacao` identifica a ficha técnica utilizada. Consulte também `data/candidatos/LEIAME.md`.
- Outros custos: cada item contém fonte e/ou observação. O custo de instalação é uma estimativa de referência, não cotação de instalador.
- Cenários: o consumo de 160 kWh/mês é um valor simulado para demonstrar o fluxo, não um dado medido nem uma média oficial atribuída à EPE.

Preços e disponibilidade mudam. Antes de qualquer uso comercial ou instalação, confirme os dados com o fornecedor e submeta o dimensionamento à análise de profissional habilitado.
