import random
import numpy as np
from tqdm import tqdm

# === Configurações da simulacao ===
rollover = 25
multiplicador_bonus_inicial = 2
limite_bonus = 300
somente_bonus =  False
# Configuração dos símbolos
symbols = {
    "🐯": {"multiplier": 250, "weight": 1},  
    "🏆": {"multiplier": 100, "weight": 2},
    "🍊": {"multiplier": 25, "weight": 5},
    "🔑": {"multiplier": 10, "weight": 4},
    "💰": {"multiplier": 8, "weight": 7},
    "🧧": {"multiplier": 5, "weight": 12},
    "🔭": {"multiplier": 3, "weight": 44},
}

# Geração do pool de símbolos
symbol_pool = []
for emoji, data in symbols.items():
    symbol_pool.extend([emoji] * data["weight"])

# Paylines
paylines = [
    [(0,0), (0,1), (0,2)],
    [(1,0), (1,1), (1,2)],
    [(2,0), (2,1), (2,2)],
    [(0,0), (1,1), (2,2)],
    [(2,0), (1,1), (0,2)]
]

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

def simular_jogador(saldo_inicial, aposta_total, max_rodadas=1000):
    saldo_multiplicado = saldo_inicial * multiplicador_bonus_inicial
    saldo = saldo_multiplicado if saldo_multiplicado < limite_bonus else limite_bonus+saldo_inicial
    rodadas = 0
    linhas_ativas = len(paylines)
    aposta_por_linha = aposta_total / linhas_ativas
    total_ganho = 0
    ganhos_rodada = []
    total_apostado = 0
    if somente_bonus == False:
        meta_apostas = rollover * (saldo_multiplicado if saldo_multiplicado < limite_bonus else limite_bonus+saldo_inicial)
    else:
        meta_apostas = rollover * ((saldo_multiplicado-saldo_inicial) if saldo_multiplicado < limite_bonus else limite_bonus)

    while saldo >= aposta_total and rodadas < max_rodadas:
        saldo -= aposta_total
        total_apostado += aposta_total

        grade = gerar_grade()
        ganho = calcular_premio(grade, aposta_por_linha)
        saldo += ganho
        total_ganho += ganho
        ganhos_rodada.append(ganho)
        rodadas += 1

        if total_apostado >= meta_apostas:
            lucro_rel_multiplicado = saldo - saldo_multiplicado
            lucro_rel_inicial = saldo - saldo_inicial
            return lucro_rel_multiplicado, lucro_rel_inicial, rodadas, True, total_ganho, ganhos_rodada, saldo

    lucro_rel_multiplicado = saldo - saldo_multiplicado
    lucro_rel_inicial = saldo - saldo_inicial
    return lucro_rel_multiplicado, lucro_rel_inicial, rodadas, False, total_ganho, ganhos_rodada, saldo

def main():
    NUM_JOGADORES = 100000
    media_salario = 354
    media_aposta = 12

    saldos_iniciais = np.round(np.clip(np.random.normal(media_salario, 50, NUM_JOGADORES), 10, 1000), 2)
    apostas = np.round(np.clip(np.random.normal(media_aposta, 5, NUM_JOGADORES), 0.5, 40) * 2) / 2

    resultados = {
        'lucros_multiplicado': [],
        'lucros_inicial': [],
        'rodadas': [],
        'atingiu_rollover': 0,
        'total_apostado': 0,
        'total_ganho': 0,
        'ganhos_rodadas': [],
        'lucros_validos': []  
    }

    for i in tqdm(range(NUM_JOGADORES), desc="Simulando jogadores"):
        lucro_mult, lucro_ini, rodadas, rollover_atingido, total_ganho, ganhos_rodada, saldo_final = simular_jogador(saldos_iniciais[i], apostas[i])
        resultados['lucros_multiplicado'].append(lucro_mult)
        resultados['lucros_inicial'].append(lucro_ini)
        resultados['rodadas'].append(rodadas)
        resultados['atingiu_rollover'] += int(rollover_atingido)
        resultados['total_apostado'] += apostas[i] * rodadas
        resultados['total_ganho'] += total_ganho
        resultados['ganhos_rodadas'].extend(ganhos_rodada)

        if rollover_atingido and saldo_final > saldos_iniciais[i]:
            resultados['lucros_validos'].append(lucro_ini)

    rtp = (resultados['total_ganho'] / resultados['total_apostado']) * 100
    positivos = len(resultados['lucros_validos'])
    negativos = NUM_JOGADORES - positivos

    print("\n=== RESULTADOS DA SIMULAÇÃO ===")
    print(f"RTP Observado: {rtp:.2f}%")
    print(f"Jogadores com lucro : {positivos} ({positivos/NUM_JOGADORES*100:.1f}%)")
    print(f"Jogadores com prejuízo : {negativos} ({negativos/NUM_JOGADORES*100:.1f}%)")
    print(f"Jogadores que atingiram o rollover: {resultados['atingiu_rollover']} ({resultados['atingiu_rollover']/NUM_JOGADORES*100:.4f}%)")
    print(f"Média de rodadas: {np.mean(resultados['rodadas']):.1f}")
    print(f"Lucro médio (relativo ao saldo com bônus): R$ {np.mean(resultados['lucros_multiplicado']):.2f}")
    print(f"Lucro médio (relativo ao saldo inicial): R$ {np.mean(resultados['lucros_inicial']):.2f}")

    lucros_relativos = [lucro / (aposta if aposta > 0 else 1) for lucro, aposta in zip(resultados['lucros_multiplicado'], apostas)]
    volatilidade_sessao = np.std(lucros_relativos)

    ganhos_relativos_rodada = [ganho / aposta for ganho, aposta, rodada in zip(
        resultados['ganhos_rodadas'],
        np.repeat(apostas, resultados['rodadas']),
        resultados['ganhos_rodadas']
    )]
    volatilidade_rodada = np.std(ganhos_relativos_rodada)

    print(f"\nVolatilidade do lucro por sessão (relativo à aposta): {volatilidade_sessao:.4f}")
    print(f"Volatilidade do ganho por rodada (relativo à aposta): {volatilidade_rodada:.4f}")

if __name__ == "__main__":
    main()
