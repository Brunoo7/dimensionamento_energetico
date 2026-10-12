# Verificação de preços e disponibilidade — 12/10/2026

Esta verificação cobre os três componentes do cenário sem bateria/com bateria que aparecem nos exemplos recentes. Preços de vitrine não são orçamento comercial, e estoque/prazo final depende da confirmação da loja e do CEP.

| Componente | Loja e preço consultado | Situação exibida | Tratamento no projeto |
|---|---|---|---|
| Módulo Canadian Solar CS6W-550MS (M01) | Direta Energia Solar: **R$ 449,90** listado na vitrine. [Página do produto](https://www.diretaenergiasolar.com.br/painel-solar-550w-monocristalino-half-cell-canadian-cs6w-550ms/prod-10838858/) | A vitrine lista o modelo exato e oferece compra, mas não mostra quantidade de estoque nem prazo. A [Minha Casa Solar](https://www.minhacasasolar.com.br/painel-solar-550w-monocristalino-half-cell-canadian-cs6w-550ms-82127) mostrava R$ 589,00 no cartão / R$ 547,77 no Pix e **Produto Indisponível**. | Dataset atualizado para o preço de vitrine da Direta Energia Solar; disponibilidade física permanece **não confirmada**. |
| Inversor Deye SUN-3K-G04 P1-EU-AM1 (I08) | Minha Casa Solar: **R$ 1.699,00** no cartão / R$ 1.580,07 no Pix. [Página do produto](https://www.minhacasasolar.com.br/inversor-solar-on-grid-monofasico-3kw-220v-2mppt-deye-afci-sun-3k-g04-84308) | Página indica **PRÉ-VENDA**, prazo de 4 dias úteis sujeito a CEP. O título diz 2 MPPT, mas a descrição/tabela do modelo P1-EU-AM1 indica **1 MPPT**. | Dataset atualizado para preço no cartão e corrente máxima de entrada FV 20 A / curto-circuito 30 A, conforme a tabela técnica. A variante e o prazo precisam de confirmação comercial. |
| Bateria Livoltek BLF-B51100 (B03) | Minha Casa Solar: **R$ 5.375,27** no cartão / R$ 4.999,00 no Pix. [Página do produto](https://www.minhacasasolar.com.br/bateria-solar-de-litio-100ah-5-12kwh-51-2v-livoltek-blf-b51100-83560) | A página mostra selo **PRÉ-VENDA**, prazo de 23 dias úteis, mas também **Produto Indisponível**. | Mantida como referência de preço no dataset, explicitamente marcada como **não disponível para compra imediata**. Não usar em orçamento de compra sem confirmação da loja. |

## Impacto nos orçamentos

Os custos gerados pelo programa são **estimativas acadêmicas** com valores de catálogo. Não devem ser apresentados como orçamento com estoque garantido. O cenário sem bateria foi percorrido pelo menu e a proposta foi salva/reaberta; seus valores são recalculados com o preço atualizado do módulo e do inversor quando a aplicação é executada. O cenário com bateria foi gerado por `cenarios.py`, mas a bateria usada como exemplo aparece indisponível na página consultada.

## Escopo e limitações

O catálogo contém 10 módulos, 8 inversores e 6 baterias. Nesta rodada, a checagem em tempo real foi aprofundada nos três modelos acima, que são os componentes dos cenários demonstrados; os outros registros mantêm fontes e datas de coleta já documentadas nos próprios CSVs, mas **não foram todos reconsultados individualmente em 12/10/2026**. Antes de usar qualquer linha para compra ou orçamento real, abra a fonte correspondente no CSV e confirme preço, estoque, variante, frete e compatibilidade.
