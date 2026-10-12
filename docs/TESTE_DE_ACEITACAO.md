# Verificação de aceitação — rodada de 12/10/2026

Este documento separa verificações reproduzíveis nesta entrega de ações manuais que ainda dependem de uma pessoa percorrer o menu. Não marque como manualmente concluído algo coberto apenas por testes unitários.

## Resultados reproduzidos nesta rodada

| Verificação | Resultado | Evidência |
|---|---|---|
| Suíte automatizada | **85 aprovados** | `python -m pytest -q` |
| Compilação dos módulos principais | **Aprovada** | `python -m py_compile ...` |
| Estrutura dos datasets | **Aprovada** | `python validar_datasets.py`: 10 módulos, 8 inversores, 6 baterias e 1 localidade HSP |
| Cenários com e sem bateria | **Executados** | `evidencias/cenario_sem_bateria.txt` e `evidencias/cenario_com_bateria.txt` |
| Propostas e valores de orçamento | **Evidências regeneradas** | Os arquivos acima refletem os CSVs atuais, com preços consultados em 12/10/2026 |
| Interface/fluxos interativos completos | **Pendente** | Não foi possível comprovar todos os fluxos por interação manual nesta rodada |
| Estoque de todos os equipamentos | **Não confirmado** | A consulta aprofundada foi limitada aos modelos indicados em `VERIFICACAO_PRECOS_DISPONIBILIDADE_2026-10-12.md` |
| Publicação no GitHub | **Pendente** | Esta entrega local não faz push para o repositório remoto |

## Roteiro manual ainda necessário

- [ ] Cadastrar usuário e confirmar rejeição de e-mail duplicado e senha inválida.
- [ ] Entrar com credenciais válidas e confirmar rejeição de senha incorreta.
- [ ] Cadastrar, editar e excluir imóvel, incluindo cancelamento da confirmação.
- [ ] Registrar consumos em meses diferentes e conferir ordem cronológica, média, máximo e mês correspondente.
- [ ] Com dois usuários, tentar consultar, alterar e excluir imóvel/consumo/proposta por ID cruzado.
- [ ] Gerar proposta com e sem bateria pelo menu, salvar e consultar propostas.
- [ ] Fechar e reabrir o programa e confirmar persistência no SQLite.
- [ ] Testar migração com cópia de um banco antigo sem as colunas `cidade` e `uf`.
- [ ] Fazer revisão elétrica por profissional habilitado antes de usar qualquer dimensionamento em instalação real.

## Limitações

Os testes automatizados não substituem a verificação manual da experiência de uso. Preços de catálogo não são cotação comercial, estoque, frete ou prazo garantido. O dimensionamento é preliminar e não substitui projeto executivo.
