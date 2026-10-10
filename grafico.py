"""
grafico.py

Gráfico do histórico de consumo (PB12): meses no eixo X e consumo (kWh) no eixo Y.

    gerar_grafico_texto  - gráfico em barras no próprio terminal (não precisa instalar nada)
    salvar_grafico_png   - imagem PNG (precisa do matplotlib: pip install matplotlib)
"""

from consumo import NOMES_MES


def _rotulo(item):
    return f"{NOMES_MES[item['mes'] - 1][:3]}/{str(item['ano'])[2:]}"


def gerar_grafico_texto(historico, altura=10):
    """Gráfico de barras verticais em texto. Retorna uma string (ou aviso se não houver dados)."""
    if not historico:
        return "Nenhum consumo registrado para gerar o gráfico."

    valores = [item["consumo_kwh"] for item in historico]
    maximo = max(valores)
    if maximo <= 0:
        return "Todos os consumos são zero; não há o que mostrar no gráfico."

    rotulos = [_rotulo(item) for item in historico]
    largura_coluna = max(len(r) for r in rotulos) + 1
    # Altura (em "andares") de cada barra, arredondada para o inteiro mais próximo.
    alturas = [round(v / maximo * altura) for v in valores]

    linhas = ["Consumo mensal (kWh)"]
    for nivel in range(altura, 0, -1):
        valor_do_nivel = maximo * nivel / altura
        corpo = "".join(("█" if h >= nivel else " ").center(largura_coluna) for h in alturas)
        linhas.append(f"{valor_do_nivel:8.0f} |{corpo}")
    linhas.append(" " * 9 + "+" + "-" * (largura_coluna * len(valores)))
    linhas.append(" " * 10 + "".join(r.center(largura_coluna) for r in rotulos))
    linhas.append(" " * 10 + "Mês/ano")
    return "\n".join(linhas)


def salvar_grafico_png(historico, caminho="grafico_consumo.png"):
    """Salva o gráfico em PNG. Retorna (True, caminho) ou (False, mensagem)."""
    if not historico:
        return False, "Nenhum consumo registrado para gerar o gráfico."
    try:
        import matplotlib
        matplotlib.use("Agg")   # não abre janela; só grava o arquivo
        import matplotlib.pyplot as plt
    except ImportError:
        return False, "matplotlib não está instalado. Instale com: pip install matplotlib"

    rotulos = [_rotulo(item) for item in historico]
    valores = [item["consumo_kwh"] for item in historico]

    figura, eixo = plt.subplots(figsize=(8, 4))
    eixo.bar(rotulos, valores, color="#2a7ab0")
    eixo.set_xlabel("Mês/ano")
    eixo.set_ylabel("Consumo (kWh)")
    eixo.set_title("Histórico de consumo mensal")
    eixo.tick_params(axis="x", rotation=45)
    figura.tight_layout()
    figura.savefig(caminho, dpi=120)
    plt.close(figura)
    return True, caminho
