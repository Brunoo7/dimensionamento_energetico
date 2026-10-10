# Sistema de Dimensionamento Energético Residencial

Sistema em Python (sem POO, módulos simples, SQLite) que, a partir do histórico de consumo de um imóvel,
gera uma **proposta preliminar de sistema fotovoltaico** com estimativa de orçamento.

> Pré-dimensionamento acadêmico e estimativa de custos. **Não substitui projeto elétrico executivo,
> responsabilidade técnica ou análise de profissional habilitado.** Em uma instalação real é preciso verificar
> área disponível, orientação e inclinação, sombreamento, configuração de strings, limites do inversor,
> proteções, aterramento, estrutura, normas técnicas e requisitos da distribuidora.

## Como executar

Requer Python 3. O sistema usa só a biblioteca padrão; o `matplotlib` é opcional e serve apenas para salvar o gráfico em PNG (`pip install matplotlib`).

```
python main.py                                  # menu do sistema
python -m unittest discover -s tests -t .       # testes automáticos
python validar_datasets.py                      # confere os CSVs de data/
python cenarios.py --consumo 346 --hsp 4.5 --fonte-hsp "CRESESB/SunData, Cidade/UF" --cidade Cidade --uf SP
```

`cenarios.py` gera `evidencias/cenario_sem_bateria.txt` e `evidencias/cenario_com_bateria.txt`.
Use o consumo e o HSP reais do imóvel de teste.

## Fluxo do produto

Imóvel (cidade/UF) → histórico de consumo → consumo de referência → HSP → potência FV → módulos →
inversor e strings → baterias (opcional) → orçamento → proposta (salva no banco).

## Estrutura

| Arquivo | Função |
|---|---|
| `main.py` | menu de linha de comando |
| `usuario.py`, `imovel.py`, `consumo.py` | cadastro/login (senha com PBKDF2 + sal), imóvel (cidade/UF, editar e excluir) e consumo |
| `grafico.py` | gráfico do histórico de consumo (texto no terminal e PNG com matplotlib) |
| `dados.py` | SQLite: criação e migração das tabelas |
| `calculos.py` | fórmulas (consumo de referência, P_FV, módulos, geração, baterias) |
| `parametros.py` | valores padrão, limites e validações |
| `solar.py` | HSP por cidade (`data/hsp.csv`) |
| `equipamentos.py` | leitura e validação de `modulos.csv`, `inversores.csv`, `baterias.csv` |
| `selecao.py` | validação das strings, escolha do inversor e da bateria |
| `orcamento.py` | orçamento (`data/outros_custos.csv` para outros custos) |
| `dimensionamento.py` | pipeline completo do cálculo |
| `proposta.py` | texto da proposta e propostas salvas |
| `tests/` | testes automáticos (usam dados fictícios só em memória/pasta temporária) |

## Fórmulas

- E_FV = C_m × f
- P_FV = E_FV / (HSP × D × η)  (kWp)
- N = ⌈P_FV × 1000 / P_módulo⌉ ; P_instalada = N × P_módulo / 1000
- Geração = P_instalada × HSP × D × η
- E_d = C_m / 30 ; E_autonomia = E_d × A / 24 ; C_bat = E_autonomia / (DoD × η_bat)
- N_bat = ⌈C_bat / capacidade nominal da bateria⌉ (C_bat já inclui o DoD; usar a capacidade útil aplicaria o DoD duas vezes)
- C_equipamentos = C_módulos + C_inversor + C_baterias ; C_total = C_equipamentos + outros custos

## Premissas (todas editáveis em `parametros.py`)

| Premissa | Valor | Origem / justificativa |
|---|---|---|
| Consumo de referência | média dos meses cadastrados | (documentar) — o maior consumo pode ser escolhido no menu |
| D (dias do mês) | 30 | aproximação da atividade |
| η (desempenho global) | 0,75 | (documentar a fonte do valor adotado) |
| Fator de Voc a frio | 1,12 | margem típica, na falta do coeficiente de temperatura do datasheet |
| Fator de Vmp a quente | 0,85 | idem |
| Razão FV/CA do inversor | 0,8 a 1,5 | faixa de projeto configurável |
| η da bateria | 0,95 | valor típico, o dataset não traz esse campo |
| Critério de módulo | menor R$/Wp (com inversor compatível) | decisão da equipe |
| Strings | divisão em strings iguais, mais longas primeiro; Isc ≤ corrente máxima por MPPT | simplificação |

## Datasets e fontes

Os CSVs ficam em `data/` e precisam conter **apenas produtos reais**, com `fornecedor`, `data_coleta` e `url_fonte`
(veja `data/LEIAME_dados.md`). Colunas opcionais em `inversores.csv`: `tensao_bateria_min_v` e
`tensao_bateria_max_v` (se preenchidas, a tensão da bateria é validada). `data/outros_custos.csv` guarda estrutura,
cabos, proteções e instalação, cada item com a fonte da premissa.

| Dataset | Fonte | Data da coleta |
|---|---|---|
| hsp.csv | (preencher) | |
| modulos.csv | (preencher) | |
| inversores.csv | (preencher) | |
| baterias.csv | (preencher) | |
| outros_custos.csv | (preencher) | |

## Cenários testados

(Cole aqui o resumo dos cenários gerados por `cenarios.py`, com os arquivos de `evidencias/`.)

## Limitações conhecidas

- Sem coeficientes de temperatura reais, a validação de tensão usa fatores de margem.
- Não considera sombreamento, orientação, inclinação nem perdas específicas do local.
- O gráfico em PNG exige `matplotlib`; sem ele o gráfico em texto continua funcionando.
- A senha mínima passou a ter 8 caracteres (contas antigas continuam entrando e são atualizadas para o hash seguro no primeiro login).
