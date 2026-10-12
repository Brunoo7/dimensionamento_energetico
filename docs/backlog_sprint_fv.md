# Product Backlog — Sprint de Evolução Fotovoltaica

Sistema de Dimensionamento Energético Residencial · continuação do backlog da Sprint 1 (PB01 a PB15)

## 1. Visão geral e premissas

O objetivo da sprint é transformar o histórico de consumo já cadastrado em uma **proposta preliminar de sistema fotovoltaico**: consumo de referência, recurso solar (HSP), potência FV, módulos, inversor, baterias opcionais e orçamento, tudo a partir de datasets CSV de equipamentos reais. É um pré-dimensionamento acadêmico, que não substitui projeto elétrico executivo.

Fluxo do produto: **Imóvel → Histórico de consumo → Consumo de referência → HSP → Dimensionamento FV → Seleção e validação de equipamentos → Baterias (opcional) → Orçamento → Proposta preliminar.**

Premissas documentadas no repositório (docs/PREMISSAS_E_FONTES.md), cada uma com origem:

- Consumo de referência padrão: **média** dos meses cadastrados (o máximo continua disponível como alternativa). Recomendado ter 12 meses; com menos de 12, o sistema avisa.
- D = 30 dias. η = 0,75. HSP vem de fonte oficial (CRESESB/SunData), com fonte e data registradas.
- Dados técnicos vêm do datasheet do fabricante. Preços vêm de fornecedores que vendem no Brasil, com `fornecedor`, `data_coleta` e `url_fonte`. Nenhum dado fictício.
- Razão FV/CA do inversor, margens de tensão, corrente e custos "demais" ficam em arquivos de parâmetros, nunca fixos no código.
- Fórmula de baterias: N_bat = ⌈C_bat / capacidade nominal da bateria⌉, com C_bat = E_autonomia / (DoD × η_bat). O DoD já está em C_bat, então não é aplicado de novo no cálculo da quantidade.

## 2. Épicos

| Épico | Nome | Resultado |
|---|---|---|
| E1 | Consumo de referência e integração | Reaproveita imóvel e histórico da Sprint 1 |
| E2 | Localização e recurso solar | HSP por imóvel, com fonte |
| E3 | Base de equipamentos | modulos.csv, inversores.csv, baterias.csv validados |
| E4 | Dimensionamento FV | kWp, módulos, P instalada, geração estimada |
| E5 | Inversor e compatibilidade | Seleção válida, sem combinações incompatíveis |
| E6 | Armazenamento por baterias | Capacidade, quantidade e compatibilidade |
| E7 | Orçamento | Equipamentos, outros custos e total |
| E8 | Proposta ao cliente | Resumo completo, salvo e consultável |
| E9 | Documentação e evidências | Cenários, fontes e reprodução |

## 3. User Stories

Prioridade: A = alta, M = média, B = baixa.

### E1 — Consumo de referência e integração

| ID | User Story | Critérios de aceite | Prior. |
|---|---|---|---|
| PB16 | Como usuário, quero escolher o consumo de referência (média ou máximo) para dimensionar o sistema. | Padrão = média; valor exibido em kWh/mês; histórico 320, 295, 410, 365 e 340 gera média 346,0 e máximo 410,0; com 0 meses, bloqueia com mensagem; com menos de 12 meses, exibe aviso. | A |
| PB17 | Como usuário, quero iniciar o dimensionamento FV a partir de um imóvel já cadastrado, sem redigitar dados. | Lista apenas imóveis do usuário logado; usa o histórico existente; imóvel de outro usuário é recusado (PB15). | A |

### E2 — Localização e recurso solar

| ID | User Story | Critérios de aceite | Prior. |
|---|---|---|---|
| PB18 | Como usuário, quero informar cidade e UF do imóvel para que o sistema encontre o recurso solar. | Cidade e UF obrigatórias; UF deve estar entre as 27 válidas; imóveis já cadastrados continuam acessíveis e são migrados sem perda de dados. | A |
| PB19 | Como usuário, quero que o sistema obtenha o HSP da minha localidade, com a origem exibida. | HSP em kWh/m²/dia lido de tabela (hsp.csv) com fonte e data; valor entre 0 e 8; cidade ausente da tabela permite informar HSP manualmente, com aviso. | A |
| PB20 | Como usuário, quero informar o percentual de atendimento e demais parâmetros do dimensionamento. | f entre 1% e 100%; η entre 0,50 e 0,95 (padrão 0,75); bateria sim/não; autonomia A em horas (maior que 0 e até 48) só quando houver bateria; valores fora da faixa são rejeitados com mensagem. | A |

### E3 — Base de equipamentos

| ID | User Story | Critérios de aceite | Prior. |
|---|---|---|---|
| PB21 | Como equipe, quero o dataset modulos.csv com módulos reais comercializados no Brasil. | Mínimo 10 módulos; campos: id, fabricante, modelo, potencia_wp, voc_v, isc_a, vmp_v, imp_a, eficiencia_pct, preco_brl, fornecedor, data_coleta, url_fonte; unidades padronizadas; cada linha conferida com datasheet e link de preço. | A |
| PB22 | Como equipe, quero inversores.csv com inversores reais. | Mínimo 8 inversores; campos da US (tipo, potencia_nominal_w, potencia_max_fv_w, tensao_max_entrada_v, faixa_mppt_min_v, faixa_mppt_max_v, corrente_max_entrada_a, numero_mppt, compativel_bateria, preco_brl, fornecedor, data_coleta, url_fonte); incluir pelo menos 2 híbridos. | A |
| PB23 | Como equipe, quero baterias.csv com baterias reais. | Mínimo 6 baterias; campos: id, fabricante, modelo, tecnologia, tensao_nominal_v, capacidade_ah, capacidade_kwh, dod_pct, ciclos, preco_brl, fornecedor, data_coleta, url_fonte; capacidade_kwh coerente com tensão × Ah (diferença até 5%). | A |
| PB24 | Como desenvolvedor, quero um carregador que valide os CSVs antes do uso. | Lê os três arquivos; rejeita coluna ausente, valor não numérico, preço menor ou igual a zero e id duplicado; a mensagem informa arquivo e linha; arquivo válido carrega sem erro. | A |

### E4 — Dimensionamento FV

| ID | User Story | Critérios de aceite | Prior. |
|---|---|---|---|
| PB25 | Como usuário, quero que o sistema calcule a energia a gerar e a potência FV necessária. | E_FV = C_m × f; P_FV = E_FV / (HSP × D × η). Exemplo: C_m = 346, f = 100%, HSP = 4,5, D = 30, η = 0,75 resulta em P_FV = 3,417 kWp (tolerância de 0,001). Unidades exibidas em kWh/mês e kWp. | A |
| PB26 | Como usuário, quero que o sistema selecione o módulo e calcule a quantidade e a potência instalada. | N = ⌈P_FV × 1000 / P_módulo⌉; P_instalada = N × P_módulo / 1000; P_instalada ≥ P_FV sempre. Exemplo com módulo de 550 Wp: N = 7 e P_instalada = 3,85 kWp. O critério de escolha (menor R$/Wp) é documentado. | A |
| PB27 | Como usuário, quero ver a geração mensal estimada do sistema instalado. | G = P_instalada × HSP × D × η. Exemplo: 3,85 × 4,5 × 30 × 0,75 = 389,8 kWh/mês; exibir também G / C_m (112,7%). | M |

### E5 — Inversor e compatibilidade

| ID | User Story | Critérios de aceite | Prior. |
|---|---|---|---|
| PB28 | Como usuário, quero que o sistema escolha um inversor tecnicamente adequado, não apenas o mais barato. | Filtra por: P_instalada ≤ potencia_max_fv_w e razão P_instalada / potencia_nominal dentro de faixa configurável (0,5 a 1,5); entre os válidos, escolhe o de menor preço; sem candidato válido, exibe "nenhum inversor compatível" sem erro. | A |
| PB29 | Como usuário, quero que o sistema valide a ligação elétrica módulos–inversor. | Voc do arranjo com margem de segurança ≤ tensao_max_entrada_v; Vmp do arranjo dentro da faixa MPPT; Isc ≤ limite de curto-circuito quando informado; Imp acima da corrente de entrada gera aviso (ou reprova, se o limite de curto-circuito não constar); quantidade de strings por MPPT respeitada; reprovação lista qual regra falhou. | A |
| PB39 | Como usuário, quero que o sistema acrescente módulos, quando necessário, para a ligação respeitar a faixa MPPT do inversor. | Primeiro tenta a quantidade calculada com todos os módulos; só então acrescenta módulos, até um máximo configurável (4); a proposta avisa quantos módulos foram acrescentados e que a geração fica acima do consumo. | M |

### E6 — Armazenamento por baterias

| ID | User Story | Critérios de aceite | Prior. |
|---|---|---|---|
| PB30 | Como usuário, quero informar se desejo bateria e a autonomia, e ver a capacidade necessária. | E_d = C_m / 30; E_autonomia = E_d × A / 24; C_bat = E_autonomia / (DoD × η_bat). Exemplo: C_m = 346, A = 12 h, DoD = 90%, η_bat = 95% resulta em E_d = 11,53 kWh, E_autonomia = 5,77 kWh e C_bat ≈ 6,75 kWh. Sem bateria, nada é calculado. | A |
| PB31 | Como usuário, quero que o sistema selecione baterias compatíveis e a quantidade necessária. | Escolhe bateria do dataset; N_bat = ⌈C_bat / capacidade nominal⌉; capacidade instalada ≥ necessária; exige inversor com compativel_bateria = sim e tensão compatível; se o inversor já escolhido não for compatível, o sistema reseleciona um inversor híbrido e refaz PB28 e PB29, em vez de apenas somar a bateria. | A |

### E7 — Orçamento

| ID | User Story | Critérios de aceite | Prior. |
|---|---|---|---|
| PB32 | Como usuário, quero a soma dos equipamentos selecionados. | C_equipamentos = C_módulos + C_inversor + C_baterias; C_módulos = N × preço; sem bateria, C_baterias = 0; cada linha mostra id, modelo, quantidade, preço unitário e subtotal; o total confere com a soma manual. | A |
| PB33 | Como usuário, quero ver os outros custos separados do preço dos equipamentos. | Estrutura, cabos, proteções e instalação vêm de outros_custos.csv, cada item com fonte; a saída mostra "custo dos equipamentos", "outros custos" e "custo total estimado" em linhas distintas. | M |

### E8 — Proposta ao cliente

| ID | User Story | Critérios de aceite | Prior. |
|---|---|---|---|
| PB34 | Como usuário, quero um resumo da proposta preliminar. | Exibe os 13 itens da atividade: consumo usado, % atendido, energia a gerar, HSP e origem, kWp calculado e instalado, módulos (quantidade, fabricante, modelo), inversor, existência de armazenamento, capacidade calculada e instalada, geração estimada, custo dos equipamentos, outros custos e custo total; inclui o aviso de pré-dimensionamento acadêmico. | A |
| PB35 | Como usuário, quero salvar e consultar propostas anteriores. | Proposta gravada no SQLite com parâmetros, ids e preços usados naquele momento; listagem apenas das propostas do próprio usuário (PB15); reabrir uma proposta mostra os mesmos valores mesmo se o CSV mudar depois. | M |
| PB36 | Como usuário, quero acessar tudo pelo menu existente. | Nova opção no menu logado; fluxo guiado do imóvel até a proposta; entradas inválidas repetem a pergunta sem encerrar o programa. | A |

### E9 — Documentação e evidências

| ID | User Story | Critérios de aceite | Prior. |
|---|---|---|---|
| PB37 | Como equipe, quero cenários de teste com e sem bateria. | Pelo menos 2 cenários (sem bateria e com bateria) com entradas, saídas e conferência manual dos cálculos; testes automatizados dos cálculos e das validações passam. | A |
| PB38 | Como equipe, quero documentar fontes, premissas e como reproduzir os resultados. | README com instalação, execução e cenários; tabela de fontes (HSP, datasheets, fornecedores, data de coleta); premissas (η, D, margens, custos "demais"). | M |

## 4. Tasks (decomposição)

| US | Tasks |
|---|---|
| PB16 | T1 função consumo_de_referencia() em calculos.py; T2 aviso para menos de 12 meses; T3 testes com o exemplo de 346 kWh |
| PB17 | T1 reutilizar escolher_imovel(); T2 checar posse do imóvel; T3 carregar histórico |
| PB18 | T1 adicionar cidade e UF em imoveis; T2 script de migração (ALTER TABLE); T3 atualizar cadastro e validação; T4 testar com banco antigo |
| PB19 | T1 pesquisar HSP (CRESESB ou Atlas) das cidades-alvo; T2 criar hsp.csv com fonte e data; T3 função buscar_hsp(); T4 fallback manual |
| PB20 | T1 tela de parâmetros; T2 validações de faixa; T3 arquivo de parâmetros padrão |
| PB21 a PB23 | T1 pesquisar fabricantes e datasheets; T2 levantar preços em fornecedores; T3 preencher o CSV; T4 revisão cruzada por outro membro; T5 commit dos CSVs |
| PB24 | T1 definir schema; T2 função de leitura; T3 validações com mensagens por linha; T4 testes com CSV inválido |
| PB25 | T1 função calcular_potencia_fv(); T2 testes com o exemplo |
| PB26 | T1 critério de seleção do módulo; T2 função de N e P_instalada; T3 testes de borda (P_FV exato múltiplo do módulo) |
| PB27 | T1 função de geração estimada; T2 exibir cobertura |
| PB28 | T1 definir filtros e razão FV/CA; T2 função de seleção; T3 caso sem candidato |
| PB29 | T1 calcular Voc, Vmp e correntes do arranjo; T2 definir margens de tensão; T3 definir módulos por string; T4 mensagens por regra |
| PB39 | T1 laço de módulos extras com limite configurável; T2 aviso na proposta; T3 testes (sistema pequeno com híbrido) |
| PB30 | T1 funções E_d, E_autonomia e C_bat; T2 decidir e documentar a fórmula de N_bat; T3 testes |
| PB31 | T1 filtrar baterias por tensão e DoD; T2 calcular N_bat; T3 forçar inversor híbrido; T4 refazer PB28 e PB29 |
| PB32 e PB33 | T1 funções de custo por componente; T2 parâmetros de outros custos com fonte; T3 formatação do orçamento; T4 conferência manual |
| PB34 a PB36 | T1 montar o dicionário da proposta; T2 formatar a saída; T3 tabela propostas; T4 gravar e listar; T5 integrar ao main.py |
| PB37 e PB38 | T1 rodar 2 cenários completos; T2 guardar evidências; T3 escrever README e fontes; T4 revisar com checklist da atividade |

## 5. Dependências

| Item | Depende de | Motivo |
|---|---|---|
| PB16 | PB05, PB06, PB09 (Sprint 1) | Média e histórico já existem |
| PB19 | PB18 | O HSP depende de cidade e UF |
| PB21 a PB23 | nenhuma | Pode começar já, em paralelo |
| PB24 | PB21 a PB23 | Valida os CSVs |
| PB25 | PB16, PB19, PB20 | Precisa de C_m, HSP, f e η |
| PB26 | PB25, PB24 | Precisa de P_FV e do dataset de módulos |
| PB27 | PB26, PB19 | Usa P_instalada e HSP |
| PB28 | PB26, PB24 | Precisa de P_instalada e do dataset de inversores |
| PB29 | PB26, PB28 | Valida o arranjo contra o inversor |
| PB39 | PB26, PB28, PB29 | Ajusta a quantidade de módulos à ligação |
| PB30 | PB16, PB20 | Precisa de C_m e da autonomia |
| PB31 | PB30, PB23, PB28 | Bateria depende do inversor compatível |
| PB32 | PB26, PB28, PB31 (se houver bateria) | Orçamento usa o que foi selecionado |
| PB33 | PB32 | Soma ao total |
| PB34 | PB27, PB29, PB33 | Resumo reúne tudo |
| PB35, PB36 | PB34 | Salvar e integrar o fluxo |
| PB37, PB38 | PB34 | Cenários só depois da proposta |

Caminho crítico: PB21 a PB24 → PB25 → PB26 → PB28 e PB29 → PB31 → PB32 → PB34.

## 6. Kanban

| A fazer | Em andamento | Em revisão | Concluído |
|---|---|---|---|
| Conferir links dos dados pesquisados; completar 2 módulos; colar documentação no README; exportar este backlog | PB21 (módulos 8 de 10); evidências do SunData | PB22, PB23 e PB33 (conferir links e preços) | PB16 a PB20, PB24 a PB32, PB34 a PB37, PB39 e as pendências da Sprint 1 |

O Kanban completo, card a card, está em docs/KANBAN_SPRINT_FV.csv.

## 7. Status da implementação

O código e os testes automáticos da sprint estão no repositório, e os cenários sem e com bateria foram gerados (consumo de referência simulado de 160 kWh/mês). Falta conferir os links dos dados pesquisados, completar 2 módulos, colar a documentação no README e exportar este backlog em PDF.

| Itens | Status | Onde |
|---|---|---|
| PB16 a PB20 | Implementado | calculos.py, imovel.py, solar.py, parametros.py, main.py |
| PB21 a PB23 | Em andamento: inversores (8 de 8) e baterias (6 de 6) preenchidos, módulos 8 de 10; falta conferir os links | data/ |
| PB24 | Implementado | equipamentos.py, validar_datasets.py |
| PB25 a PB27 | Implementado | calculos.py, dimensionamento.py |
| PB28, PB29 e PB39 | Implementado | selecao.py, dimensionamento.py |
| PB30 e PB31 | Implementado | calculos.py, selecao.py |
| PB32 e PB33 | Implementado; outros custos com fonte em outros_custos.csv | orcamento.py |
| PB34 a PB36 | Implementado | proposta.py, main.py |
| PB37 | Implementado com consumo simulado | cenarios.py, evidencias/ |
| PB38 | Parcial: textos prontos em docs/PREMISSAS_E_FONTES.md, falta colar no README | README.md, docs/ |
| PB04, PB07, PB10, PB12 (Sprint 1) | Implementado | imovel.py, grafico.py, main.py |
| Senha com PBKDF2 e sal (melhoria de segurança) | Implementado | usuario.py |

*Pré-dimensionamento acadêmico e estimativa de custos; não substitui projeto elétrico executivo, responsabilidade técnica ou análise de profissional habilitado.*
