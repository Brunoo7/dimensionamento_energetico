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

Sprint FV (parte 1):
    PB16 - Consumo de referência
    PB18 - Cidade e UF do imóvel
    PB19 - HSP por localidade (data/hsp.csv) ou informado manualmente
    PB20 - Parâmetros do dimensionamento (percentual de atendimento e η)
    PB25 - Potência FV necessária
    PB26 - Módulos e potência instalada (quando data/modulos.csv tiver dados)
    PB27 - Geração mensal estimada

Sprint FV (parte 2):
    PB28/PB29 - Inversor e validação das strings
    PB30/PB31 - Baterias opcionais
    PB32/PB33 - Orçamento
    PB34/PB35 - Proposta preliminar (salvar e consultar)
"""

from dados import criar_tabelas
import usuario
import imovel
import consumo
import calculos
import parametros
import solar
import equipamentos
import orcamento
import dimensionamento
import proposta


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


def ler_numero_com_padrao(mensagem, padrao):
    """Lê um número; se o usuário só apertar Enter, devolve o valor padrão."""
    while True:
        valor = input(mensagem).strip().replace(",", ".")
        if valor == "":
            return padrao
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

    print(f"Tipos sugeridos: {', '.join(imovel.TIPOS_VALIDOS)}")
    tipo = input("Tipo do imóvel: ")

    cidade = input("Cidade: ")
    uf = input("UF (ex.: SP): ")
    endereco = input("Endereço (opcional): ")

    ok, resultado = imovel.cadastrar_imovel(usuario_logado["id"], nome, tipo, cidade, uf, endereco)
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
        local = f"{item['cidade']}/{item['uf']}" if item["cidade"] and item["uf"] else "sem cidade/UF"
        print(f"  {item['id']} - {item['nome']} ({item['tipo']}, {local})")

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


def garantir_localizacao(usuario_logado, imovel_escolhido):
    """PB18 - Se o imóvel (ex.: cadastrado antes da Sprint FV) não tem cidade/UF, pede agora."""
    while not (imovel_escolhido["cidade"] and imovel_escolhido["uf"]):
        print("Este imóvel ainda não tem cidade e UF (necessárias para o HSP).")
        cidade = input("Cidade: ")
        uf = input("UF (ex.: SP): ")
        ok, mensagem = imovel.atualizar_localizacao(usuario_logado["id"], imovel_escolhido["id"], cidade, uf)
        if not ok:
            print(f"Erro: {mensagem}")
            continue
        imovel_escolhido["cidade"], imovel_escolhido["uf"] = cidade.strip(), uf.strip().upper()


def obter_hsp(imovel_escolhido):
    """PB19 - Busca o HSP no CSV; se não achar, pede o valor manualmente."""
    registro = solar.buscar_hsp(imovel_escolhido["cidade"], imovel_escolhido["uf"])
    if registro:
        print(f"HSP de {registro['cidade']}/{registro['uf']}: {registro['hsp']:.2f} kWh/m²/dia "
              f"(fonte: {registro['fonte']})")
        return registro["hsp"], registro["fonte"]

    print(f"Não há HSP de {imovel_escolhido['cidade']}/{imovel_escolhido['uf']} em data/hsp.csv.")
    print("Consulte o CRESESB (SunData) ou o Atlas Brasileiro de Energia Solar e informe o valor.")
    while True:
        hsp = ler_numero("HSP médio anual (kWh/m²/dia): ")
        ok, mensagem = parametros.validar_hsp(hsp)
        if ok:
            return hsp, "informado manualmente pelo usuário"
        print(f"Erro: {mensagem}")


def ler_sim_nao(mensagem):
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        print("Responda com s ou n.")


def tela_dimensionamento_fv(usuario_logado):
    print("\n--- Pré-dimensionamento fotovoltaico ---")
    imovel_escolhido = escolher_imovel(usuario_logado)
    if imovel_escolhido is None:
        return

    historico = consumo.listar_consumos_imovel(usuario_logado["id"], imovel_escolhido["id"])
    if not historico:
        print("Cadastre ao menos um mês de consumo antes de dimensionar.")
        return

    garantir_localizacao(usuario_logado, imovel_escolhido)

    # PB16 - consumo de referência
    print("\nConsumo de referência: 1 - média (padrão)  2 - maior consumo")
    criterio = "maximo" if input("Escolha: ").strip() == "2" else "media"
    ok, ref = calculos.consumo_de_referencia(historico, criterio)
    if not ok:
        print(f"Erro: {ref}")
        return
    if ref["aviso"]:
        print(f"Aviso: {ref['aviso']}")

    # PB19 - recurso solar
    hsp, fonte_hsp = obter_hsp(imovel_escolhido)

    # PB20 - parâmetros
    while True:
        percentual = ler_numero_com_padrao("Percentual do consumo a atender, 1 a 100 (Enter = 100): ", 100.0)
        ok, mensagem = parametros.validar_fracao(percentual / 100)
        if ok:
            break
        print(f"Erro: {mensagem}")

    while True:
        eta = ler_numero_com_padrao(f"Fator de desempenho η (Enter = {parametros.ETA_PADRAO}): ", parametros.ETA_PADRAO)
        ok, mensagem = parametros.validar_eta(eta)
        if ok:
            break
        print(f"Erro: {mensagem}")

    com_bateria = ler_sim_nao("Deseja incluir armazenamento por baterias? (s/n): ")
    autonomia = None
    if com_bateria:
        while True:
            autonomia = ler_numero("Autonomia desejada em horas: ")
            ok, mensagem = parametros.validar_autonomia(autonomia)
            if ok:
                break
            print(f"Erro: {mensagem}")

    # Datasets
    modulos, e1 = equipamentos.carregar_modulos()
    inversores, e2 = equipamentos.carregar_inversores()
    baterias, e3 = equipamentos.carregar_baterias()
    outros, e4 = orcamento.carregar_outros_custos()
    for erro in e1 + e2 + e3 + e4:
        print(f"Aviso (dataset): {erro}")

    ok, resultado = dimensionamento.dimensionar(
        ref["valor_kwh"], hsp, percentual / 100, eta, modulos, inversores,
        baterias=baterias, outros_custos=outros, com_bateria=com_bateria, autonomia_h=autonomia)
    if not ok:
        print("\nNão foi possível montar a proposta:")
        for mensagem in resultado:
            print(f"  - {mensagem}")
        return

    dados_proposta = proposta.montar_proposta(
        imovel_escolhido, criterio, ref["meses_analisados"], fonte_hsp, resultado)
    print()
    print(proposta.formatar_proposta(dados_proposta))

    if ler_sim_nao("\nSalvar esta proposta? (s/n): "):
        ok, retorno = proposta.salvar_proposta(usuario_logado["id"], imovel_escolhido["id"], dados_proposta)
        print(f"Proposta salva (id {retorno})." if ok else f"Erro: {retorno}")


def tela_minhas_propostas(usuario_logado):
    print("\n--- Minhas propostas ---")
    lista = proposta.listar_propostas(usuario_logado["id"])
    if not lista:
        print("Você ainda não salvou nenhuma proposta.")
        return
    for item in lista:
        tipo = "com bateria" if item["com_bateria"] else "sem bateria"
        print(f"  {item['id']} - {item['criada_em']} - {item['imovel_nome']} - "
              f"{item['potencia_instalada_kwp']:.2f} kWp, {tipo}, "
              f"{proposta.formatar_brl(item['custo_total'])}")
    id_escolhido = ler_inteiro("Digite o id da proposta para abrir (0 para voltar): ")
    if id_escolhido == 0:
        return
    dados_proposta = proposta.carregar_proposta(usuario_logado["id"], id_escolhido)
    if dados_proposta is None:
        print("Proposta não encontrada.")
        return
    print()
    print(proposta.formatar_proposta(dados_proposta))


def menu_logado(usuario_logado):
    while True:
        print(f"\n===== Menu ({usuario_logado['nome']}) =====")
        print("1 - Cadastrar imóvel")
        print("2 - Informar consumo mensal")
        print("3 - Ver resumo energético (maior consumo, média)")
        print("4 - Pré-dimensionamento fotovoltaico")
        print("5 - Minhas propostas salvas")
        print("6 - Sair do usuário (logout)")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            tela_cadastro_imovel(usuario_logado)
        elif opcao == "2":
            tela_informar_consumo(usuario_logado)
        elif opcao == "3":
            tela_resumo_energetico(usuario_logado)
        elif opcao == "4":
            tela_dimensionamento_fv(usuario_logado)
        elif opcao == "5":
            tela_minhas_propostas(usuario_logado)
        elif opcao == "6":
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