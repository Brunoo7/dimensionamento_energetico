"""Testes dos cálculos (PB16, PB25, PB26, PB27, PB30, PB31) com os exemplos do backlog."""

import unittest

import calculos

HISTORICO = [
    {"mes": 1, "ano": 2026, "consumo_kwh": 320},
    {"mes": 2, "ano": 2026, "consumo_kwh": 295},
    {"mes": 3, "ano": 2026, "consumo_kwh": 410},
    {"mes": 4, "ano": 2026, "consumo_kwh": 365},
    {"mes": 5, "ano": 2026, "consumo_kwh": 340},
]


class TesteConsumoDeReferencia(unittest.TestCase):
    def test_media_e_maximo(self):
        ok, ref = calculos.consumo_de_referencia(HISTORICO)
        self.assertTrue(ok)
        self.assertAlmostEqual(ref["valor_kwh"], 346.0)
        ok, ref = calculos.consumo_de_referencia(HISTORICO, "maximo")
        self.assertAlmostEqual(ref["valor_kwh"], 410.0)

    def test_aviso_com_menos_de_12_meses(self):
        _, ref = calculos.consumo_de_referencia(HISTORICO)
        self.assertIsNotNone(ref["aviso"])

    def test_sem_aviso_com_12_meses(self):
        historico = [{"mes": m, "ano": 2025, "consumo_kwh": 300} for m in range(1, 13)]
        _, ref = calculos.consumo_de_referencia(historico)
        self.assertIsNone(ref["aviso"])

    def test_historico_vazio(self):
        ok, mensagem = calculos.consumo_de_referencia([])
        self.assertFalse(ok)

    def test_criterio_invalido(self):
        ok, _ = calculos.consumo_de_referencia(HISTORICO, "mediana")
        self.assertFalse(ok)


class TesteDimensionamentoFV(unittest.TestCase):
    def test_potencia_fv_exemplo_do_backlog(self):
        e_fv = calculos.energia_fv_mensal(346, 1.0)
        self.assertAlmostEqual(e_fv, 346.0)
        p_fv = calculos.potencia_fv_kwp(e_fv, hsp=4.5, eta=0.75, dias=30)
        self.assertAlmostEqual(p_fv, 3.417, places=3)

    def test_percentual_menor_que_100(self):
        self.assertAlmostEqual(calculos.energia_fv_mensal(400, 0.5), 200.0)

    def test_modulos_e_potencia_instalada(self):
        p_fv = calculos.potencia_fv_kwp(346, 4.5, 0.75)
        n = calculos.quantidade_modulos(p_fv, 550)
        self.assertEqual(n, 7)
        p_inst = calculos.potencia_instalada_kwp(n, 550)
        self.assertAlmostEqual(p_inst, 3.85)
        self.assertGreaterEqual(p_inst, p_fv)

    def test_multiplo_exato_nao_soma_modulo_extra(self):
        # 3,85 kWp com módulo de 550 Wp = exatamente 7 módulos
        self.assertEqual(calculos.quantidade_modulos(3.85, 550), 7)

    def test_geracao_mensal(self):
        g = calculos.geracao_mensal_kwh(3.85, 4.5, 0.75)
        self.assertAlmostEqual(g, 389.8, places=1)
        self.assertAlmostEqual(g / 346 * 100, 112.7, places=1)


class TesteBaterias(unittest.TestCase):
    def test_capacidade_necessaria_exemplo_do_backlog(self):
        self.assertAlmostEqual(calculos.energia_diaria_kwh(346), 11.533, places=3)
        e_aut = calculos.energia_autonomia_kwh(346, 12)
        self.assertAlmostEqual(e_aut, 5.767, places=3)
        c_bat = calculos.capacidade_bateria_necessaria_kwh(e_aut, 0.90, 0.95)
        self.assertAlmostEqual(c_bat, 6.745, places=3)

    def test_quantidade_nao_aplica_dod_duas_vezes(self):
        c_bat = calculos.capacidade_bateria_necessaria_kwh(5.767, 0.90, 0.95)
        # 6,745 kWh nominais necessários / 5 kWh por bateria = 2 baterias
        self.assertEqual(calculos.quantidade_baterias(c_bat, 5.0), 2)


if __name__ == "__main__":
    unittest.main()
