import random
import os
import msvcrt

# Configuração dos símbolos e pesos ajustados para RTP ≈ 96.8%
symbols = {
    "🐭": {"multiplier": 300, "weight": 5},  
    "🏆": {"multiplier": 100, "weight": 2},
    "🍊": {"multiplier": 50,  "weight": 5},
    "🔑": {"multiplier": 30,  "weight": 5},
    "💰": {"multiplier": 15,   "weight": 6},
    "🧧": {"multiplier": 5,   "weight": 55},
    "🔭": {"multiplier": 3,   "weight": 92},
}

symbol_pool = []
for emoji, data in symbols.items():
    symbol_pool.extend([emoji] * data["weight"])

paylines = [
    [(0,0), (0,1), (0,2)],
    [(1,0), (1,1), (1,2)],
    [(2,0), (2,1), (2,2)],
    [(0,0), (1,1), (2,2)],
    [(2,0), (1,1), (0,2)]
]

# Parâmetros do jogo
saldo = 264.00
aposta_total = 4.00
linhas_ativas = len(paylines)
aposta_por_linha = aposta_total / linhas_ativas
rodadas = 0
total_ganho = 0
modo_rato_fortuna = False

# Funções principais
def gerar_grade_completa():
    return [[random.choice(symbol_pool) for _ in range(3)] for _ in range(3)]

def gerar_grade_rato_fortuna():
    grade = [[None for _ in range(3)] for _ in range(3)]
    for i in range(3):
        grade[i][1] = "🐭"  # Coluna do meio = coringa
        grade[i][0] = random.choice(symbol_pool)
        grade[i][2] = random.choice(symbol_pool)
    return grade

def calcular_premio(grade):
    # Verifica se todos os símbolos da grade são ratos
    todos_simbolos = [s for linha in grade for s in linha]
    if all(s == "🐭" for s in todos_simbolos):
        return aposta_por_linha * 1000

    ganho_total = 0
    for linha in paylines:
        simbolos = [grade[x][y] for x, y in linha]

        # Contagem dos símbolos ignorando ratos
        simbolos_sem_rato = [s for s in simbolos if s != "🐭"]

        if not simbolos_sem_rato:
            # Todos são ratos: pode considerar qualquer símbolo, escolhemos rato
            simbolo_vencedor = "🐭"
        elif all(s == simbolos_sem_rato[0] for s in simbolos_sem_rato):
            simbolo_vencedor = simbolos_sem_rato[0]
        else:
            continue  

        multiplicador = symbols[simbolo_vencedor]["multiplier"]
        ganho_total += aposta_por_linha * multiplicador

    return ganho_total


def mostrar_grade(grade):
    for linha in grade:
        print(" | ".join(linha))

def tentar_ativar_rato_fortuna():
    chance_ativar = 0.1  # 10% de chance de ativar
    return random.random() < chance_ativar

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
    print(f"🎰 RODADA {rodadas + 1}")

    if not modo_rato_fortuna and tentar_ativar_rato_fortuna():
        print("🧀 RATO DA FORTUNA ATIVADO! Coluna do meio é coringa!")
        modo_rato_fortuna = True

    if modo_rato_fortuna:
        grade = gerar_grade_rato_fortuna()
    else:
        grade = gerar_grade_completa()

    ganho = calcular_premio(grade)
    saldo -= aposta_total
    saldo += ganho
    total_ganho += ganho
    rodadas += 1

    mostrar_grade(grade)
    print(f"\n💸 Ganhou: R$ {ganho:.2f}")
    print(f"💰 Saldo: R$ {saldo:.2f}")
    rtp_atual = (total_ganho / (rodadas * aposta_total)) * 100
    print(f"📊 RTP Atual: {rtp_atual:.2f}%")

    # Se houve ganho e estávamos no modo rato da fortuna, ele se desativa
    if ganho > 0 and modo_rato_fortuna:
        print("🐭 Rato da Fortuna desativado após vitória!")
        modo_rato_fortuna = False

print("\n❌ Saldo insuficiente. Fim de jogo!")
