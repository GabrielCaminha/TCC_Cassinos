import random
import numpy as np
from tqdm import tqdm

# === Configuração do depósito inicial ===
DEPOSITO_INICIAL = 10.0  

# === Configuração das rodadas grátis ===
NUM_RODADAS_GRATIS = 25
APOSTA_FIXA = 0.5

# === Configuração dos símbolos ===
symbols = {
    "🐯": {"multiplier": 250, "weight": 1},
    "🏆": {"multiplier": 100, "weight": 2},
    "🍊": {"multiplier": 25,  "weight": 5},
    "🔑": {"multiplier": 10,  "weight": 4},
    "💰": {"multiplier": 8,   "weight": 7},
    "🧧": {"multiplier": 5,   "weight": 12},
    "🔭": {"multiplier": 3,   "weight": 44},
}

# === Geração do pool de símbolos ===
symbol_pool = []
for emoji, data in symbols.items():
    symbol_pool.extend([emoji] * data["weight"])

# === Paylines ===
paylines = [
    [(0, 0), (0, 1), (0, 2)],
    [(1, 0), (1, 1), (1, 2)],
    [(2, 0), (2, 1), (2, 2)],
    [(0, 0), (1, 1), (2, 2)],
    [(2, 0), (1, 1), (0, 2)]
]

# === Funções do jogo ===
def gerar_grade():
    return [[random.choice(symbol_pool) for _ in range(3)] for _ in range(3)]

def calcular_premio(grade, aposta_por_linha):
    ganho_total = 0
    simbolos_na_grade = [s for linha in grade for s in linha if s != "🐯"]
    simbolos_distintos = set(simbolos_na_grade)
    multiplicador_bonus = 10 if len(simbolos_distintos) <= 1 else 1

    for linha in paylines:
        simbolos = [grade[x][y] for x, y in linha]
        simbolos_reais = [s for s in simbolos if s != "🐯"]

        if not simbolos_reais or all(s == simbolos_reais[0] for s in simbolos_reais):
            simbolo_vencedor = simbolos_reais[0] if simbolos_reais else "🐯"
            multiplicador = symbols[simbolo_vencedor]["multiplier"]
            ganho_total += aposta_por_linha * multiplicador * multiplicador_bonus

    return ganho_total

def simular_jogador():
    linhas_ativas = len(paylines)
    aposta_por_linha = APOSTA_FIXA / linhas_ativas
    saldo = 0
    total_apostado = 0
    ganhos_por_rodada = []

    for _ in range(NUM_RODADAS_GRATIS):
        grade = gerar_grade()
        ganho = calcular_premio(grade, aposta_por_linha)
        saldo += ganho
        total_apostado += APOSTA_FIXA
        ganhos_por_rodada.append(ganho)

    return saldo, total_apostado, ganhos_por_rodada

# === Simulação ===
def main():
    NUM_JOGADORES = 100000
    resultados = {
        'saldos_finais': [],
        'total_apostado': 0,
        'total_ganho': 0,
        'ganhos_por_rodada': [],
        'jogadores_com_lucro': 0
    }

    for _ in tqdm(range(NUM_JOGADORES), desc="Simulando jogadores"):
        saldo_final, apostado, ganhos_por_rodada = simular_jogador()

        # Subtrai o depósito inicial do saldo final
        saldo_liquido = saldo_final - DEPOSITO_INICIAL

        resultados['saldos_finais'].append(saldo_liquido)
        resultados['total_apostado'] += apostado
        resultados['total_ganho'] += saldo_final
        resultados['ganhos_por_rodada'].extend(ganhos_por_rodada)

        # Contabiliza jogadores que ficaram com mais do que o depósito inicial
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
    volatilidade_rodada = np.std(resultados['ganhos_por_rodada'])

    print(f"Volatilidade do ganho por sessão: {volatilidade_sessao:.2f}")
    print(f"Volatilidade do ganho por rodada: {volatilidade_rodada:.2f}")

if __name__ == "__main__":
    main()
