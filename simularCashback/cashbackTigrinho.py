import random
import numpy as np
from tqdm import tqdm

# === Configurações do cashback ===
cashback_percentual = 10        
rollover_multiplicador = 3    
valor_maximo = 300000000000000000

# === Configuração dos símbolos ===
symbols = {
    "🐯": {"multiplier": 250, "weight": 1},
    "🏆": {"multiplier": 100, "weight": 2},
    "🍊": {"multiplier": 25, "weight": 5},
    "🔑": {"multiplier": 10, "weight": 4},
    "💰": {"multiplier": 8, "weight": 7},
    "🧧": {"multiplier": 5, "weight": 12},
    "🔭": {"multiplier": 3, "weight": 44},
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

def simular_jogador(saldo_inicial):
    cashback = min((saldo_inicial * (cashback_percentual / 100)), valor_maximo)
    saldo = cashback
    linhas_ativas = len(paylines)
    total_apostado = 0
    total_ganho = 0
    rodadas = 0
    ganhos_por_rodada = []
    atingiu_rollover = False

    # === Escolha da aposta fixa, entre 10% e 20% do cashback, arredondado para múltiplo de 0.5 ===
    percentual_escolhido = random.uniform(0.10, 0.20)
    aposta_fixa = round(percentual_escolhido * cashback / 0.5) * 0.5
    if aposta_fixa < 0.5:
        aposta_fixa = 0.5

    while saldo >= 0.5:
        # Se o saldo não permite a aposta fixa, aposta o máximo possível, mas nunca abaixo de 0.5
        if saldo >= aposta_fixa:
            aposta_total = aposta_fixa
        else:
            aposta_total = round(saldo / 0.5) * 0.5
            if aposta_total < 0.5:
                break

        aposta_por_linha = aposta_total / linhas_ativas

        saldo -= aposta_total
        total_apostado += aposta_total

        grade = gerar_grade()
        ganho = calcular_premio(grade, aposta_por_linha)
        saldo += ganho
        total_ganho += ganho
        ganhos_por_rodada.append((ganho, aposta_por_linha))

        rodadas += 1

        if total_apostado >= cashback * rollover_multiplicador:
            atingiu_rollover = True
            break

    lucro_final = saldo - cashback
    return lucro_final, rodadas, total_apostado, total_ganho, ganhos_por_rodada, atingiu_rollover

# === Simulação ===
def main():
    NUM_JOGADORES = 1000000
    media_salario = 354

    saldos_iniciais = np.round(np.clip(np.random.normal(media_salario, 50, NUM_JOGADORES), 10, 1000), 2)

    resultados = {
        'lucros': [],
        'rodadas': [],
        'total_apostado': 0,
        'total_ganho': 0,
        'ganhos_rodadas': [],
        'rodadas_por_jogador': [],
        'atingiu_rollover': 0
    }

    for i in tqdm(range(NUM_JOGADORES), desc="Simulando jogadores"):
        lucro, rodadas, apostado, ganho, ganhos_por_rodada, rollover = simular_jogador(saldos_iniciais[i])
        resultados['lucros'].append(lucro)
        resultados['rodadas'].append(rodadas)
        resultados['total_apostado'] += apostado
        resultados['total_ganho'] += ganho
        resultados['ganhos_rodadas'].extend([(g, aposta) for g, aposta in ganhos_por_rodada])
        resultados['rodadas_por_jogador'].append(rodadas)
        resultados['atingiu_rollover'] += int(rollover)

    # === Estatísticas principais ===
    rtp = (resultados['total_ganho'] / resultados['total_apostado']) * 100 if resultados['total_apostado'] > 0 else 0
    media_percentual_lucro = np.mean([lucro / (saldo_inicial * (cashback_percentual / 100))
                                       for lucro, saldo_inicial in zip(resultados['lucros'], saldos_iniciais)]) * 100
    perc_atingiu_rollover = (resultados['atingiu_rollover'] / NUM_JOGADORES) * 100

    # === Volatilidade ===
    lucros_relativos = [lucro / (saldo_inicial * (cashback_percentual / 100))
                         for lucro, saldo_inicial in zip(resultados['lucros'], saldos_iniciais)]
    volatilidade_sessao = np.std(lucros_relativos)

    ganhos_relativos_rodada = [ganho / aposta if aposta > 0 else 0 for ganho, aposta in resultados['ganhos_rodadas']]
    volatilidade_rodada = np.std(ganhos_relativos_rodada)

    # === Impressão dos resultados ===
    print("\n=== RESULTADOS DA SIMULAÇÃO COM CASHBACK ===")
    print(f"RTP Observado: {rtp:.2f}%")
    print(f"Média de rodadas por jogador: {np.mean(resultados['rodadas']):.2f}")
    print(f"Média de lucro/prejuízo em relação ao cashback: {media_percentual_lucro:.2f}%")
    print(f"Lucro médio absoluto: R$ {np.mean(resultados['lucros']):.2f}")
    print(f"Jogadores que atingiram o rollover: {resultados['atingiu_rollover']} ({perc_atingiu_rollover:.4f}%)")
    print(f"\nVolatilidade do lucro por sessão (relativo ao cashback): {volatilidade_sessao:.4f}")
    print(f"Volatilidade do ganho por rodada (relativo à aposta): {volatilidade_rodada:.4f}")

if __name__ == "__main__":
    main()
