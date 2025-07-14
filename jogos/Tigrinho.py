import random
import os
import time
import msvcrt

# Configuração dos símbolos e pesos ajustados para RTP ≈ 96.8%
symbols = {
    "🐯": {"multiplier": 250, "weight": 1 },
    "🏆": {"multiplier": 100, "weight": 2 },
    "🍊": {"multiplier": 25, "weight": 5 },
    "🔑": {"multiplier": 10, "weight": 4 },
    "💰": {"multiplier": 8, "weight": 7 },
    "🧧": {"multiplier": 5, "weight": 12 },
    "🔭": {"multiplier": 3, "weight": 44 },
}

# Geração do pool de símbolos com base nos pesos
symbol_pool = []
for emoji, data in symbols.items():
    symbol_pool.extend([emoji] * data["weight"])

# Paylines (linhas premiadas)
paylines = [
    [(0,0), (0,1), (0,2)],
    [(1,0), (1,1), (1,2)],
    [(2,0), (2,1), (2,2)],
    [(0,0), (1,1), (2,2)],
    [(2,0), (1,1), (0,2)]
]

# Parâmetros do jogo
saldo = 264.00
aposta_total =4.00
linhas_ativas = len(paylines)
aposta_por_linha = aposta_total / linhas_ativas
rodadas = 0
total_ganho = 0

# Funções principais
def gerar_grade():
    return [[random.choice(symbol_pool) for _ in range(3)] for _ in range(3)]

def calcular_premio(grade):
    ganho_total = 0

    # Verifica a quantidade de símbolos únicos (ignorando tigres)
    simbolos_na_grade = [s for linha in grade for s in linha if s != "🐯"]
    simbolos_distintos = set(simbolos_na_grade)
    multiplicador_bonus = 10 if len(simbolos_distintos) <= 1 else 1

    for linha in paylines:
        simbolos = [grade[x][y] for x, y in linha]
        simbolos_reais = [s for s in simbolos if s != "🐯"]

        if not simbolos_reais or all(s == simbolos_reais[0] for s in simbolos_reais):
            if simbolos_reais:
                simbolo_vencedor = simbolos_reais[0]
            else:
                simbolo_vencedor = "🐯"
            multiplicador = symbols[simbolo_vencedor]["multiplier"]
            ganho_total += aposta_por_linha * multiplicador * multiplicador_bonus

    return ganho_total

def mostrar_grade(grade):
    for linha in grade:
        print(" | ".join(linha))

# Loop principal do jogo
while saldo >= aposta_total:
    if rodadas > 0:
        print("Pressione ESPAÇO para girar ou ESC para sair.")
        key = msvcrt.getch()
        if key == b'\x1b':  # ESC
            break
        if key != b' ':
            continue

    os.system('cls' if os.name == 'nt' else 'clear')
    grade = gerar_grade()
    ganho = calcular_premio(grade)
    saldo -= aposta_total
    saldo += ganho
    total_ganho += ganho
    rodadas += 1

    print(f"🎰 RODADA {rodadas}")
    mostrar_grade(grade)
    print(f"\n💶 Apostou: R$ {aposta_total:.2f}")
    print(f"💸 Ganhou: R$ {ganho:.2f}")
    print(f"💰 Saldo: R$ {saldo:.2f}")
    rtp_atual = (total_ganho / (rodadas * aposta_total)) * 100
    print(f"📊 RTP Atual: {rtp_atual:.2f}%")

print("\n❌ Saldo insuficiente. Fim de jogo!")
