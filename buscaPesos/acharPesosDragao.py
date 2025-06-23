import random
import numpy as np
from collections import defaultdict

# Configuração inicial dos símbolos (pesos serão calculados)
symbols = {
    "🐉": {"multiplier": 100},
    "🏆": {"multiplier": 50},
    "🍊": {"multiplier": 25},
    "🔑": {"multiplier": 10},
    "💰": {"multiplier": 5},
    "🧧": {"multiplier": 3},
    "🔭": {"multiplier": 2}
}

# Parâmetros fixos conforme o jogo original
aposta_total = 12.00
paylines = [
    [(0,0), (0,1), (0,2)],
    [(1,0), (1,1), (1,2)],
    [(2,0), (2,1), (2,2)],
    [(0,0), (1,1), (2,2)],
    [(2,0), (1,1), (0,2)]
]
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
        "🐉": 2,   
        "🏆": 3,   
        "🍊": 6,   
        "🔑": 10,  
        "💰": 15,  
        "🧧": 30,  
        "🔭": 50   
    }
    
    pesos = {}
    for simbolo, base in pesos_base.items():
        variacao = random.uniform(0.7, 1.3)  # Variação de ±30%
        pesos[simbolo] = max(1, int(base * variacao))
    
    return pesos

def gerar_config_cilindro():
    """Gera configurações balanceadas para os cilindros"""
    # Cilindro normal (base + variação)
    base_normal = {"1": 8, "2": 22, "5": 12, "10": 4}
    cilindro_normal = {}
    for k, v in base_normal.items():
        cilindro_normal[k] = max(1, int(v * random.uniform(0.8, 1.2)))
    
    # Cilindro fortuna (mais generoso)
    base_fortuna = {"1": 0, "2": 14, "5": 5, "10": 2}
    cilindro_fortuna = {}
    for k, v in base_fortuna.items():
        cilindro_fortuna[k] = max(0, int(v * random.uniform(0.8, 1.2)))  # 1x nunca aparece
    
    return cilindro_normal, cilindro_fortuna

def gerar_parametros_aleatorios():
    """Gera todos os parâmetros com abordagem balanceada"""
    pesos = gerar_pesos_balanceados()
    cilindro_normal, cilindro_fortuna = gerar_config_cilindro()
    
    # Probabilidades especiais com variação controlada
    chance_terceiro = round(0.2 * random.uniform(0.8, 1.2), 2)  # Base 20% ±20%
    prob_fortuna = round(0.02 * random.uniform(0.8, 1.2), 3)    # Base 2% ±20%
    
    return pesos, chance_terceiro, prob_fortuna, cilindro_normal, cilindro_fortuna

def simular_rodadas(params):
    """Simula o jogo completo com todos os parâmetros"""
    pesos, chance_terceiro, prob_fortuna, cilindro_normal, cilindro_fortuna = params
    
    # Configura o pool de símbolos
    symbol_pool = []
    for simbolo in symbols.keys():
        symbol_pool.extend([simbolo] * pesos[simbolo])
    
    total_ganho = 0
    rodadas_fortuna = 0
    rodada_da_fortuna = False
    
    def girar_cilindro():
        cilindro = cilindro_fortuna if rodada_da_fortuna else cilindro_normal
        return int(random.choices(list(cilindro.keys()), weights=cilindro.values(), k=1)[0])
    
    for _ in range(rodadas_por_teste):
        # Ativação da rodada da fortuna
        if not rodada_da_fortuna and rodadas_fortuna == 0:
            if random.random() < prob_fortuna:
                rodadas_fortuna = 8
                rodada_da_fortuna = True
        
        # Gera grade e calcula prêmio
        grade = [[random.choice(symbol_pool) for _ in range(3)] for _ in range(3)]
        
        # Calcula multiplicador do dragão
        if rodada_da_fortuna:
            mult = girar_cilindro() + girar_cilindro()
            if random.random() < chance_terceiro:
                mult += girar_cilindro()
        else:
            mult = girar_cilindro()
        
        # Verifica paylines
        ganho_rodada = 0
        for linha in paylines:
            simbolos = [grade[x][y] for x, y in linha]
            simbolos_reais = [s for s in simbolos if s != "🐉"]
            
            if not simbolos_reais or all(s == simbolos_reais[0] for s in simbolos_reais):
                simbolo = simbolos_reais[0] if simbolos_reais else "🐉"
                ganho_rodada += aposta_por_linha * symbols[simbolo]["multiplier"] * mult
        
        total_ganho += ganho_rodada
        
        # Atualiza estado da rodada da fortuna
        if rodada_da_fortuna:
            rodadas_fortuna -= 1
            if rodadas_fortuna <= 0:
                rodada_da_fortuna = False
    
    return (total_ganho / (rodadas_por_teste * aposta_total)) * 100

# Busca automática pelos melhores parâmetros
melhor_rtp = 0
melhores_parametros = None

for tentativa in range(tentativas_maximas):
    params = gerar_parametros_aleatorios()
    rtp = simular_rodadas(params)
    
    # Verifica se encontrou parâmetros ideais
    if abs(rtp - rtp_alvo) < abs(melhor_rtp - rtp_alvo):
        melhor_rtp = rtp
        melhores_parametros = {
            'pesos': params[0],
            'chance_terceiro_giro': params[1],
            'prob_rodada_fortuna': params[2],
            'cilindro_normal': params[3],
            'cilindro_fortuna': params[4]
        }
        
        print(f"Tentativa {tentativa+1}: RTP {rtp:.2f}%")
        
        if abs(rtp - rtp_alvo) <= margem_erro:
            break

# Resultados finais
print("\n⭐ Melhores parâmetros encontrados:")
print(f"RTP Alcançado: {melhor_rtp:.2f}%")

# Verificação final com 1 milhão de rodadas
print("\n🔍 Verificação final com 1.000.000 rodadas:")
params_verificacao = (
    melhores_parametros['pesos'],
    melhores_parametros['chance_terceiro_giro'],
    melhores_parametros['prob_rodada_fortuna'],
    melhores_parametros['cilindro_normal'],
    melhores_parametros['cilindro_fortuna']
)
rodadas_por_teste = 1000000
rtp_final = simular_rodadas(params_verificacao)
print(f"RTP na verificação: {rtp_final:.2f}%")

# Saída para implementação
print("\n💻 Configuração final para implementação:")
print("symbols = {")
for simbolo, data in symbols.items():
    print(f'    "{simbolo}": {{"multiplier": {data["multiplier"]}, "weight": {melhores_parametros["pesos"][simbolo]} }},')
print("}")

print("\n# Configurações do cilindro")
print("cilindro_normal = {")
for valor, peso in melhores_parametros['cilindro_normal'].items():
    print(f'    "{valor}": {peso},')
print("}")

print("\ncilindro_fortuna = {")
for valor, peso in melhores_parametros['cilindro_fortuna'].items():
    print(f'    "{valor}": {peso},')
print("}")

print(f"\nchance_terceiro_giro = {melhores_parametros['chance_terceiro_giro']}")
print(f"prob_rodada_da_fortuna = {melhores_parametros['prob_rodada_fortuna']}")