import random
import numpy as np
from tqdm import tqdm

# === Configurações do Cashback ===
cashback_percentual = 10        
rollover_multiplicador = 3    
valor_maximo = 300000000000000000

# === Configuração dos símbolos ===
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

def girar_cilindro(rodada_da_fortuna):
    cylinder = {
        "1":  {"multiplier": 1,  "weight": 0 if rodada_da_fortuna else 10},
        "2":  {"multiplier": 2,  "weight": 12 if rodada_da_fortuna else 24},
        "5":  {"multiplier": 5,  "weight": 5 if rodada_da_fortuna else 15},
        "10": {"multiplier": 10, "weight": 3 if rodada_da_fortuna else 4},
    }
    opcoes = list(cylinder.keys())
    pesos = [cylinder[k]["weight"] for k in opcoes]
    return int(random.choices(opcoes, weights=pesos, k=1)[0])

def gerar_grade():
    return [[random.choice(symbol_pool) for _ in range(3)] for _ in range(3)]

def calcular_multiplicador(rodada_da_fortuna):
    if rodada_da_fortuna:
        m1 = girar_cilindro(True)
        m2 = girar_cilindro(True)
        m3 = girar_cilindro(True) if random.random() < chance_terceiro_giro else 0
        return m1 + m2 + m3
    else:
        return girar_cilindro(False)

def calcular_premio(grade, aposta_por_linha, multiplicador_dragao):
    ganho_total = 0
    for linha in paylines:
        simbolos = [grade[x][y] for x, y in linha]
        simbolos_sem_dragao = [s for s in simbolos if s != "🐉"]
        if not simbolos_sem_dragao or all(s == simbolos_sem_dragao[0] for s in simbolos_sem_dragao):
            simbolo_vencedor = simbolos_sem_dragao[0] if simbolos_sem_dragao else "🐉"
            ganho = aposta_por_linha * symbols[simbolo_vencedor]["multiplier"] * multiplicador_dragao
            ganho_total += ganho
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

    rodada_da_fortuna = False
    rodadas_fortuna = 0

    # Escolhe aposta entre 10% e 20% do cashback, arredondado para múltiplo de 0.5
    percentual_escolhido = random.uniform(0.10, 0.20)
    aposta_fixa = round(percentual_escolhido * cashback / 0.5) * 0.5
    if aposta_fixa < 0.5:
        aposta_fixa = 0.5

    while saldo >= 0.5:
        # Se o saldo não permite a aposta fixa, aposta o mínimo possível (múltiplo de 0.5)
        if saldo >= aposta_fixa:
            aposta_total = aposta_fixa
        else:
            aposta_total = round(saldo / 0.5) * 0.5
            if aposta_total < 0.5:
                break

        aposta_por_linha = aposta_total / linhas_ativas

        saldo -= aposta_total
        total_apostado += aposta_total

        if not rodada_da_fortuna and rodadas_fortuna == 0:
            if random.random() < prob_rodada_da_fortuna:
                rodada_da_fortuna = True
                rodadas_fortuna = 8

        multiplicador_dragao = calcular_multiplicador(rodada_da_fortuna)
        grade = gerar_grade()
        ganho = calcular_premio(grade, aposta_por_linha, multiplicador_dragao)

        saldo += ganho
        total_ganho += ganho
        ganhos_por_rodada.append(ganho)
        rodadas += 1

        if rodada_da_fortuna:
            rodadas_fortuna -= 1
            if rodadas_fortuna <= 0:
                rodada_da_fortuna = False

        if total_apostado >= cashback * rollover_multiplicador:
            atingiu_rollover = True
            break

    lucro_final = saldo - cashback
    return lucro_final, rodadas, total_apostado, total_ganho, ganhos_por_rodada, atingiu_rollover

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
        resultados['ganhos_rodadas'].extend(ganhos_por_rodada)
        resultados['rodadas_por_jogador'].append(rodadas)
        resultados['atingiu_rollover'] += int(rollover)

    rtp = (resultados['total_ganho'] / resultados['total_apostado']) * 100 if resultados['total_apostado'] > 0 else 0
    media_percentual_lucro = np.mean([lucro / (saldo_inicial * (cashback_percentual / 100))
                                       for lucro, saldo_inicial in zip(resultados['lucros'], saldos_iniciais)]) * 100
    perc_atingiu_rollover = (resultados['atingiu_rollover'] / NUM_JOGADORES) * 100

    lucros_relativos = [lucro / (saldo_inicial * (cashback_percentual / 100))
                         for lucro, saldo_inicial in zip(resultados['lucros'], saldos_iniciais)]
    volatilidade_sessao = np.std(lucros_relativos)

    ganhos_relativos_rodada = [ganho / 0.5 if ganho > 0 else 0 for ganho in resultados['ganhos_rodadas']]
    volatilidade_rodada = np.std(ganhos_relativos_rodada)

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
