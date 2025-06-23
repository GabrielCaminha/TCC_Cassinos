import random
import numpy as np
from tqdm import tqdm

# === Configuração do depósito inicial ===
DEPOSITO_INICIAL = 30.0  

# === Configuração das rodadas grátis ===
NUM_RODADAS_GRATIS = 10
APOSTA_FIXA = 0.4

symbols = {
    "🐉": {"multiplier": 100, "weight": 1},
    "🏆": {"multiplier": 50, "weight": 2},
    "🍊": {"multiplier": 25, "weight": 8},
    "🔑": {"multiplier": 10, "weight": 20},
    "💰": {"multiplier": 5, "weight": 30},
    "🧧": {"multiplier": 3, "weight": 39},
    "🔭": {"multiplier": 2, "weight": 61},
}

prob_rodada_da_fortuna = 0.03
chance_terceiro_giro = 0.21
rodadas_fortuna_iniciais = 8

# === Paylines ===
paylines = [
    [(0, 0), (0, 1), (0, 2)],
    [(1, 0), (1, 1), (1, 2)],
    [(2, 0), (2, 1), (2, 2)],
    [(0, 0), (1, 1), (2, 2)],
    [(2, 0), (1, 1), (0, 2)]
]

# === Geração do pool de símbolos ===
symbol_pool = []
for emoji, data in symbols.items():
    symbol_pool.extend([emoji] * data["weight"])

def girar_cilindro(rodada_da_fortuna):
    cylinder = {
        "1":  {"multiplier": 1,  "weight": 0 if rodada_da_fortuna else 10},
        "2":  {"multiplier": 2,  "weight": 12 if rodada_da_fortuna else 24},
        "5":  {"multiplier": 5,  "weight": 5 if rodada_da_fortuna else 15},
        "10": {"multiplier": 10, "weight": 3 if rodada_da_fortuna else 4},
    }
    opcoes = list(cylinder.keys())
    pesos = [cylinder[key]["weight"] for key in opcoes]
    return int(random.choices(opcoes, weights=pesos, k=1)[0])

def gerar_grade():
    return [[random.choice(symbol_pool) for _ in range(3)] for _ in range(3)]

def calcular_premio(grade, aposta_por_linha, rodada_da_fortuna):
    # Determinar multiplicador Dragão
    if rodada_da_fortuna:
        multi1 = girar_cilindro(True)
        multi2 = girar_cilindro(True)
        multi3 = girar_cilindro(True) if random.random() < chance_terceiro_giro else 0
        multiplicador_dragao = multi1 + multi2 + multi3
    else:
        multiplicador_dragao = girar_cilindro(False)

    ganho_total = 0
    for linha in paylines:
        simbolos = [grade[x][y] for x, y in linha]
        simbolos_reais = [s for s in simbolos if s != "🐉"]

        if not simbolos_reais or all(s == simbolos_reais[0] for s in simbolos_reais):
            simbolo_vencedor = simbolos_reais[0] if simbolos_reais else "🐉"
            multiplicador = symbols[simbolo_vencedor]["multiplier"]
            ganho_total += aposta_por_linha * multiplicador * multiplicador_dragao

    return ganho_total

def simular_jogador():
    linhas_ativas = len(paylines)
    aposta_por_linha = APOSTA_FIXA / linhas_ativas
    saldo = 0
    total_apostado = 0
    ganhos_por_rodada = []

    rodadas_fortuna_restantes = 0

    # === Rodadas grátis ===
    for _ in range(NUM_RODADAS_GRATIS):
        rodada_da_fortuna = rodadas_fortuna_restantes > 0
        grade = gerar_grade()
        ganho = calcular_premio(grade, aposta_por_linha, rodada_da_fortuna)
        saldo += ganho
        total_apostado += APOSTA_FIXA
        ganhos_por_rodada.append(ganho)

        if rodada_da_fortuna:
            rodadas_fortuna_restantes -= 1
        else:
            if random.random() < prob_rodada_da_fortuna:
                rodadas_fortuna_restantes = rodadas_fortuna_iniciais

    return saldo, total_apostado, ganhos_por_rodada

def main():
    NUM_JOGADORES = 100000

    resultados = {
        'saldos_finais': [],
        'total_apostado': 0,
        'total_ganho': 0,
        'ganhos_rodadas': [],
        'jogadores_com_lucro': 0
    }

    for _ in tqdm(range(NUM_JOGADORES), desc="Simulando jogadores"):
        saldo_final, apostado, ganhos_por_rodada = simular_jogador()

        # Subtrai o depósito inicial do saldo final
        saldo_liquido = saldo_final - DEPOSITO_INICIAL

        resultados['saldos_finais'].append(saldo_liquido)
        resultados['total_apostado'] += apostado
        resultados['total_ganho'] += saldo_final
        resultados['ganhos_rodadas'].extend(ganhos_por_rodada)

        # Contabiliza jogadores que terminaram com lucro (ganho > depósito)
        if saldo_final > DEPOSITO_INICIAL:
            resultados['jogadores_com_lucro'] += 1

    rtp_observado = (resultados['total_ganho'] / resultados['total_apostado']) * 100
    percentual_lucro = (resultados['jogadores_com_lucro'] / NUM_JOGADORES) * 100

    print("\n=== RESULTADOS DA SIMULAÇÃO COM DEPÓSITO INICIAL ===")
    print(f"RTP Observado: {rtp_observado:.2f}%")
    print(f"Ganho médio líquido por jogador: R$ {np.mean(resultados['saldos_finais']):.2f}")
    print(f"Ganho máximo líquido observado: R$ {np.max(resultados['saldos_finais']):.2f}")
    print(f"Ganho mínimo líquido observado: R$ {np.min(resultados['saldos_finais']):.2f}")
    print(f"Percentual de jogadores que terminaram com lucro: {percentual_lucro:.2f}%")

    volatilidade_sessao = np.std(resultados['saldos_finais'])
    volatilidade_rodada = np.std(resultados['ganhos_rodadas'])

    print(f"Volatilidade do ganho por sessão: {volatilidade_sessao:.2f}")
    print(f"Volatilidade do ganho por rodada: {volatilidade_rodada:.2f}")

if __name__ == "__main__":
    main()
