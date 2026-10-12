# Premissas, fontes e cenários (texto pronto para o README.md)

Copie as seções abaixo para o `README.md`, no lugar das tabelas de premissas e de fontes. Onde houver `[preencher]`, complete com o que a equipe fez.

## Premissas e justificativas técnicas

### Fator de desempenho global (η = 0,75)
Adotou-se η = 0,75 como fator de desempenho global (Performance Ratio) do sistema. Ele agrupa, de forma simplificada, perdas por temperatura, sujeira, sombreamento parcial, descasamento entre módulos, queda de tensão nos cabos e eficiência de conversão do inversor. O valor é **conservador** em relação a estudos brasileiros de sistemas conectados à rede, que medem PR em torno de 80%: dissertação da UTFPR (Paraná, 2020), com PR médio estimado próximo de 80%, e artigo do CBENS, com PR de 80,29% em um sistema analisado. É uma premissa de pré-dimensionamento; em projeto real o PR deve ser calculado com dados do local e dos equipamentos.
Referência técnica complementar: *Manual de Engenharia para Sistemas Fotovoltaicos* (CEPEL/CRESESB). [preencher: capítulo e página lidos, se for citar o manual]

### Margens de tensão (1,12 e 0,85)
O dataset mínimo não traz os coeficientes de temperatura de cada módulo. Por isso o sistema aplica margens fixas sobre as tensões em STC:
- Voc a frio = módulos em série × Voc × 1,12. A Voc aumenta quando a temperatura cai; a regra evita ultrapassar a tensão máxima de entrada do inversor.
- Vmp a quente = módulos em série × Vmp × 0,85. A Vmp diminui com o calor; a regra evita ficar abaixo do início da faixa MPPT.
São margens simplificadas, não valores de norma. Com os coeficientes de temperatura de cada datasheet o resultado seria mais preciso.

### Corrente e potência do inversor
- Se o dataset informa a corrente máxima de curto-circuito do inversor, ela decide a segurança (a Isc do arranjo por MPPT não pode ultrapassá-la). Imp acima da corrente máxima de entrada gera um aviso, porque o inversor apenas limita a corrente (possível pequena perda de geração).
- Se o limite de curto-circuito não consta no dataset, o sistema é conservador e reprova quando a Imp passa da corrente máxima de entrada.
- Razão FV/CA aceita: de 0,5 a 1,5 (editável em `parametros.py`).

### Baterias
C_bat = E_autonomia / (DoD × η_bat) e N_bat = ⌈C_bat / capacidade nominal da bateria⌉. O DoD usado é o de cada bateria do dataset; η_bat = 0,95 é uma premissa, porque os datasheets consultados não trazem esse valor.

### Outros custos
Vêm de `data/outros_custos.csv`, cada item com fonte. A mão de obra de instalação usa uma estimativa de referência de mercado (R$ 850 por kWp), não um orçamento de instalador.

## Tabela de fontes dos datasets (consulta de 2026-10-11 e 2026-10-12)

| Dataset | Fonte | Observação |
|---|---|---|
| `hsp.csv` | CRESESB/SunData (http://cresesb.cepel.br/index.php#data), estação São Paulo/SP a 5,4 km do ponto de referência, plano inclinado com ângulo igual à latitude (24°), média anual de 4,65 kWh/m²/dia | Print e transcrição em `evidencias/`. Confirmar se a cidade do imóvel de teste é São Paulo/SP |
| `modulos.csv` | Lojas: Minha Casa Solar, Eletrotrafo, Direta Energia Solar, Buyers Energy. Fichas: página da loja, datasheets de TCL, Honor e Trina, distribuidora Techlux (Ronma) e registro INMETRO | Cada linha traz o link do produto e a fonte da ficha. Preço e estoque mudam: conferir antes de entregar |
| `inversores.csv` | Lojas: Minha Casa Solar e Neosolar. Fichas: página da loja e site da Deye (série SG04LP1) | Alguns itens estavam em pré-venda ou indisponíveis (ver coluna `observacao`) |
| `baterias.csv` | Lojas: MeuGerador, Energy Shop e Minha Casa Solar. Ficha da Deye no site do fabricante | Livoltek e Unipower estavam em pré-venda |
| `outros_custos.csv` | SGV Solar, Shopuruara, Energy Shop e artigo de mercado (larpontual.com.br) | Instalação é estimativa de referência |

## Cenários testados
[preencher: rodar `python cenarios.py --consumo <média real> --hsp 4.65 --fonte-hsp "CRESESB/SunData, São Paulo/SP" --cidade "São Paulo" --uf SP --autonomia 12` e citar `evidencias/cenario_sem_bateria.txt` e `evidencias/cenario_com_bateria.txt`, com consumo de referência, potência instalada, equipamentos e custo total de cada um.]

## Limitações conhecidas
- Preços e disponibilidade de loja variam; as consultas valem para as datas indicadas.
- A validação elétrica é simplificada (margens de tensão e de corrente) e não substitui projeto executivo.
- Não considera sombreamento, orientação, inclinação específica do telhado nem perdas do local.
