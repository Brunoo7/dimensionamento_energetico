"""Testes de segurança de senha, editar/excluir imóvel (PB04) e gráfico (PB12)."""

import hashlib
import os
import tempfile
import unittest

import dados
import grafico
import imovel
import proposta
import usuario


class BaseComBanco(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.banco_original = dados.NOME_BANCO
        dados.NOME_BANCO = os.path.join(self.pasta.name, "teste.db")
        dados.criar_tabelas()

    def tearDown(self):
        dados.NOME_BANCO = self.banco_original
        self.pasta.cleanup()


class TesteSenha(BaseComBanco):
    def test_cadastro_e_login(self):
        ok, _ = usuario.cadastrar_usuario("Ana", "Ana@X.com", "senhaforte1")
        self.assertTrue(ok)
        ok, u = usuario.login("ana@x.com", "senhaforte1")
        self.assertTrue(ok)
        self.assertEqual(u["nome"], "Ana")
        ok, _ = usuario.login("ana@x.com", "errada123")
        self.assertFalse(ok)

    def test_hash_usa_sal_e_nao_guarda_senha(self):
        usuario.cadastrar_usuario("Ana", "a@x.com", "senhaforte1")
        usuario.cadastrar_usuario("Beto", "b@x.com", "senhaforte1")   # mesma senha
        conexao = dados.conectar()
        hashes = [r[0] for r in conexao.execute("SELECT senha_hash FROM usuarios ORDER BY id")]
        conexao.close()
        self.assertNotEqual(hashes[0], hashes[1])                    # sal diferente por usuário
        self.assertTrue(all(h.startswith("pbkdf2_sha256$") for h in hashes))
        self.assertTrue(all("senhaforte1" not in h for h in hashes))

    def test_email_duplicado_mensagem_especifica(self):
        usuario.cadastrar_usuario("Ana", "a@x.com", "senhaforte1")
        ok, mensagem = usuario.cadastrar_usuario("Outra", "A@X.com", "senhaforte2")
        self.assertFalse(ok)
        self.assertIn("e-mail", mensagem)

    def test_senha_curta_e_rejeitada(self):
        ok, _ = usuario.cadastrar_usuario("Ana", "a@x.com", "1234")
        self.assertFalse(ok)

    def test_conta_antiga_sha256_continua_funcionando_e_e_atualizada(self):
        antigo = hashlib.sha256("senhaantiga".encode("utf-8")).hexdigest()
        conexao = dados.conectar()
        conexao.execute("INSERT INTO usuarios (nome, email, senha_hash) VALUES ('Velho', 'v@x.com', ?)", (antigo,))
        conexao.commit()
        conexao.close()

        ok, _ = usuario.login("v@x.com", "senhaantiga")
        self.assertTrue(ok)
        conexao = dados.conectar()
        novo = conexao.execute("SELECT senha_hash FROM usuarios WHERE email = 'v@x.com'").fetchone()[0]
        conexao.close()
        self.assertTrue(novo.startswith("pbkdf2_sha256$"))
        ok, _ = usuario.login("v@x.com", "senhaantiga")           # ainda entra após a atualização
        self.assertTrue(ok)
        ok, _ = usuario.login("v@x.com", "outrasenha")
        self.assertFalse(ok)


class TesteEditarExcluirImovel(BaseComBanco):
    def setUp(self):
        super().setUp()
        usuario.cadastrar_usuario("Ana", "a@x.com", "senhaforte1")
        usuario.cadastrar_usuario("Beto", "b@x.com", "senhaforte2")
        _, self.id_imovel = imovel.cadastrar_imovel(1, "Casa", "Casa", "Campinas", "SP", "Rua A")

    def test_editar(self):
        ok, _ = imovel.editar_imovel(1, self.id_imovel, "Casa de praia", "Sobrado", "Santos", "sp", "Av B")
        self.assertTrue(ok)
        i = imovel.buscar_imovel_por_id(self.id_imovel)
        self.assertEqual((i["nome"], i["tipo"], i["cidade"], i["uf"], i["endereco"]),
                         ("Casa de praia", "Sobrado", "Santos", "SP", "Av B"))

    def test_editar_com_dados_invalidos_nao_altera(self):
        ok, _ = imovel.editar_imovel(1, self.id_imovel, "", "Casa", "Santos", "SP")
        self.assertFalse(ok)
        ok, _ = imovel.editar_imovel(1, self.id_imovel, "Casa", "Casa", "Santos", "XX")
        self.assertFalse(ok)
        self.assertEqual(imovel.buscar_imovel_por_id(self.id_imovel)["cidade"], "Campinas")

    def test_outro_usuario_nao_edita_nem_exclui(self):
        ok, _ = imovel.editar_imovel(2, self.id_imovel, "Invasor", "Casa", "X", "SP")
        self.assertFalse(ok)
        ok, _ = imovel.excluir_imovel(2, self.id_imovel)
        self.assertFalse(ok)
        self.assertEqual(imovel.buscar_imovel_por_id(self.id_imovel)["nome"], "Casa")

    def test_excluir_apaga_consumos_e_propostas(self):
        conexao = dados.conectar()
        conexao.execute("INSERT INTO consumos (imovel_id, mes, ano, consumo_kwh) VALUES (?, 1, 2026, 300)", (self.id_imovel,))
        conexao.commit()
        conexao.close()
        proposta_minima = {"imovel": {"nome": "Casa"}, "potencia_instalada_kwp": 3.0,
                           "orcamento": {"custo_total": 1.0}, "armazenamento": None}
        ok, _ = proposta.salvar_proposta(1, self.id_imovel, proposta_minima)
        self.assertTrue(ok)

        ok, _ = imovel.excluir_imovel(1, self.id_imovel)
        self.assertTrue(ok)
        self.assertIsNone(imovel.buscar_imovel_por_id(self.id_imovel))
        conexao = dados.conectar()
        self.assertEqual(conexao.execute("SELECT COUNT(*) FROM consumos").fetchone()[0], 0)
        self.assertEqual(conexao.execute("SELECT COUNT(*) FROM propostas").fetchone()[0], 0)
        conexao.close()

    def test_excluir_um_imovel_nao_afeta_outro(self):
        _, outro = imovel.cadastrar_imovel(1, "Apto", "Apartamento", "Recife", "PE")
        imovel.excluir_imovel(1, self.id_imovel)
        self.assertIsNotNone(imovel.buscar_imovel_por_id(outro))


class TesteGrafico(unittest.TestCase):
    HISTORICO = [{"mes": 1, "ano": 2026, "consumo_kwh": 320}, {"mes": 2, "ano": 2026, "consumo_kwh": 295},
                 {"mes": 3, "ano": 2026, "consumo_kwh": 410}]

    def test_texto_tem_meses_no_x_e_kwh_no_y(self):
        texto = grafico.gerar_grafico_texto(self.HISTORICO)
        self.assertIn("Consumo mensal (kWh)", texto)
        for rotulo in ("Jan/26", "Fev/26", "Mar/26"):
            self.assertIn(rotulo, texto)
        self.assertIn("410", texto)              # o topo do eixo Y é o maior consumo
        self.assertIn("█", texto)

    def test_maior_consumo_tem_a_barra_mais_alta(self):
        linhas = grafico.gerar_grafico_texto(self.HISTORICO, altura=10).splitlines()
        primeira_linha_de_barra = linhas[1]      # nível mais alto
        self.assertEqual(primeira_linha_de_barra.count("█"), 1)   # só março chega ao topo

    def test_sem_dados(self):
        self.assertIn("Nenhum consumo", grafico.gerar_grafico_texto([]))
        ok, _ = grafico.salvar_grafico_png([])
        self.assertFalse(ok)

    def test_png(self):
        try:
            import matplotlib  # noqa: F401
        except ImportError:
            self.skipTest("matplotlib não instalado")
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "g.png")
            ok, _ = grafico.salvar_grafico_png(self.HISTORICO, caminho)
            self.assertTrue(ok)
            self.assertGreater(os.path.getsize(caminho), 1000)


if __name__ == "__main__":
    unittest.main()
