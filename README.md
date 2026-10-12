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
python cenarios.py --consumo 160 --hsp 4.65 --fonte-hsp "CRESESB/SunData; São Paulo/SP; evidência registrada" --cidade "São Paulo" --uf SP --percentual 100 --autonomia 12 --nota "Consumo simulado para demonstração acadêmica; não é consumo medido de imóvel real."
```

`cenarios.py` gera `evidencias/cenario_sem_bateria.txt` e `evidencias/cenario_com_bateria.txt`.
Use o consumo e o HSP do imóvel de teste. Nos cenários entregues, o consumo é simulado; veja a seção de cenários e `docs/PREMISSAS_E_FONTES.md`.

## Fluxo do produto

Imóvel (cidade/UF) → histórico de consumo → consumo de referência → HSP → potência FV → módulos →
inversor e strings (com módulos extras, se preciso) → baterias (opcional) → orçamento → proposta (salva no banco).

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
| `docs/` | premissas e fontes, backlog da sprint (Markdown e PDF) e Kanban em CSV |
| `evidencias/` | evidências do SunData e dos cenários com e sem bateria |
| `tests/` | testes automáticos (usam dados fictícios só em memória/pasta temporária) |

## Fórmulas

- E_FV = C_m × f
- P_FV = E_FV / (HSP × D × η)  (kWp)
- N = ⌈P_FV × 1000 / P_módulo⌉ ; P_instalada = N × P_módulo / 1000
- Geração = P_instalada × HSP × D × η
- E_d = C_m / 30 ; E_autonomia = E_d × A / 24 ; C_bat = E_autonomia / (DoD × η_bat)
- N_bat = ⌈C_bat / capacidade nominal da bateria⌉ (C_bat já inclui o DoD; usar a capacidade útil aplicaria o DoD duas vezes)
- C_equipamentos = C_módulos + C_inversor + C_baterias ; C_total = C_equipamentos + outros custos

## Premissas e justificativas técnicas

### Fator de desempenho global (η = 0,75)
Adotou-se η = 0,75 como fator de desempenho global (Performance Ratio) do sistema. Ele agrupa, de forma simplificada, perdas por temperatura, sujeira, sombreamento parcial, descasamento entre módulos, queda de tensão nos cabos e eficiência de conversão do inversor. O valor é **conservador** em relação a estudos brasileiros de sistemas conectados à rede, que medem PR em torno de 80%: dissertação da UTFPR (Paraná, 2020), com PR médio estimado próximo de 80%, e artigo do CBENS, com PR de 80,29% em um sistema analisado. É uma premissa de pré-dimensionamento; em projeto real o PR deve ser calculado com dados do local e dos equipamentos.
Referência técnica geral: PINHO, João Tavares; GALDINO, Marco Antonio (org.). *Manual de Engenharia para Sistemas Fotovoltaicos*. 2. ed. Rio de Janeiro: CEPEL/CRESESB, 2014. Disponível em: https://cresesb.cepel.br/publicacoes/download/Manual_de_Engenharia_FV_2014.pdf. A referência é indicada como leitura geral; não se atribui a ela uma página específica para a escolha do fator η = 0,75.

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
| `modulos.csv` | Lojas: Minha Casa Solar, Eletrotrafo, Direta Energia Solar, Buyers Energy e Stentor do Brasil. Fichas: páginas dos fornecedores e datasheets de fabricantes, distribuidora Techlux (Ronma) e registro INMETRO | O CSV tem 10 registros. O M01 aponta para a página individual do produto na Direta Energia Solar. M09/M10 e demais itens devem ter preço, estoque, variante e eventuais condições de compra reconfirmados antes de orçamento real |
| `inversores.csv` | Lojas: Minha Casa Solar e Neosolar. Fichas: página da loja e site da Deye (série SG04LP1) | Alguns itens estavam em pré-venda ou indisponíveis (ver coluna `observacao`) |
| `baterias.csv` | Lojas: MeuGerador, Energy Shop e Minha Casa Solar. Ficha da Deye no site do fabricante | Livoltek e Unipower estavam em pré-venda |
| `outros_custos.csv` | SGV Solar, Shopuruara, Energy Shop e artigo de mercado (larpontual.com.br) | Instalação é estimativa de referência |
| Consumo de referência dos cenários | Entrada simulada de 160 kWh/mês, escolhida para demonstrar o funcionamento do sistema | Não é consumo medido nem média oficial atribuída à EPE. Substituir pelo consumo do imóvel quando houver dados reais |

## Cenários testados
Entradas comuns: consumo de referência **simulado** de 160 kWh/mês (valor escolhido na ordem de grandeza do consumo residencial médio brasileiro; não é consumo medido de um imóvel real nem média oficial atribuída à EPE), atendimento de 100%, HSP de 4,65 kWh/m²/dia (CRESESB/SunData, São Paulo/SP, 24°, média anual), η = 0,75. Resultados completos em `evidencias/cenario_sem_bateria.txt` e `evidencias/cenario_com_bateria.txt`.

| Item | Cenário A (sem bateria) | Cenário B (com bateria, 12 h) |
|---|---|---|
| Potência FV calculada | 1,529 kWp | 1,529 kWp |
| Módulos | 3 × Canadian Solar CS6W-550MS | 5 × Canadian Solar CS6W-550MS (2 a mais, para a faixa MPPT do inversor) |
| Potência instalada | 1,650 kWp | 2,750 kWp |
| Inversor | Deye SUN-3K-G04P1-EU-AM1 (string) | Deye SUN-5K-SG04LP1-EU (híbrido) |
| Armazenamento | não | 1 × Livoltek BLF-B51100 (5,12 kWh nominais; necessário 3,12 kWh) |
| Geração estimada | 172,6 kWh/mês (107,9%) | 287,7 kWh/mês (179,8%) |
| Custo dos equipamentos | R$ 3.048,70 | R$ 14.512,55 |
| Outros custos | R$ 2.513,00 | R$ 3.723,00 |
| **Custo total estimado** | **R$ 5.561,70** | **R$ 18.235,55** |

Observação sobre o cenário B: a geração estimada fica em 179,8% do consumo porque o inversor híbrido de 5 kW exige strings com tensão acima do início da faixa MPPT (150 V), o que obrigou a acrescentar 2 módulos. O custo do cenário B é, portanto, inflado por essa limitação do inversor escolhido, e não só pela bateria.

Outras observações: os preços dependem da confirmação dos links (alguns itens estavam em pré-venda ou indisponíveis); o consumo é simulado e deve ser substituído pelo de um imóvel real, se houver. Os valores da tabela foram regenerados a partir dos CSVs incluídos em 12/10/2026; consulte as evidências para os subtotais atualizados.

## Limitações conhecidas
- Preços e disponibilidade de loja variam; as consultas valem para as datas indicadas.
- A validação elétrica é simplificada (margens de tensão e de corrente) e não substitui projeto executivo.
- Não considera sombreamento, orientação, inclinação específica do telhado nem perdas do local.


## Situação da validação da entrega (12/10/2026)

- Suíte automatizada: 85 testes aprovados nesta cópia (`python -m unittest discover -s tests -t .`).
- Validação estrutural: 10 módulos, 8 inversores, 6 baterias e 1 localidade HSP aprovados (`python validar_datasets.py`).
- Cenários: arquivos com e sem bateria presentes em `evidencias/`; o consumo de 160 kWh/mês é simulado.
- Pendências: roteiro manual em `docs/TESTE_DE_ACEITACAO.md`, conferência individual dos preços/estoques restantes e publicação final no GitHub. Os status detalhados estão em `docs/KANBAN_SPRINT_FV.csv`.

## Checklist de aceitação manual antes da apresentação

Os testes automatizados cobrem funções e casos de regressão, mas a equipe também deve percorrer o fluxo de interface no terminal. Use uma base de teste separada e dados não reais.

- [ ] Cadastrar usuário e confirmar rejeição de e-mail duplicado/senha inválida.
- [ ] Entrar com credenciais válidas e confirmar rejeição de senha incorreta.
- [ ] Cadastrar imóvel, editar os dados e excluir somente após confirmação.
- [ ] Registrar consumos em meses diferentes e verificar ordenação cronológica, média, máximo e mês correspondente.
- [ ] Conferir que um usuário não lista, consulta, edita nem exclui imóvel, consumo ou proposta de outro usuário.
- [ ] Executar o dimensionamento com e sem bateria e conferir avisos de compatibilidade, custos e proposta salva.
- [ ] Fechar e reabrir o programa e confirmar persistência dos registros.
- [ ] Validar os CSVs e executar toda a suíte de testes antes de gerar o ZIP final.

O checklist acima é um roteiro de aceitação para a equipe; itens não marcados não devem ser apresentados como verificados manualmente.
