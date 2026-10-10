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
"""

from dados import criar_tabelas
import usuario
import imovel
import consumo
import calculos
import parametros
import solar
import equipamentos


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
    consumo_ref = ref["valor_kwh"]

    # PB19 - recurso solar
    hsp, fonte_hsp = obter_hsp(imovel_escolhido)

    # PB20 - parâmetros
    while True:
        percentual = ler_numero_com_padrao("Percentual do consumo a atender, 1 a 100 (Enter = 100): ", 100.0)
        ok, mensagem = parametros.validar_fracao(percentual / 100)
        if ok:
            break
        print(f"Erro: {mensagem}")
    fracao = percentual / 100

    while True:
        eta = ler_numero_com_padrao(f"Fator de desempenho η (Enter = {parametros.ETA_PADRAO}): ", parametros.ETA_PADRAO)
        ok, mensagem = parametros.validar_eta(eta)
        if ok:
            break
        print(f"Erro: {mensagem}")

    # PB25 - cálculo da geração necessária
    energia_fv = calculos.energia_fv_mensal(consumo_ref, fracao)
    p_fv = calculos.potencia_fv_kwp(energia_fv, hsp, eta)

    print("\n===== PRÉ-DIMENSIONAMENTO FV =====")
    print(f"Imóvel: {imovel_escolhido['nome']} ({imovel_escolhido['cidade']}/{imovel_escolhido['uf']})")
    print(f"Consumo de referência ({'média' if criterio == 'media' else 'máximo'}): {consumo_ref:.2f} kWh/mês")
    print(f"Percentual de atendimento: {percentual:.0f}%")
    print(f"Energia mensal a gerar: {energia_fv:.2f} kWh/mês")
    print(f"HSP: {hsp:.2f} kWh/m²/dia (fonte: {fonte_hsp})")
    print(f"η: {eta:.2f}  |  dias considerados: {parametros.DIAS_MES}")
    print(f"Potência FV necessária: {p_fv:.3f} kWp")

    # PB26 / PB27 - módulos (só se o dataset tiver dados válidos)
    modulos, erros = equipamentos.carregar_modulos()
    for erro in erros:
        print(f"Aviso (dataset): {erro}")
    modulo = equipamentos.selecionar_modulo_mais_barato(modulos)
    if modulo is None:
        print("\nmodulos.csv ainda não tem módulos válidos; a seleção de módulos fica para quando o dataset estiver preenchido.")
    else:
        n = calculos.quantidade_modulos(p_fv, modulo["potencia_wp"])
        p_inst = calculos.potencia_instalada_kwp(n, modulo["potencia_wp"])
        geracao = calculos.geracao_mensal_kwh(p_inst, hsp, eta)
        print(f"\nMódulo selecionado (menor R$/Wp): {modulo['fabricante']} {modulo['modelo']} ({modulo['potencia_wp']:.0f} Wp)")
        print(f"Quantidade de módulos: {n}")
        print(f"Potência instalada: {p_inst:.3f} kWp")
        print(f"Geração mensal estimada: {geracao:.1f} kWh/mês ({geracao / consumo_ref * 100:.1f}% do consumo de referência)")

    print("\nPré-dimensionamento acadêmico: não substitui projeto elétrico executivo nem análise de profissional habilitado.")


def menu_logado(usuario_logado):
    while True:
        print(f"\n===== Menu ({usuario_logado['nome']}) =====")
        print("1 - Cadastrar imóvel")
        print("2 - Informar consumo mensal")
        print("3 - Ver resumo energético (maior consumo, média)")
        print("4 - Pré-dimensionamento fotovoltaico")
        print("5 - Sair do usuário (logout)")
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