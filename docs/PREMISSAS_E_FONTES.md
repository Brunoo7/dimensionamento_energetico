# Premissas técnicas, fontes e cenários

Este documento registra as escolhas simplificadas adotadas no protótipo acadêmico. Não é um memorial de cálculo executivo.

## Premissas e justificativas

### Fator de desempenho global (η = 0,75)

O protótipo usa η = 0,75 como fator global simplificado para representar perdas de temperatura, sujeira, cabos, descasamento e conversão. É uma premissa de simulação, não um valor medido para um imóvel específico. Em projeto real, o desempenho deve ser estimado com dados do local e dos equipamentos.

Referência técnica para fundamentação geral: PINHO, João Tavares; GALDINO, Marco Antonio (org.). *Manual de Engenharia para Sistemas Fotovoltaicos*. 2. ed. Rio de Janeiro: CEPEL/CRESESB, 2014. Disponível em: https://cresesb.cepel.br/publicacoes/download/Manual_de_Engenharia_FV_2014.pdf. O manual é referência de consulta geral; não se atribui a ele um número de página específico para a escolha de η = 0,75.

### Margens de tensão (1,12 e 0,85)

O dataset não armazena coeficientes de temperatura específicos para todos os módulos. O programa aplica, portanto, margens fixas aproximadas:

- Voc a frio = módulos em série × Voc × 1,12.
- Vmp a quente = módulos em série × Vmp × 0,85.

São regras simplificadas de triagem, não valores normativos nem substitutos do cálculo com temperaturas de projeto e coeficientes do datasheet.

### Corrente e potência do inversor

- Quando há limite de corrente de curto-circuito declarado no dataset, ele é usado na validação de Isc do arranjo.
- Quando esse limite não está disponível, a rotina adota uma verificação conservadora com os dados disponíveis.
- A razão FV/CA permitida pelo programa é configurável em `parametros.py`.

A compatibilidade calculada deve ser conferida contra o manual exato do inversor, incluindo número de MPPTs, corrente por entrada, limites de tensão e regras do fabricante.

### Módulos extras

Se a string calculada não alcança a faixa MPPT de uma opção de inversor, o programa tenta acrescentar módulos até o limite definido em `parametros.py`. Isso pode aumentar a geração estimada acima do consumo de referência e deve ser destacado na proposta.

### Baterias

O cálculo de capacidade usa a profundidade de descarga informada no dataset e η_bat = 0,95 como premissa simplificada. A autonomia estimada não garante o atendimento de cargas de pico, partida de motores ou perfil horário real; estes fatores exigem dimensionamento específico.

### Outros custos

Os itens vêm de `data/outros_custos.csv`. A mão de obra, projeto, ART e homologação são valores de referência, não cotações formais; o custo real depende do imóvel, da distribuidora e do escopo contratado.

## Fontes dos datasets

| Dataset | Fonte registrada | Limitação conhecida |
|---|---|---|
| `hsp.csv` | CRESESB/SunData; consulta para São Paulo/SP, plano inclinado e média anual; evidência em `evidencias/sundata_sao_paulo_2026-10-11.txt` | HSP depende de coordenadas, inclinação, orientação e base consultada. O registro de São Paulo não deve ser aplicado automaticamente a outra cidade. |
| `modulos.csv` | URLs de fornecedores e fichas técnicas identificadas por linha | M09 e M10 completam a quantidade mínima, mas a consulta registrada apontava indisponibilidade; M10 também tinha quantidade mínima de compra. Preços/estoque precisam ser reconfirmados. |
| `inversores.csv` | URLs de lojas e fabricante identificadas por linha | Alguns itens tinham ressalvas de estoque ou divergências comerciais. Confirmar datasheet e variante exata. |
| `baterias.csv` | URLs de fornecedores e fabricante identificadas por linha | Alguns itens tinham ressalvas de pré-venda/disponibilidade. Confirmar tensão, energia útil, corrente e compatibilidade. |
| `outros_custos.csv` | Fonte e observação por item | Estimativas de material e instalação não equivalem a orçamento de fornecedor. |

As datas nos CSVs refletem as consultas anotadas em 11 e 12 de outubro de 2026. Não foi possível garantir que todos os preços e estoques permaneçam vigentes; verifique cada link antes de usar valores fora da demonstração acadêmica.

## Cenários reproduzíveis

Os arquivos `evidencias/cenario_sem_bateria.txt` e `evidencias/cenario_com_bateria.txt` foram gerados com estas entradas: consumo simulado de 160 kWh/mês, HSP de 4,65 kWh/m²/dia para São Paulo/SP, atendimento de 100%, η = 0,75 e autonomia de 12 horas no cenário com bateria. O consumo de 160 kWh/mês é deliberadamente uma entrada de demonstração; não é consumo medido nem uma média oficial atribuída à EPE.

Para regenerar as evidências a partir da raiz do projeto:

```bash
python cenarios.py --consumo 160 --hsp 4.65 --fonte-hsp "CRESESB/SunData; São Paulo/SP; consulta registrada em evidencias" --cidade "São Paulo" --uf SP --percentual 100 --autonomia 12 --nota "Consumo simulado para demonstração acadêmica; não é consumo medido de imóvel real."
```

## Limitações conhecidas

- Não modela em detalhe orientação/inclinação real, sombras, perfil horário, temperatura de projeto, cabos, proteções, aterramento, estrutura do telhado nem todas as regras da distribuidora.
- O cálculo elétrico usa margens simplificadas e depende da completude dos dados dos equipamentos.
- Preços, estoque, frete e condições comerciais mudam.
- A proposta é estimativa preliminar e não substitui projeto elétrico, ART, homologação ou avaliação de profissional habilitado.


## Estado da verificação comercial (12/10/2026)

O preenchimento do CSV não significa que todos os produtos estejam disponíveis para compra imediata. A conferência aprofundada desta rodada cobriu os três modelos utilizados nos cenários (módulo M01, inversor I08 e bateria B03). Os demais preços, variantes e estoques não foram todos reconfirmados individualmente nesta data. O campo `url_fonte` de M01 ainda aponta para a página inicial da Direta Energia Solar, não para uma página individual do produto; portanto, sua rastreabilidade de preço deve ser melhorada. Consulte `docs/VERIFICACAO_PRECOS_DISPONIBILIDADE_2026-10-12.md` antes de interpretar os valores como orçamento.
