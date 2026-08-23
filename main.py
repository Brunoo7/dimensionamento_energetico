"""
main.py

Ponto de entrada do sistema. Menu de linha de comando cobrindo a Sprint 1:
    PB01 - Cadastro de usuário
    PB02 - Login
    PB03 - Cadastro de imóvel
    PB05 - Informar consumo mensal
    PB06 - Vários meses de consumo (histórico)
    PB08 - Maior consumo
    PB11 - Resumo energético
    PB13 - Validações
    PB14 - Persistência em banco (SQLite)
    PB15 - Segurança (isolamento de dados entre usuários)
"""

from dados import criar_tabelas
import usuario
import imovel
import consumo
import calculos


def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem).strip()
        try:
            return int(valor)
        except ValueError:
            print("Por favor, digite um número inteiro válido.")


def ler_numero(mensagem):
    while True:
        valor = input(mensagem).strip().replace(",", ".")
        try:
            return float(valor)
        except ValueError:
            print("Por favor, digite um número válido.")


def tela_cadastro_usuario():
    print("\n--- Cadastro de usuário ---")
    nome = input("Nome: ")
    email = input("E-mail: ")
    senha = input("Senha: ")

    ok, resultado = usuario.cadastrar_usuario(nome, email, senha)
    if ok:
        print("Usuário cadastrado com sucesso! Faça login para continuar.")
    else:
        print(f"Erro: {resultado}")


def tela_login():
    print("\n--- Login ---")
    email = input("E-mail: ")
    senha = input("Senha: ")

    ok, resultado = usuario.login(email, senha)
    if ok:
        print(f"Bem-vindo(a), {resultado['nome']}!")
        return resultado
    else:
        print(f"Erro: {resultado}")
        return None


def tela_cadastro_imovel(usuario_logado):
    print("\n--- Cadastro de imóvel ---")
    nome = input("Nome/apelido do imóvel (ex.: Casa, Apartamento): ")
    endereco = input("Endereço (opcional): ")

    ok, resultado = imovel.cadastrar_imovel(usuario_logado["id"], nome, endereco)
    if ok:
        print(f"Imóvel cadastrado com sucesso! (id {resultado})")
    else:
        print(f"Erro: {resultado}")


def escolher_imovel(usuario_logado):
    imoveis = imovel.listar_imoveis_usuario(usuario_logado["id"])
    if not imoveis:
        print("Você ainda não tem nenhum imóvel cadastrado.")
        return None

    print("\nSeus imóveis:")
    for item in imoveis:
        print(f"  {item['id']} - {item['nome']} ({item['endereco'] or 'sem endereço'})")

    id_escolhido = ler_inteiro("Digite o id do imóvel: ")
    escolhidos = [i for i in imoveis if i["id"] == id_escolhido]
    return escolhidos[0] if escolhidos else None


def tela_informar_consumo(usuario_logado):
    print("\n--- Informar consumo mensal ---")
    imovel_escolhido = escolher_imovel(usuario_logado)
    if imovel_escolhido is None:
        return

    mes = ler_inteiro("Mês (1 a 12): ")
    ano = ler_inteiro("Ano (ex.: 2026): ")
    consumo_kwh = ler_numero("Consumo do mês em kWh: ")

    ok, mensagem = consumo.registrar_consumo(
        usuario_logado["id"], imovel_escolhido["id"], mes, ano, consumo_kwh
    )
    print(mensagem if ok else f"Erro: {mensagem}")


def tela_resumo_energetico(usuario_logado):
    print("\n--- Resumo energético ---")
    imovel_escolhido = escolher_imovel(usuario_logado)
    if imovel_escolhido is None:
        return

    historico = consumo.listar_consumos_imovel(usuario_logado["id"], imovel_escolhido["id"])

    print(f"\nHistórico de {imovel_escolhido['nome']}:")
    for item in historico:
        mes_nome = consumo.nome_do_mes(item["mes"])
        print(f"  {mes_nome}/{item['ano']}: {item['consumo_kwh']:.2f} kWh")

    resumo = calculos.calcular_resumo(historico)
    print()
    print(calculos.formatar_resumo(resumo))


def menu_logado(usuario_logado):
    while True:
        print(f"\n===== Menu ({usuario_logado['nome']}) =====")
        print("1 - Cadastrar imóvel")
        print("2 - Informar consumo mensal")
        print("3 - Ver resumo energético (maior consumo, média)")
        print("4 - Sair do usuário (logout)")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            tela_cadastro_imovel(usuario_logado)
        elif opcao == "2":
            tela_informar_consumo(usuario_logado)
        elif opcao == "3":
            tela_resumo_energetico(usuario_logado)
        elif opcao == "4":
            break
        else:
            print("Opção inválida.")


def menu_principal():
    criar_tabelas()

    while True:
        print("\n===== DIMENSIONAMENTO ENERGÉTICO RESIDENCIAL =====")
        print("1 - Cadastrar usuário")
        print("2 - Login")
        print("3 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            tela_cadastro_usuario()
        elif opcao == "2":
            usuario_logado = tela_login()
            if usuario_logado:
                menu_logado(usuario_logado)
        elif opcao == "3":
            print("Até logo!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu_principal()