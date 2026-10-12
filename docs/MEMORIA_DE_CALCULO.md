# Memória de cálculo dos cenários

Evidência passo a passo dos cálculos de `evidencias/cenario_sem_bateria.txt` e `evidencias/cenario_com_bateria.txt`.
Reproduza com: `python cenarios.py --consumo 160 --hsp 4.65 --fonte-hsp "CRESESB/SunData; São Paulo/SP; evidência registrada" --cidade "São Paulo" --uf SP --percentual 100 --autonomia 12`

**Entradas (comuns):** C_m = 160 kWh/mês (simulado), f = 100% (1.00), HSP = 4.65 kWh/m²/dia (CRESESB/SunData, São Paulo/SP, 24°, média anual), D = 30 dias, η = 0.75, módulo M01 Canadian Solar CS6W-550MS (550 Wp).

## Geração fotovoltaica
| Passo | Fórmula | Conta | Resultado |
|---|---|---|---|
| Energia a gerar | E_FV = C_m × f | 160 × 1.00 | 160.00 kWh/mês |
| Fator solar | HSP × D × η | 4.65 × 30 × 0.75 | 104.6250 kWh/kWp |
| Potência necessária | P_FV = E_FV / (HSP × D × η) | 160 / 104.6250 | 1.529 kWp |
| Módulos (cenário A) | N = ⌈P_FV × 1000 / P_módulo⌉ | ⌈1529.3 / 550⌉ | 3 módulos |
| Potência instalada (A) | P_inst = N × P_módulo / 1000 | 3 × 550 / 1000 | 1.650 kWp |
| Geração estimada (A) | P_inst × HSP × D × η | 1.65 × 104.6250 | 172.6 kWh/mês (107.9% do consumo) |
| Módulos (cenário B) | N + 2 extras (faixa MPPT do inversor híbrido) | 3 + 2 | 5 módulos |
| Potência instalada (B) | 5 × 550 / 1000 | | 2.750 kWp |
| Geração estimada (B) | P_inst × HSP × D × η | 2.75 × 104.6250 | 287.7 kWh/mês (179.8% do consumo) |

## Verificação elétrica (margens de `parametros.py`)
| Cenário | Inversor | Voc a frio = n × Voc × 1,12 | Vmp a quente = n × Vmp × 0,85 | Limites do inversor | Razão FV/CA |
|---|---|---|---|---|---|
| A | I08 Deye SUN-3K-G04P1-EU-AM1 (3 kW) | 3 × 49,6 × 1,12 = 167 V | 3 × 41,7 × 0,85 = 106 V | tensão máx. 550 V; MPPT 70–500 V | 0.55 |
| B | I02 Deye SUN-5K-SG04LP1-EU (5 kW, híbrido) | 5 × 49,6 × 1,12 = 278 V | 5 × 41,7 × 0,85 = 177 V | tensão máx. 500 V; MPPT 150–425 V | 0.55 |

No cenário A, 3 módulos em série dão Vmp a quente de 106 V, acima de 70 V (início do MPPT do I08). No cenário B, 3 módulos dariam 106 V, abaixo dos 150 V do I02, por isso o sistema acrescenta módulos até a tensão ficar na faixa (5 módulos: 177 V).

## Baterias (cenário B, autonomia de 12 h)
| Passo | Fórmula | Conta | Resultado |
|---|---|---|---|
| Consumo diário | E_d = C_m / 30 | 160 / 30 | 5.333 kWh/dia |
| Energia de autonomia | E_autonomia = E_d × A / 24 | 5.333 × 12 / 24 | 2.667 kWh |
| Capacidade nominal necessária | C_bat = E_autonomia / (DoD × η_bat) | 2.667 / (0.9 × 0.95) | 3.12 kWh |
| Quantidade | N_bat = ⌈C_bat / C_nominal⌉ | ⌈3.12 / 5.12⌉ | 1 bateria (B03 Livoltek BLF-B51100) |
| Capacidade instalada | N_bat × C_nominal | 1 × 5.12 | 5.12 kWh nominais |
| Capacidade útil instalada | C_útil = C_nominal × DoD | 5.12 × 0.9 | 4.61 kWh |

O DoD entra uma vez só (em C_bat); N_bat usa a capacidade nominal para não contar o DoD duas vezes. O inversor I02 é híbrido (`compativel_bateria = sim`) e a tensão da bateria (51,2 V) está dentro da faixa de 40–60 V do inversor.

## Orçamento
| Item | Cenário A | Cenário B |
|---|---|---|
| Módulos M01 | 3 × R$ 449,90 = R$ 1.349,70 | 5 × R$ 449,90 = R$ 2.249,50 |
| Inversor | I08: R$ 1.699,00 | I02: R$ 6.887,78 |
| Bateria | R$ 0,00 | B03: R$ 5.375,27 |
| **Custo dos equipamentos** | **R$ 3.048,70** | **R$ 14.512,55** |
| Outros custos (estrutura, cabos, string box, instalação) | R$ 2.513,00 | R$ 3.723,00 |
| **Custo total estimado** | **R$ 5.561,70** | **R$ 18.235,55** |

Preços de catálogo consultados em 12/10/2026, não são cotação comercial (ver `docs/VERIFICACAO_PRECOS_DISPONIBILIDADE_2026-10-12.md`).
