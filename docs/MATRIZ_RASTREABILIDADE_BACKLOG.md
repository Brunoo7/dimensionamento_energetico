# Matriz de rastreabilidade — Product Backlog

Auditoria estática da cópia entregue em 12/10/2026, combinada com a suíte automatizada (85 testes aprovados), compilação dos módulos principais e validação dos CSVs. “Implementado — validar manualmente” significa que há código correspondente, mas a aceitação completa por interação ainda não foi demonstrada nesta rodada.

## Backlog principal PB01–PB15

| Requisito | Evidência de implementação | Avaliação |
|---|---|---|
| PB01 Cadastro | `usuario.py`: validação de nome/e-mail/senha, hash PBKDF2 com salt | Implementado; validar fluxo manual |
| PB02 Login | `usuario.py`: validação de credenciais e mensagem genérica de erro | Implementado; validar fluxo manual |
| PB03 Cadastro de imóvel | `imovel.py`: nome, tipo, cidade/UF e endereço opcional | Implementado |
| PB04 Editar/excluir imóvel | `imovel.py`; confirmação de exclusão em `main.py` | Implementado; validar manualmente |
| PB05 Consumo mensal | `consumo.py`: kWh e validação | Implementado |
| PB06 Histórico multi-mês | `consumo.py`: chave única imóvel/mês/ano e atualização do registro existente | Implementado |
| PB07 Histórico cronológico | Consulta ordenada por ano e mês e exibida em `main.py` | Implementado |
| PB08 Máximo mensal | `calculos.py` | Implementado |
| PB09 Média mensal | `calculos.py` | Implementado |
| PB10 Mês do máximo | Resumo relaciona máximo aos registros de mês/ano em `main.py` | Implementado |
| PB11 Resumo energético | `calculos.py` e `main.py` | Implementado |
| PB12 Gráfico | `grafico.py`: gráfico no terminal e PNG opcional | Implementado |
| PB13 Validações | `usuario.py`, `imovel.py`, `consumo.py` e parâmetros | Implementado; validar entradas pelo menu |
| PB14 Persistência | SQLite em `dados.py` | Implementado; reinício manual pendente |
| PB15 Isolamento | consultas e operações verificam proprietário do imóvel; propostas filtradas por usuário | Implementado em código; teste manual completo pendente |

## Sprint FV PB16–PB39

| Requisito(s) | Evidência | Avaliação |
|---|---|---|
| PB16–PB20 | `calculos.py`, `main.py`, `parametros.py`, `solar.py`, `dados.py` | Implementados em código; migração de banco antigo e fluxos manuais pendentes |
| PB21–PB23 | `data/modulos.csv`, `data/inversores.csv`, `data/baterias.csv` | Quantidades mínimas atendidas: 10, 8 e 6; nem todos os preços/estoques foram reconfirmados individualmente |
| PB24 | `equipamentos.py`, `validar_datasets.py` | Validação executada sem erros estruturais |
| PB25–PB27 | `calculos.py`, `dimensionamento.py` | Fórmulas e cenários executados |
| PB28–PB29 | `selecao.py`, `parametros.py` | Seleção/validação elétrica simplificada implementada; não substitui validação executiva |
| PB30–PB31 | `calculos.py`, `selecao.py`, `dimensionamento.py` | Bateria opcional e compatibilidade implementadas; cenário gerado |
| PB32–PB33 | `orcamento.py`, `data/outros_custos.csv` | Orçamento calculado; preços e outros custos são estimativas |
| PB34–PB35 | `proposta.py`, tabela `propostas` em `dados.py` | Proposta formatada e persistida em JSON; reabertura após reinício pendente de teste manual |
| PB36 | `main.py` | Menu guiado implementado; percurso manual completo pendente |
| PB37 | `cenarios.py`, `evidencias/`, `tests/` | Dois cenários reproduzidos e 85 testes aprovados |
| PB38 | `README.md`, `docs/PREMISSAS_E_FONTES.md` | Documentação presente; valores de cenário atualizados nesta entrega |
| PB39 | `dimensionamento.py`, `selecao.py`, `parametros.py` | Tentativa de adicionar módulos para faixa MPPT, com limite configurável; validado pelos testes existentes |

## Pontos de atenção antes de declarar o trabalho integralmente aceito

1. Percorrer manualmente o checklist em `docs/TESTE_DE_ACEITACAO.md`.
2. Reconfirmar cada preço/estoque e variante de produto antes de uso comercial.
3. Validar com profissional habilitado a configuração elétrica real; as margens de tensão são premissas simplificadas.
4. Publicar a versão final no GitHub, se isso fizer parte da entrega acadêmica.
