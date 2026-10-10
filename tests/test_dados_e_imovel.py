"""Testes da migração do banco (PB18) e do cadastro de imóvel com cidade/UF."""

import os
import sqlite3
import tempfile
import unittest

import dados
import imovel


class BaseComBancoTemporario(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.banco_original = dados.NOME_BANCO
        dados.NOME_BANCO = os.path.join(self.pasta.name, "teste.db")

    def tearDown(self):
        dados.NOME_BANCO = self.banco_original
        self.pasta.cleanup()


class TesteMigracao(BaseComBancoTemporario):
    def test_banco_antigo_ganha_colunas_sem_perder_dados(self):
        # Cria um banco no formato ANTIGO (sem cidade/uf) com um imóvel.
        conexao = sqlite3.connect(dados.NOME_BANCO)
        conexao.executescript("""
            CREATE TABLE usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE, senha_hash TEXT NOT NULL);
            CREATE TABLE imoveis (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL,
                nome TEXT NOT NULL, endereco TEXT, tipo TEXT NOT NULL DEFAULT 'Não informado');
            CREATE TABLE consumos (id INTEGER PRIMARY KEY AUTOINCREMENT, imovel_id INTEGER NOT NULL,
                mes INTEGER NOT NULL, ano INTEGER NOT NULL, consumo_kwh REAL NOT NULL,
                UNIQUE (imovel_id, mes, ano));
            INSERT INTO usuarios (nome, email, senha_hash) VALUES ('Ana', 'ana@x.com', 'h');
            INSERT INTO imoveis (usuario_id, nome, endereco, tipo) VALUES (1, 'Casa', 'Rua A', 'Casa');
        """)
        conexao.commit()
        conexao.close()

        dados.criar_tabelas()
        dados.criar_tabelas()  # rodar duas vezes não pode dar erro

        antigo = imovel.buscar_imovel_por_id(1)
        self.assertEqual(antigo["nome"], "Casa")
        self.assertIsNone(antigo["cidade"])
        self.assertIsNone(antigo["uf"])

        ok, _ = imovel.atualizar_localizacao(1, 1, "Campinas", "sp")
        self.assertTrue(ok)
        atualizado = imovel.buscar_imovel_por_id(1)
        self.assertEqual((atualizado["cidade"], atualizado["uf"]), ("Campinas", "SP"))

    def test_atualizar_localizacao_de_imovel_de_outro_usuario_e_recusado(self):
        dados.criar_tabelas()
        conexao = dados.conectar()
        conexao.execute("INSERT INTO usuarios (nome, email, senha_hash) VALUES ('A', 'a@x.com', 'h')")
        conexao.execute("INSERT INTO usuarios (nome, email, senha_hash) VALUES ('B', 'b@x.com', 'h')")
        conexao.commit()
        conexao.close()
        ok, id_imovel = imovel.cadastrar_imovel(1, "Casa", "Casa", "Recife", "PE")
        self.assertTrue(ok)
        ok, _ = imovel.atualizar_localizacao(2, id_imovel, "Natal", "RN")
        self.assertFalse(ok)


class TesteValidacaoImovel(unittest.TestCase):
    def test_cidade_obrigatoria(self):
        ok, _ = imovel.validar_dados_imovel("Casa", "Casa", "  ", "SP")
        self.assertFalse(ok)

    def test_uf_invalida(self):
        ok, _ = imovel.validar_dados_imovel("Casa", "Casa", "Santos", "XX")
        self.assertFalse(ok)

    def test_valido(self):
        ok, _ = imovel.validar_dados_imovel("Casa", "Casa", "Santos", "sp")
        self.assertTrue(ok)

    def test_27_ufs(self):
        self.assertEqual(len(imovel.UFS_VALIDAS), 27)
        self.assertEqual(len(set(imovel.UFS_VALIDAS)), 27)


if __name__ == "__main__":
    unittest.main()
