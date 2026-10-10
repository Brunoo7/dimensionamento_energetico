# Guia para pesquisar os dados dos CSVs

Este guia ajuda a coletar dados **reais e rastreáveis**. Nenhum valor aqui deve ser copiado para os CSVs
sem conferir na fonte: cada linha precisa de `fornecedor` brasileiro, `data_coleta` (AAAA-MM-DD) e `url_fonte`.

## 1. Onde achar cada tipo de dado

| Dado | Onde buscar |
|---|---|
| Especificações elétricas | Datasheet (PDF) no site do fabricante. Anote o link se quiser, mas `url_fonte` deve apontar para a página de **preço** no fornecedor, e o datasheet pode ir na tabela de fontes do README |
| Preço | Loja ou distribuidor que venda no Brasil (página do produto com preço visível). Tire print e anote a data |
| HSP | CRESESB/SunData (informe a localidade e use a média anual da irradiação, em kWh/m²/dia) ou Atlas Brasileiro de Energia Solar. Confirme no site qual plano e qual coluna usar e registre isso na fonte |

## 2. Como ler o datasheet (nomes comuns em inglês)

**Módulo** (`modulos.csv`): `potencia_wp` = Maximum Power (Pmax); `voc_v` = Open Circuit Voltage (Voc);
`isc_a` = Short Circuit Current (Isc); `vmp_v` = Voltage at Pmax (Vmp); `imp_a` = Current at Pmax (Imp);
`eficiencia_pct` = Module Efficiency. Use os valores em condição STC.

**Inversor** (`inversores.csv`): `potencia_nominal_w` = rated AC output power; `potencia_max_fv_w` = max. PV input power
(ou recomendada); `tensao_max_entrada_v` = max. DC input voltage; `faixa_mppt_min_v` e `faixa_mppt_max_v` = MPPT voltage range;
`corrente_max_entrada_a` = max. input current **por MPPT**; `numero_mppt` = number of MPPT; `tipo` = `string` ou `hibrido`;
`compativel_bateria` = `sim` só se o fabricante diz que aceita bateria. Para híbridos, preencha também
`tensao_bateria_min_v` e `tensao_bateria_max_v` (battery voltage range), pois assim a compatibilidade de tensão é verificada.
Atenção: o sistema trata a corrente máxima como valor por MPPT. Se o datasheet dá outro tipo de limite, anote na fonte.

**Bateria** (`baterias.csv`): `tensao_nominal_v` = nominal voltage; `capacidade_ah` = nominal capacity;
`capacidade_kwh` = **nominal** energy (não a energia útil); `dod_pct` = depth of discharge (0 a 100); `ciclos` = cycle life.
O validador exige que `capacidade_kwh` esteja a até 5% de tensão × Ah / 1000.

Exemplo de como um datasheet vira linha de CSV (só para ilustrar o formato, **não inclua sem preço e fornecedor brasileiro**):
um datasheet de bateria que informa tensão nominal 48 V, 100 Ah, 4,8 kWh, DoD 95% e mais de 6000 ciclos vira
`tensao_nominal_v=48`, `capacidade_ah=100`, `capacidade_kwh=4.8`, `dod_pct=95`, `ciclos=6000`.

## 3. Cuidados

- **Confira se o produto ainda é vendido.** Na pesquisa que fiz, vários módulos de um fabricante apareciam no site dele
  como "descontinuados". Dê preferência a itens com preço e estoque visíveis no fornecedor.
- Misture fabricantes e potências, mas inclua pelo menos 2 inversores híbridos (cenário com bateria).
- Garanta que há pelo menos um inversor compatível com os módulos escolhidos (tensão de string e corrente). O `validar_datasets.py`
  verifica o formato, e o `cenarios.py` mostra na prática se a combinação funciona.
- Marcas e linhas frequentemente encontradas no mercado brasileiro (**só para orientar a busca, confirmem disponibilidade e preço**):
  módulos (Canadian Solar, Jinko, Trina, JA Solar, Risen, Longi, DAH, Intelbras); inversores (Growatt, Fronius, WEG, Sungrow,
  Deye, Huawei, GoodWe, Intelbras); baterias de LiFePO4 (Pylontech, BYD, Deye e outras).
- Divida o trabalho (por exemplo, uma pessoa por CSV) e faça revisão cruzada: outra pessoa abre cada link e confere as linhas.

## 4. Antes de entregar

1. `python validar_datasets.py` sem erros e sem pendências.
2. `python cenarios.py --consumo ... --hsp ... --fonte-hsp "..."` gerando os dois cenários sem mensagem de falha.
3. Tabela de fontes do `README.md` preenchida e pasta `evidencias/` no repositório.
