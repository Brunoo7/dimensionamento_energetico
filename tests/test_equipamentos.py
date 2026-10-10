"""Testes do carregador/validador de datasets (PB24) e do HSP (PB19).

ATENÇÃO: os valores abaixo são fictícios e existem SÓ para testar o validador,
dentro de uma pasta temporária. Eles NÃO fazem parte dos datasets do projeto.
"""

import os
import tempfile
import unittest

import equipamentos
import solar

CAB_MOD = "id,fabricante,modelo,potencia_wp,voc_v,isc_a,vmp_v,imp_a,eficiencia_pct,preco_brl,fornecedor,data_coleta,url_fonte"
CAB_BAT = "id,fabricante,modelo,tecnologia,tensao_nominal_v,capacidade_ah,capacidade_kwh,dod_pct,ciclos,preco_brl,fornecedor,data_coleta,url_fonte"
CAB_INV = ("id,fabricante,modelo,tipo,potencia_nominal_w,potencia_max_fv_w,tensao_max_entrada_v,faixa_mppt_min_v,"
           "faixa_mppt_max_v,corrente_max_entrada_a,numero_mppt,compativel_bateria,preco_brl,fornecedor,data_coleta,url_fonte")
CAB_HSP = "cidade,uf,hsp_kwh_m2_dia,fonte,data_coleta,url_fonte"


class BasePastaTemporaria(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.pasta.cleanup()

    def escrever(self, nome, linhas):
        with open(os.path.join(self.pasta.name, nome), "w", encoding="utf-8") as f:
            f.write("\n".join(linhas) + "\n")


class TesteModulos(BasePastaTemporaria):
    def test_linha_valida(self):
        self.escrever("modulos.csv", [CAB_MOD, "M1,FabX,ModA,550,49.5,14.0,41.5,13.3,21.3,600.00,LojaX,2026-01-01,https://exemplo.test/a"])
        registros, erros = equipamentos.carregar_modulos(self.pasta.name)
        self.assertEqual(erros, [])
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["potencia_wp"], 550.0)

    def test_erros_por_linha(self):
        self.escrever("modulos.csv", [
            CAB_MOD,
            "M1,FabX,ModA,550,49.5,14.0,41.5,13.3,21.3,600.00,LojaX,2026-01-01,https://exemplo.test/a",
            "M2,FabX,ModB,abc,49.5,14.0,41.5,13.3,21.3,600.00,LojaX,2026-01-01,https://exemplo.test/b",
            "M3,FabX,ModC,550,49.5,14.0,41.5,13.3,21.3,0,LojaX,2026-01-01,https://exemplo.test/c",
            "M1,FabX,ModD,550,49.5,14.0,41.5,13.3,21.3,600.00,LojaX,2026-01-01,https://exemplo.test/d",
            "M5,FabX,ModE,550,49.5,14.0,41.5,13.3,21.3,600.00,LojaX,2026-01-01,exemplo-sem-http",
        ])
        registros, erros = equipamentos.carregar_modulos(self.pasta.name)
        self.assertEqual(len(registros), 1)
        self.assertEqual(len(erros), 4)
        self.assertIn("linha 3", erros[0])
        self.assertIn("linha 4", erros[1])
        self.assertIn("duplicado", erros[2])

    def test_coluna_ausente(self):
        self.escrever("modulos.csv", ["id,fabricante,modelo", "M1,A,B"])
        registros, erros = equipamentos.carregar_modulos(self.pasta.name)
        self.assertEqual(registros, [])
        self.assertIn("colunas ausentes", erros[0])

    def test_arquivo_so_com_cabecalho_e_quantidade_minima(self):
        self.escrever("modulos.csv", [CAB_MOD])
        registros, erros = equipamentos.carregar_modulos(self.pasta.name)
        self.assertEqual((registros, erros), ([], []))
        ok, _ = equipamentos.verificar_quantidade_minima("modulos", registros)
        self.assertFalse(ok)

    def test_arquivo_inexistente(self):
        registros, erros = equipamentos.carregar_modulos(self.pasta.name)
        self.assertEqual(registros, [])
        self.assertIn("não encontrado", erros[0])

    def test_selecao_menor_preco_por_wp(self):
        modulos = [
            {"id": "A", "potencia_wp": 450.0, "preco_brl": 540.0},   # 1,20 R$/Wp
            {"id": "B", "potencia_wp": 550.0, "preco_brl": 605.0},   # 1,10 R$/Wp
            {"id": "C", "potencia_wp": 600.0, "preco_brl": 720.0},   # 1,20 R$/Wp
        ]
        self.assertEqual(equipamentos.selecionar_modulo_mais_barato(modulos)["id"], "B")
        self.assertIsNone(equipamentos.selecionar_modulo_mais_barato([]))


class TesteBateriasEInversores(BasePastaTemporaria):
    def test_bateria_coerente(self):
        self.escrever("baterias.csv", [CAB_BAT, "B1,FabY,Bat5,LiFePO4,51.2,100,5.12,90,6000,9000.00,LojaY,2026-01-01,https://exemplo.test/b"])
        registros, erros = equipamentos.carregar_baterias(self.pasta.name)
        self.assertEqual(erros, [])
        self.assertEqual(len(registros), 1)

    def test_bateria_com_kwh_incoerente(self):
        self.escrever("baterias.csv", [CAB_BAT, "B1,FabY,Bat5,LiFePO4,51.2,100,10.0,90,6000,9000.00,LojaY,2026-01-01,https://exemplo.test/b"])
        registros, erros = equipamentos.carregar_baterias(self.pasta.name)
        self.assertEqual(registros, [])
        self.assertIn("não confere", erros[0])

    def test_inversor_compativel_bateria_invalido(self):
        self.escrever("inversores.csv", [CAB_INV, "I1,FabZ,Inv3,hibrido,3000,4500,600,80,550,16,2,talvez,5000.00,LojaZ,2026-01-01,https://exemplo.test/i"])
        registros, erros = equipamentos.carregar_inversores(self.pasta.name)
        self.assertEqual(registros, [])
        self.assertIn("compativel_bateria", erros[0])

    def test_inversor_valido(self):
        self.escrever("inversores.csv", [CAB_INV, "I1,FabZ,Inv3,hibrido,3000,4500,600,80,550,16,2,SIM,5000.00,LojaZ,2026-01-01,https://exemplo.test/i"])
        registros, erros = equipamentos.carregar_inversores(self.pasta.name)
        self.assertEqual(erros, [])
        self.assertEqual(registros[0]["compativel_bateria"], "sim")


class TesteHSP(BasePastaTemporaria):
    def test_busca_ignora_acento_e_maiuscula(self):
        self.escrever("hsp.csv", [CAB_HSP, "São Paulo,SP,4.5,Fonte de teste,2026-01-01,https://exemplo.test/h"])
        caminho = os.path.join(self.pasta.name, "hsp.csv")
        achado = solar.buscar_hsp("sao paulo", "sp", caminho)
        self.assertIsNotNone(achado)
        self.assertAlmostEqual(achado["hsp"], 4.5)
        self.assertIsNone(solar.buscar_hsp("Santos", "SP", caminho))

    def test_hsp_invalido_gera_erro(self):
        self.escrever("hsp.csv", [CAB_HSP, "Cidade,SP,12,Fonte,2026-01-01,https://exemplo.test/h", "Outra,SP,x,Fonte,2026-01-01,https://exemplo.test/h"])
        registros, erros = solar.carregar_hsp(os.path.join(self.pasta.name, "hsp.csv"))
        self.assertEqual(registros, [])
        self.assertEqual(len(erros), 2)

    def test_arquivo_so_com_cabecalho(self):
        self.escrever("hsp.csv", [CAB_HSP])
        self.assertIsNone(solar.buscar_hsp("X", "SP", os.path.join(self.pasta.name, "hsp.csv")))


if __name__ == "__main__":
    unittest.main()
