import random
import numpy as np

# Configuração dos símbolos
symbols = {
    "🐭": {"multiplier": 300},
    "🏆": {"multiplier": 100},
    "🍊": {"multiplier": 50},
    "🔑": {"multiplier": 30},
    "💰": {"multiplier": 15},
    "🧧": {"multiplier": 5},
    "🔭": {"multiplier": 3},
}

paylines = [
    [(0,0), (0,1), (0,2)],
    [(1,0), (1,1), (1,2)],
    [(2,0), (2,1), (2,2)],
    [(0,0), (1,1), (2,2)],
    [(2,0), (1,1), (0,2)],
]

# Parâmetros fixos
aposta_total = 4.00
linhas_ativas = len(paylines)
aposta_por_linha = aposta_total / linhas_ativas

# Parâmetros de simulação
rtp_alvo = 96.8
margem_erro = 0.5
rodadas_por_teste = 100000
tentativas_maximas = 1000

def gerar_pesos_balanceados():
    """Gera pesos com base em valores referenciais + variação controlada"""
    pesos_base = {
        "🐭": 2,   
        "🏆": 3,
        "🍊": 5,
        "🔑": 8,
        "💰": 12,
        "🧧": 30,
        "🔭": 50
    }
    
    pesos = {}
    for simbolo, base in pesos_base.items():
        variacao = random.uniform(0.7, 1.3)  # Variação de ±30%
        pesos[simbolo] = max(1, int(base * variacao))
    
    prob_fortuna = round(random.uniform(0.05, 0.25), 3)
    
    return pesos, prob_fortuna

def gerar_grade_normal(symbol_pool):
    return [[random.choice(symbol_pool) for _ in range(3)] for _ in range(3)]

def gerar_grade_rato_fortuna(symbol_pool):
    grade = [[None for _ in range(3)] for _ in range(3)]
    for i in range(3):
        grade[i][1] = "🐭"  # Wild na coluna do meio
        grade[i][0] = random.choice(symbol_pool)
        grade[i][2] = random.choice(symbol_pool)
    return grade

def calcular_premio(grade):
    # Jackpot especial (todos símbolos iguais)
    todos = [s for linha in grade for s in linha]
    if all(s == "🐭" for s in todos):
        return aposta_por_linha * 1000
    
    ganho = 0
    for linha in paylines:
        simbolos = [grade[x][y] for x, y in linha]
        sem_rato = [s for s in simbolos if s != "🐭"]
        
        if not sem_rato:
            simbolo = "🐭"
        elif all(s == sem_rato[0] for s in sem_rato):
            simbolo = sem_rato[0]
        else:
            continue
        
        ganho += aposta_por_linha * symbols[simbolo]["multiplier"]
    return ganho

def simular_jogo(pesos, prob_fortuna):
    symbol_pool = []
    for emoji, p in pesos.items():
        symbol_pool.extend([emoji] * p)

    total_ganho = 0
    modo_fortuna = False
    rodadas_fortuna = 0

    for _ in range(rodadas_por_teste):
        if not modo_fortuna and random.random() < prob_fortuna:
            modo_fortuna = True
            rodadas_fortuna = 8

        grade = gerar_grade_rato_fortuna(symbol_pool) if modo_fortuna else gerar_grade_normal(symbol_pool)
        ganho = calcular_premio(grade)
        total_ganho += ganho

        if modo_fortuna:
            rodadas_fortuna -= 1
            if rodadas_fortuna <= 0 or ganho > 0:
                modo_fortuna = False

    return (total_ganho / (rodadas_por_teste * aposta_total)) * 100

# Busca automática
melhor_rtp = 0
melhor_config = {}

for tentativa in range(tentativas_maximas):
    pesos, prob_fortuna = gerar_pesos_balanceados()
    rtp = simular_jogo(pesos, prob_fortuna)

    if abs(rtp - rtp_alvo) < abs(melhor_rtp - rtp_alvo):
        melhor_rtp = rtp
        melhor_config = {'pesos': pesos, 'prob_fortuna': prob_fortuna}
        print(f"Tentativa {tentativa + 1}: RTP = {rtp:.2f}%")

        if abs(rtp - rtp_alvo) <= margem_erro:
            break

# Validação final com 1 milhão de rodadas
rodadas_por_teste = 1000000
rtp_validacao = simular_jogo(melhor_config['pesos'], melhor_config['prob_fortuna'])

# Saída
print("\n✅ Configuração final encontrada:")
print(f"RTP final: {rtp_validacao:.2f}%")
print(f"Probabilidade da rodada do rato da fortuna: {melhor_config['prob_fortuna']}")
print("Pesos finais dos símbolos:")
for s, data in symbols.items():
    print(f'    "{s}": {{"multiplier": {data["multiplier"]}, "weight": {melhor_config["pesos"][s]}}},')