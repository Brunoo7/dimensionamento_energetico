"""
parametros.py

Parâmetros e validações do dimensionamento fotovoltaico (PB20).
Nenhum desses valores deve ficar "solto" no código: se mudar um limite ou
um valor padrão, é aqui que muda (e a documentação deve acompanhar).
"""

DIAS_MES = 30                 # D: dias considerados no mês
ETA_PADRAO = 0.75             # η: fator global de desempenho (premissa a documentar)
ETA_MIN = 0.50
ETA_MAX = 0.95
HSP_MAX = 8.0                 # kWh/m²/dia - acima disso o valor é implausível
FRACAO_MIN = 0.01             # 1 %
FRACAO_MAX = 1.0              # 100 %
AUTONOMIA_MAX_H = 48          # horas
MESES_RECOMENDADOS = 12       # meses de histórico recomendados (PB16)

# Validação elétrica módulos-inversor (PB28 / PB29)
# ATENÇÃO: sem o coeficiente de temperatura do datasheet, usamos fatores de margem.
# São PREMISSAS (valores típicos) a documentar ou substituir pelos coeficientes reais.
FATOR_VOC_FRIO = 1.12         # Voc aumenta no frio: Voc_frio = Voc × fator
FATOR_VMP_QUENTE = 0.85       # Vmp cai no calor: Vmp_quente = Vmp × fator
RAZAO_FV_CA_MIN = 0.5         # P_instalada / P_nominal do inversor (mínimo aceito; inversor sobredimensionado só encarece)
RAZAO_FV_CA_MAX = 1.5         # idem (máximo aceito)

# Parâmetros de bateria (valores padrão usados quando o dataset não informa)
DOD_PADRAO = 0.90
ETA_BATERIA_PADRAO = 0.95


def validar_fracao(fracao):
    """f deve estar entre 1 % e 100 % (valor em fração: 0,01 a 1,0)."""
    if not isinstance(fracao, (int, float)) or not (FRACAO_MIN <= fracao <= FRACAO_MAX):
        return False, "O percentual de atendimento deve estar entre 1% e 100%."
    return True, ""


def validar_eta(eta):
    if not isinstance(eta, (int, float)) or not (ETA_MIN <= eta <= ETA_MAX):
        return False, f"O fator de desempenho (η) deve estar entre {ETA_MIN:.2f} e {ETA_MAX:.2f}."
    return True, ""


def validar_hsp(hsp):
    if not isinstance(hsp, (int, float)) or not (0 < hsp <= HSP_MAX):
        return False, f"O HSP deve ser maior que 0 e no máximo {HSP_MAX:.0f} kWh/m²/dia."
    return True, ""


def validar_autonomia(horas):
    if not isinstance(horas, (int, float)) or not (0 < horas <= AUTONOMIA_MAX_H):
        return False, f"A autonomia deve ser maior que 0 e no máximo {AUTONOMIA_MAX_H} horas."
    return True, ""
