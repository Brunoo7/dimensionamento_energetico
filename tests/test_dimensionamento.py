"""Testes de seleção (PB28/29/31), orçamento (PB32/33), pipeline e propostas (PB34/35).

ATENÇÃO: todos os equipamentos abaixo são FICTÍCIOS e existem só para testar a
lógica. Não fazem parte dos datasets do projeto.
"""

import os
import tempfile
import unittest

import dados
import dimensionamento
import equipamentos
import imovel
import orcamento
import proposta
import selecao

MODULO = {"id": "M1", "fabricante": "FabX", "modelo": "Mod550", "potencia_wp": 550.0, "voc_v": 49.5,
          "isc_a": 14.0, "vmp_v": 41.5, "imp_a": 13.3, "eficiencia_pct": 21.3, "preco_brl": 605.0}

INV_STRING = {"id": "I1", "fabricante": "FabZ", "modelo": "Str3k", "tipo": "string", "potencia_nominal_w": 3000.0,
              "potencia_max_fv_w": 4500.0, "tensao_max_entrada_v": 600.0, "faixa_mppt_min_v": 80.0,
              "faixa_mppt_max_v": 550.0, "corrente_max_entrada_a": 16.0, "numero_mppt": 2.0,
              "compativel_bateria": "nao", "preco_brl": 3000.0,
              "tensao_bateria_min_v": None, "tensao_bateria_max_v": None}

INV_HIBRIDO = {**INV_STRING, "id": "I2", "modelo": "Hib3.6k", "tipo": "hibrido", "potencia_nominal_w": 3600.0,
               "potencia_max_fv_w": 5400.0, "compativel_bateria": "sim", "preco_brl": 6000.0,
               "tensao_bateria_min_v": 40.0, "tensao_bateria_max_v": 60.0}

INV_PEQUENO = {**INV_STRING, "id": "I3", "modelo": "Str2k", "potencia_nominal_w": 2000.0,
               "potencia_max_fv_w": 3000.0, "preco_brl": 2000.0}   # barato, mas não aguenta 3,85 kWp

BAT = {"id": "B1", "fabricante": "FabY", "modelo": "Bat5", "tecnologia": "LiFePO4", "tensao_nominal_v": 51.2,
       "capacidade_ah": 100.0, "capacidade_kwh": 5.12, "dod_pct": 90.0, "ciclos": 6000.0, "preco_brl": 9000.0}
BAT_24V = {**BAT, "id": "B2", "tensao_nominal_v": 25.6, "capacidade_kwh": 2.56, "preco_brl": 4000.0}

ENTRADA = dict(consumo_ref_kwh=346.0, hsp=4.5, fracao=1.0, eta=0.75)


class TesteStrings(unittest.TestCase):
    def test_sete_modulos_em_serie_sao_validos(self):
        ok, cfg = selecao.configurar_strings(MODULO, INV_STRING, 7)
        self.assertTrue(ok)
        self.assertEqual((cfg["modulos_em_serie"], cfg["strings"]), (7, 1))
        self.assertAlmostEqual(cfg["voc_frio_v"], 388.0, places=0)

    def test_tensao_acima_do_maximo_e_reprovada_com_motivo(self):
        inv = {**INV_STRING, "tensao_max_entrada_v": 300.0}
        ok, motivos = selecao.configurar_strings(MODULO, inv, 7)
        self.assertFalse(ok)
        self.assertTrue(any("Voc" in m for m in motivos))

    def test_corrente_acima_do_maximo(self):
        inv = {**INV_STRING, "corrente_max_entrada_a": 10.0}
        ok, motivos = selecao.configurar_strings(MODULO, inv, 7)
        self.assertFalse(ok)
        self.assertTrue(any("corrente" in m for m in motivos))

    def test_divide_em_strings_quando_nao_cabe_tudo_em_serie(self):
        inv = {**INV_STRING, "tensao_max_entrada_v": 300.0, "faixa_mppt_min_v": 60.0}
        ok, cfg = selecao.configurar_strings(MODULO, inv, 8)   # 4 em série × 2 strings
        self.assertTrue(ok)
        self.assertEqual((cfg["modulos_em_serie"], cfg["strings"]), (4, 2))


class TesteInversor(unittest.TestCase):
    def test_escolhe_o_mais_barato_entre_os_validos(self):
        inv, cfg, rej = selecao.selecionar_inversor(MODULO, 7, [INV_HIBRIDO, INV_STRING, INV_PEQUENO])
        self.assertEqual(inv["id"], "I1")
        self.assertIn("I3", rej)                      # barato, mas reprovado por potência
        self.assertTrue(any("máximo do inversor" in m for m in rej["I3"]))

    def test_com_bateria_exige_inversor_compativel(self):
        inv, _, rej = selecao.selecionar_inversor(MODULO, 7, [INV_STRING, INV_HIBRIDO], exigir_bateria=True)
        self.assertEqual(inv["id"], "I2")
        self.assertIn("I1", rej)

    def test_sem_inversor_valido(self):
        inv, cfg, rej = selecao.selecionar_inversor(MODULO, 7, [INV_PEQUENO])
        self.assertIsNone(inv)
        self.assertIsNone(cfg)


class TesteBateria(unittest.TestCase):
    def test_quantidade_e_capacidades(self):
        escolha, _ = selecao.selecionar_bateria(5.767, [BAT], INV_HIBRIDO)
        self.assertEqual(escolha["quantidade"], 2)
        self.assertAlmostEqual(escolha["capacidade_necessaria_kwh"], 6.745, places=3)
        self.assertAlmostEqual(escolha["capacidade_instalada_kwh"], 10.24, places=2)
        self.assertGreaterEqual(escolha["capacidade_instalada_kwh"], escolha["capacidade_necessaria_kwh"])
        self.assertTrue(escolha["tensao_verificada"])

    def test_tensao_incompativel_e_excluida(self):
        escolha, _ = selecao.selecionar_bateria(5.767, [BAT_24V, BAT], INV_HIBRIDO)   # 25,6 V fora de 40-60 V
        self.assertEqual(escolha["bateria"]["id"], "B1")

    def test_nenhuma_compativel(self):
        escolha, motivos = selecao.selecionar_bateria(5.767, [BAT_24V], INV_HIBRIDO)
        self.assertIsNone(escolha)
        self.assertTrue(motivos)

    def test_sem_faixa_de_tensao_no_inversor_avisa(self):
        inv = {**INV_HIBRIDO, "tensao_bateria_min_v": None, "tensao_bateria_max_v": None}
        escolha, _ = selecao.selecionar_bateria(5.767, [BAT], inv)
        self.assertFalse(escolha["tensao_verificada"])


class TesteOrcamento(unittest.TestCase):
    def test_sem_bateria_soma_manual(self):
        orc = orcamento.calcular_orcamento(MODULO, 7, INV_STRING, 3.85)
        self.assertAlmostEqual(orc["custo_modulos"], 4235.0)
        self.assertEqual(orc["custo_baterias"], 0.0)
        self.assertAlmostEqual(orc["custo_equipamentos"], 7235.0)
        self.assertAlmostEqual(orc["custo_total"], 7235.0)
        self.assertFalse(orc["outros_considerados"])

    def test_outros_custos_separados_do_preco_dos_equipamentos(self):
        outros = [{"item": "Estrutura", "tipo": "percentual", "valor": 10.0, "fonte": "teste"},
                  {"item": "Cabos", "tipo": "por_kwp", "valor": 100.0, "fonte": "teste"},
                  {"item": "Mão de obra", "tipo": "fixo", "valor": 500.0, "fonte": "teste"}]
        orc = orcamento.calcular_orcamento(MODULO, 7, INV_STRING, 3.85, None, outros)
        self.assertAlmostEqual(orc["custo_equipamentos"], 7235.0)
        self.assertAlmostEqual(orc["custo_outros"], 723.5 + 385.0 + 500.0)
        self.assertAlmostEqual(orc["custo_total"], 7235.0 + 723.5 + 385.0 + 500.0)

    def test_carregar_outros_custos(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "outros_custos.csv")
            with open(caminho, "w", encoding="utf-8") as f:
                f.write("item,tipo,valor,fonte,data_coleta,url_fonte\n"
                        "Estrutura,percentual,10,Premissa de teste,2026-01-01,https://exemplo.test\n"
                        "Ruim,quilo,5,fonte,2026-01-01,https://exemplo.test\n")
            lista, erros = orcamento.carregar_outros_custos(caminho)
            self.assertEqual(len(lista), 1)
            self.assertEqual(len(erros), 1)
            self.assertEqual(orcamento.carregar_outros_custos(os.path.join(pasta, "nao_existe.csv")), ([], []))


class TesteDimensionar(unittest.TestCase):
    def test_cenario_sem_bateria(self):
        ok, r = dimensionamento.dimensionar(**ENTRADA, modulos=[MODULO], inversores=[INV_HIBRIDO, INV_STRING])
        self.assertTrue(ok)
        self.assertEqual(r["n_modulos"], 7)
        self.assertAlmostEqual(r["potencia_fv_kwp"], 3.417, places=3)
        self.assertAlmostEqual(r["potencia_instalada_kwp"], 3.85)
        self.assertAlmostEqual(r["geracao_mensal_kwh"], 389.8, places=1)
        self.assertEqual(r["inversor"]["id"], "I1")
        self.assertIsNone(r["armazenamento"])
        self.assertAlmostEqual(r["orcamento"]["custo_total"], 7235.0)

    def test_cenario_com_bateria_troca_para_inversor_hibrido(self):
        ok, r = dimensionamento.dimensionar(**ENTRADA, modulos=[MODULO], inversores=[INV_STRING, INV_HIBRIDO],
                                            baterias=[BAT], com_bateria=True, autonomia_h=12)
        self.assertTrue(ok)
        self.assertEqual(r["inversor"]["id"], "I2")          # híbrido, não o mais barato
        self.assertEqual(r["armazenamento"]["quantidade"], 2)
        self.assertAlmostEqual(r["orcamento"]["custo_baterias"], 18000.0)
        self.assertAlmostEqual(r["orcamento"]["custo_total"], 4235.0 + 6000.0 + 18000.0)

    def test_com_bateria_sem_inversor_hibrido_falha_com_mensagem(self):
        ok, msgs = dimensionamento.dimensionar(**ENTRADA, modulos=[MODULO], inversores=[INV_STRING],
                                               baterias=[BAT], com_bateria=True, autonomia_h=12)
        self.assertFalse(ok)
        self.assertTrue(any("bateria" in m for m in msgs))

    def test_tenta_proximo_modulo_quando_o_mais_barato_nao_tem_inversor(self):
        barato_incompativel = {**MODULO, "id": "M2", "voc_v": 80.0, "vmp_v": 70.0, "preco_brl": 100.0}
        ok, r = dimensionamento.dimensionar(**ENTRADA, modulos=[barato_incompativel, MODULO], inversores=[INV_STRING])
        self.assertTrue(ok)
        self.assertEqual(r["modulo"]["id"], "M1")

    def test_entradas_invalidas(self):
        for alterado in ({"fracao": 0}, {"fracao": 1.5}, {"eta": 0.2}, {"hsp": -1}, {"consumo_ref_kwh": 0}):
            entrada = {**ENTRADA, **alterado}
            ok, msgs = dimensionamento.dimensionar(**entrada, modulos=[MODULO], inversores=[INV_STRING])
            self.assertFalse(ok, alterado)

    def test_autonomia_invalida(self):
        ok, _ = dimensionamento.dimensionar(**ENTRADA, modulos=[MODULO], inversores=[INV_HIBRIDO],
                                            baterias=[BAT], com_bateria=True, autonomia_h=0)
        self.assertFalse(ok)

    def test_datasets_vazios(self):
        ok, msgs = dimensionamento.dimensionar(**ENTRADA, modulos=[], inversores=[INV_STRING])
        self.assertFalse(ok)

    def test_percentual_menor_gera_menos_modulos(self):
        ok, r = dimensionamento.dimensionar(**{**ENTRADA, "fracao": 0.5}, modulos=[MODULO], inversores=[INV_STRING, INV_PEQUENO])
        self.assertTrue(ok)
        self.assertEqual(r["n_modulos"], 4)   # 1,709 kWp / 0,55 = 3,1 -> 4


class TesteInversorComColunasOpcionais(unittest.TestCase):
    CAB = ("id,fabricante,modelo,tipo,potencia_nominal_w,potencia_max_fv_w,tensao_max_entrada_v,faixa_mppt_min_v,"
           "faixa_mppt_max_v,corrente_max_entrada_a,numero_mppt,compativel_bateria,preco_brl,fornecedor,data_coleta,url_fonte")

    def _carregar(self, cabecalho, linha):
        with tempfile.TemporaryDirectory() as pasta:
            with open(os.path.join(pasta, "inversores.csv"), "w", encoding="utf-8") as f:
                f.write(cabecalho + "\n" + linha + "\n")
            return equipamentos.carregar_inversores(pasta)

    def test_sem_colunas_opcionais_vira_none(self):
        regs, erros = self._carregar(self.CAB, "I1,F,M,hibrido,3000,4500,600,80,550,16,2,sim,5000,L,2026-01-01,https://x.test")
        self.assertEqual(erros, [])
        self.assertIsNone(regs[0]["tensao_bateria_min_v"])

    def test_com_colunas_opcionais(self):
        regs, erros = self._carregar(self.CAB + ",tensao_bateria_min_v,tensao_bateria_max_v",
                                     "I1,F,M,hibrido,3000,4500,600,80,550,16,2,sim,5000,L,2026-01-01,https://x.test,40,60")
        self.assertEqual(erros, [])
        self.assertEqual((regs[0]["tensao_bateria_min_v"], regs[0]["tensao_bateria_max_v"]), (40.0, 60.0))

    def test_so_uma_das_duas_e_erro(self):
        regs, erros = self._carregar(self.CAB + ",tensao_bateria_min_v,tensao_bateria_max_v",
                                     "I1,F,M,hibrido,3000,4500,600,80,550,16,2,sim,5000,L,2026-01-01,https://x.test,40,")
        self.assertEqual(regs, [])
        self.assertIn("juntas", erros[0])


class TesteProposta(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.banco_original = dados.NOME_BANCO
        dados.NOME_BANCO = os.path.join(self.pasta.name, "teste.db")
        dados.criar_tabelas()
        conexao = dados.conectar()
        conexao.execute("INSERT INTO usuarios (nome, email, senha_hash) VALUES ('A', 'a@x.com', 'h')")
        conexao.execute("INSERT INTO usuarios (nome, email, senha_hash) VALUES ('B', 'b@x.com', 'h')")
        conexao.commit()
        conexao.close()
        _, self.id_imovel = imovel.cadastrar_imovel(1, "Casa", "Casa", "Campinas", "SP")

    def tearDown(self):
        dados.NOME_BANCO = self.banco_original
        self.pasta.cleanup()

    def _proposta(self, com_bateria=False):
        ok, r = dimensionamento.dimensionar(
            **ENTRADA, modulos=[MODULO], inversores=[INV_STRING, INV_HIBRIDO], baterias=[BAT],
            com_bateria=com_bateria, autonomia_h=12 if com_bateria else None)
        self.assertTrue(ok)
        im = imovel.buscar_imovel_por_id(self.id_imovel)
        return proposta.montar_proposta(im, "media", 5, "Fonte de teste", r)

    def test_texto_tem_os_itens_exigidos(self):
        texto = proposta.formatar_proposta(self._proposta())
        for trecho in ("Consumo de referência utilizado", "Percentual de atendimento", "Energia mensal que se pretende gerar",
                       "HSP utilizado", "Fonte de teste", "Potência FV calculada", "Potência FV instalada",
                       "7 × FabX Mod550", "Inversor:", "sem baterias", "Geração mensal estimada",
                       "Custo dos equipamentos", "Outros custos", "CUSTO TOTAL ESTIMADO", "R$ 7.235,00", "Não substitui projeto"):
            self.assertIn(trecho, texto)

    def test_texto_com_bateria(self):
        texto = proposta.formatar_proposta(self._proposta(com_bateria=True))
        for trecho in ("Armazenamento: sim", "Capacidade calculada", "Capacidade instalada", "2 × FabY Bat5"):
            self.assertIn(trecho, texto)

    def test_salvar_listar_reabrir(self):
        p = self._proposta(com_bateria=True)
        ok, id_proposta = proposta.salvar_proposta(1, self.id_imovel, p)
        self.assertTrue(ok)
        lista = proposta.listar_propostas(1)
        self.assertEqual(len(lista), 1)
        self.assertTrue(lista[0]["com_bateria"])
        reaberta = proposta.carregar_proposta(1, id_proposta)
        self.assertEqual(proposta.formatar_proposta(reaberta), proposta.formatar_proposta(p))

    def test_isolamento_entre_usuarios(self):
        ok, id_proposta = proposta.salvar_proposta(1, self.id_imovel, self._proposta())
        self.assertTrue(ok)
        self.assertEqual(proposta.listar_propostas(2), [])
        self.assertIsNone(proposta.carregar_proposta(2, id_proposta))
        ok, _ = proposta.salvar_proposta(2, self.id_imovel, self._proposta())   # imóvel do usuário 1
        self.assertFalse(ok)

    def test_formatar_brl(self):
        self.assertEqual(proposta.formatar_brl(1234.5), "R$ 1.234,50")
        self.assertEqual(proposta.formatar_brl(0), "R$ 0,00")


if __name__ == "__main__":
    unittest.main()
