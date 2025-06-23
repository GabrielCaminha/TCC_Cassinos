import random
import numpy as np
from tqdm import tqdm

# === Configuração do depósito inicial ===
DEPOSITO_INICIAL = 30.0  

# === Configuração das rodadas grátis ===
NUM_RODADAS_GRATIS = 10
APOSTA_FIXA = 0.4

# === Configuração dos símbolos ===
symbols = {
    "🐭": {"multiplier": 300, "weight": 2},
    "🏆": {"multiplier": 100, "weight": 2},
    "🍊": {"multiplier": 50,  "weight": 3},
    "🔑": {"multiplier": 30,  "weight": 10},
    "💰": {"multiplier": 15,  "weight": 11},
    "🧧": {"multiplier": 5,   "weight": 21},
    "🔭": {"multiplier": 3,   "weight": 57},
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
def gerar_grade_normal():
    return [[random.choice(symbol_pool) for _ in range(3)] for _ in range(3)]

def gerar_grade_rato_fortuna():
    grade = [[None for _ in range(3)] for _ in range(3)]
    for i in range(3):
        grade[i][1] = "🐭"
        grade[i][0] = random.choice(symbol_pool)
        grade[i][2] = random.choice(symbol_pool)
    return grade

def calcular_premio(grade, aposta_por_linha):
    todos_simbolos = [s for linha in grade for s in linha]
    if all(s == "🐭" for s in todos_simbolos):
        return aposta_por_linha * 1000 * len(paylines)

    ganho_total = 0
    for linha in paylines:
        simbolos = [grade[x][y] for x, y in linha]
        simbolos_sem_rato = [s for s in simbolos if s != "🐭"]

        if not simbolos_sem_rato:
            simbolo_vencedor = "🐭"
        elif all(s == simbolos_sem_rato[0] for s in simbolos_sem_rato):
            simbolo_vencedor = simbolos_sem_rato[0]
        else:
            continue

        ganho_total += aposta_por_linha * symbols[simbolo_vencedor]["multiplier"]

    return ganho_total

def simular_jogador():
    linhas_ativas = len(paylines)
    aposta_por_linha = APOSTA_FIXA / linhas_ativas
    saldo = 0
    total_apostado = 0
    ganhos_por_rodada = []
    modo_rato_fortuna = False
    prob_ativar_rato = 0.2

    # === Rodadas grátis ===
    for _ in range(NUM_RODADAS_GRATIS):
        if not modo_rato_fortuna and random.random() < prob_ativar_rato:
            modo_rato_fortuna = True

        grade = gerar_grade_rato_fortuna() if modo_rato_fortuna else gerar_grade_normal()
        ganho = calcular_premio(grade, aposta_por_linha)
        saldo += ganho
        total_apostado += APOSTA_FIXA
        ganhos_por_rodada.append(ganho)

        if modo_rato_fortuna and ganho > 0:
            modo_rato_fortuna = False

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

        # Subtrai o depósito inicial
        saldo_liquido = saldo_final - DEPOSITO_INICIAL

        resultados['saldos_finais'].append(saldo_liquido)
        resultados['total_apostado'] += apostado
        resultados['total_ganho'] += saldo_final
        resultados['ganhos_por_rodada'].extend(ganhos_por_rodada)

        # Contabiliza jogadores com lucro
        if saldo_final > DEPOSITO_INICIAL:
            resultados['jogadores_com_lucro'] += 1

    rtp_observado = (resultados['total_ganho'] / resultados['total_apostado']) * 100
    percentual_lucro = (resultados['jogadores_com_lucro'] / NUM_JOGADORES) * 100

    print("\n=== RESULTADOS DA SIMULAÇÃO COM DEPÓSITO INICIAL ===")
    print(f"RTP Observado : {rtp_observado:.2f}%")
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
