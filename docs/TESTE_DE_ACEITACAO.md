# Roteiro de teste de aceitação manual

Executado em 12/10/2026 no terminal, usando cópia isolada do projeto, banco SQLite temporário e dois usuários fictícios (QA Usuário A/B). Nenhum dado de teste foi gravado no banco entregue.

| ID | Ação | Resultado esperado | Status nesta entrega |
|---|---|---|---|
| TA01 | Cadastrar usuário válido e entrar | Cadastro concluído e login autorizado | **Verificado manualmente:** dois usuários cadastrados e login do usuário A e B concluído |
| TA02 | E-mail duplicado e credenciais inválidas | Mensagem de validação; login não autorizado | Cobertura automatizada; fluxo negativo não percorrido manualmente nesta rodada |
| TA03 | Cadastrar, editar e excluir imóvel | Operações concluídas com confirmação de exclusão | **Cadastro verificado manualmente**; edição/exclusão cobertas por testes automatizados, não percorridas no menu nesta rodada |
| TA04 | Inserir consumo em vários meses | Histórico cronológico, média e maior consumo/mês corretos | **Verificado manualmente:** 150 kWh em jan/2026 e 170 kWh em fev/2026; histórico e resumo exibidos; média esperada de 160 kWh/mês |
| TA05 | Acessar dados de outro usuário | Dados de outro usuário não aparecem nem podem ser acessados | **Verificado manualmente para listagem:** usuário B não viu o imóvel nem as propostas do usuário A; bloqueios por ID também cobertos por testes automatizados |
| TA06 | Gerar proposta sem bateria | Cálculo, avisos, orçamento e persistência funcionam | **Verificado manualmente no menu:** proposta gerada, salva e reaberta na mesma sessão |
| TA07 | Gerar proposta com bateria | Compatibilidade, autonomia estimada, orçamento e persistência funcionam | Cenário de linha de comando executado; ainda não percorrido pelo menu interativo nesta rodada |
| TA08 | Encerrar e reabrir o sistema | Dados persistem no SQLite | Cobertura automatizada; reabertura após reiniciar o programa não foi executada nesta rodada |
| TA09 | Validar CSVs | Sem erros estruturais e quantidades mínimas cumpridas | Executado; sem erros estruturais |
| TA10 | Executar suíte completa | Todos os testes passam | Executado; 85 testes aprovados |

## Limites da verificação

- O fluxo manual usou dados fictícios e um diretório temporário; não alterou o banco original do projeto.
- O isolamento foi verificado pela ausência de imóveis e propostas do usuário A ao entrar como usuário B. A proteção de operações diretas por ID está também coberta por testes automatizados.
- Preços e disponibilidade de lojas são fotografias de páginas consultadas em 12/10/2026; podem mudar, e frete/prazo dependem do CEP.
