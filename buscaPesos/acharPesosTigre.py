import random
import numpy as np

# Configuração dos símbolos
symbols = {
    "🐯": {"multiplier": 250},
    "🏆": {"multiplier": 100},
    "🍊": {"multiplier": 25},
    "🔑": {"multiplier": 10},
    "💰": {"multiplier": 8},
    "🧧": {"multiplier": 5},
    "🔭": {"multiplier": 3},
}

paylines = [
    [(0,0), (0,1), (0,2)],
    [(1,0), (1,1), (1,2)],
    [(2,0), (2,1), (2,2)],
    [(0,0), (1,1), (2,2)],
    [(2,0), (1,1), (0,2)]
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
        "🐯": 1,
        "🏆": 2,
        "🍊": 4,
        "🔑": 8,
        "💰": 10,
        "🧧": 20,
        "🔭": 30
    }
    
    pesos = {}
    for simbolo, base in pesos_base.items():
        variacao = random.uniform(0.7, 1.3)  # Variação de ±30%
        pesos[simbolo] = max(1, int(base * variacao))
    
    return pesos

def gerar_grade(symbol_pool):
    return [[random.choice(symbol_pool) for _ in range(3)] for _ in range(3)]

def calcular_premio(grade):
    ganho_total = 0
    simbolos_na_grade = [s for linha in grade for s in linha if s != "🐯"]
    simbolos_distintos = set(simbolos_na_grade)
    multiplicador_bonus = 10 if len(simbolos_distintos) <= 1 else 1

    for linha in paylines:
        simbolos = [grade[x][y] for x, y in linha]
        simbolos_reais = [s for s in simbolos if s != "🐯"]

        if not simbolos_reais or all(s == simbolos_reais[0] for s in simbolos_reais):
            simbolo_vencedor = simbolos_reais[0] if simbolos_reais else "💰"
            multiplicador = symbols[simbolo_vencedor]["multiplier"]
            ganho_total += aposta_por_linha * multiplicador * multiplicador_bonus

    return ganho_total

def simular_rtp(pesos):
    symbol_pool = []
    for emoji, peso in pesos.items():
        symbol_pool.extend([emoji] * peso)
    
    total_ganho = 0
    for _ in range(rodadas_por_teste):
        grade = gerar_grade(symbol_pool)
        total_ganho += calcular_premio(grade)
    
    return (total_ganho / (rodadas_por_teste * aposta_total)) * 100

# Busca automática
melhor_rtp = 0
melhores_pesos = {}

for tentativa in range(tentativas_maximas):
    pesos = gerar_pesos_balanceados()
    rtp = simular_rtp(pesos)

    if abs(rtp - rtp_alvo) < abs(melhor_rtp - rtp_alvo):
        melhor_rtp = rtp
        melhores_pesos = pesos
        print(f"Tentativa {tentativa+1}: RTP {rtp:.2f}%")

        if abs(rtp - rtp_alvo) <= margem_erro:
            break

# Verificação final com 1 milhão de rodadas
rodadas_por_teste = 1000000
rtp_final = simular_rtp(melhores_pesos)

# Resultados
print("\n📊 Resultado Final:")
print(f"RTP na verificação: {rtp_final:.2f}%")
print("\n🔢 Pesos finais sugeridos:")
for simbolo, peso in melhores_pesos.items():
    print(f"{simbolo}: peso {peso}")

print("\n💻 Configuração final:")
print("symbols = {")
for simbolo, dados in symbols.items():
    print(f'    "{simbolo}": {{"multiplier": {dados["multiplier"]}, "weight": {melhores_pesos[simbolo]} }},')
print("}")