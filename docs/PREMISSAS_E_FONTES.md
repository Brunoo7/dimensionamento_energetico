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

### Módulos extras para compatibilizar com o inversor
O sistema primeiro tenta atender a potência calculada com a quantidade necessária de módulos. Se nenhum inversor servir (por exemplo, a tensão das strings fica abaixo do início da faixa MPPT), acrescenta módulos, um a um, até um máximo de 4 (`MODULOS_EXTRAS_MAX` em `parametros.py`). Nesse caso a proposta avisa quantos módulos foram acrescentados e que a geração estimada fica acima do consumo de referência.

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
| Consumo de referência dos cenários | Consumo médio mensal de uma unidade residencial no Brasil, cerca de 160 kWh, atribuído à EPE (2023) em trabalho acadêmico (https://static.even3.com/anais/1298453.pdf) | **Valor simulado**, citado de forma indireta: conferir no Anuário Estatístico de Energia Elétrica da EPE antes de entregar |

## Cenários testados
Entradas comuns: consumo de referência **simulado** de 160 kWh/mês (média nacional residencial, não é um imóvel real), atendimento de 100%, HSP de 4,65 kWh/m²/dia (CRESESB/SunData, São Paulo/SP, 24°, média anual), η = 0,75. Resultados completos em `evidencias/cenario_sem_bateria.txt` e `evidencias/cenario_com_bateria.txt`.

| Item | Cenário A (sem bateria) | Cenário B (com bateria, 12 h) |
|---|---|---|
| Potência FV calculada | 1,529 kWp | 1,529 kWp |
| Módulos | 3 × Canadian Solar CS6W-550MS | 5 × Canadian Solar CS6W-550MS (2 a mais, para a faixa MPPT do inversor) |
| Potência instalada | 1,650 kWp | 2,750 kWp |
| Inversor | Deye SUN-3K-G04P1-EU-AM1 (string) | Deye SUN-5K-SG04LP1-EU (híbrido) |
| Armazenamento | não | 1 × Livoltek BLF-B51100 (5,12 kWh nominais; necessário 3,12 kWh) |
| Geração estimada | 172,6 kWh/mês (107,9%) | 287,7 kWh/mês (179,8%) |
| Custo dos equipamentos | R$ 3.022,27 | R$ 14.613,80 |
| Outros custos | R$ 2.513,00 | R$ 3.723,00 |
| **Custo total estimado** | **R$ 5.535,27** | **R$ 18.336,80** |

Observações: os preços dependem da confirmação dos links (alguns itens estavam em pré-venda ou indisponíveis); o consumo é simulado e deve ser substituído pelo de um imóvel real, se houver.

## Limitações conhecidas
- Preços e disponibilidade de loja variam; as consultas valem para as datas indicadas.
- A validação elétrica é simplificada (margens de tensão e de corrente) e não substitui projeto executivo.
- Não considera sombreamento, orientação, inclinação específica do telhado nem perdas do local.
