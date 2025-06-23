import random
import os
import msvcrt

# Configuração dos símbolos e pesos ajustados para RTP ≈ 96.8%
symbols = {
    "🐉": {"multiplier": 100, "weight": 1 },
    "🏆": {"multiplier": 50, "weight": 2 },
    "🍊": {"multiplier": 25, "weight": 8 },
    "🔑": {"multiplier": 10, "weight": 20 },
    "💰": {"multiplier": 5, "weight": 30 },
    "🧧": {"multiplier": 3, "weight": 39 },
    "🔭": {"multiplier": 2, "weight": 61 },
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
rodada_da_fortuna = False  

#Usado para criar a probabilidade do terceiro multiplicador nas rodadas da fortuna
chance_terceiro_giro = 0.21
prob_rodada_da_fortuna = 0.03
rodadas_fortuna = 0


# Funções principais
def gerar_grade():
    return [[random.choice(symbol_pool) for _ in range(3)] for _ in range(3)]

# Girar Cilindro (Exclusivo do Fortune Dragon)

def girar_cilindro():
    cylinder = {
        "1":  {"multiplier": 1,  "weight": 0 if rodada_da_fortuna else 10},
        "2":  {"multiplier": 2,  "weight": 12 if rodada_da_fortuna else 24},
        "5":  {"multiplier": 5,  "weight": 5 if rodada_da_fortuna else 15},
        "10": {"multiplier": 10, "weight": 3  if rodada_da_fortuna else 4},
    }
    opcoes = list(cylinder.keys())
    pesos = [cylinder[key]["weight"] for key in opcoes]
    return int(random.choices(opcoes, weights=pesos, k=1)[0])

def acionar_fortuna():
    global prob_rodada_da_fortuna, rodadas_fortuna
    if random.random() < prob_rodada_da_fortuna:
        rodadas_fortuna = 8
        return True
    return False


def calcular_premio(grade):
    global visualizar_multi, rodadas_fortuna
    multiplicador_dragao = (
        (girar_cilindro() + girar_cilindro() + (girar_cilindro() if random.random() < chance_terceiro_giro else 0))
        if rodada_da_fortuna
        else girar_cilindro()
    )
    visualizar_multi = multiplicador_dragao
    ganho_total = 0
    # Verifica a quantidade de símbolos únicos 
    for linha in paylines:
        simbolos = [grade[x][y] for x, y in linha]
        simbolos_reais = [s for s in simbolos if s != "🐉"]

        if not simbolos_reais or all(s == simbolos_reais[0] for s in simbolos_reais):
            if simbolos_reais:
                simbolo_vencedor = simbolos_reais[0]
            else:
                simbolo_vencedor = "🐉"
            multiplicador = symbols[simbolo_vencedor]["multiplier"]
            ganho_total += aposta_por_linha * multiplicador * multiplicador_dragao

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

    # Ativação/controle da rodada da fortuna (antes de calcular prêmio)
    if not rodada_da_fortuna and rodadas_fortuna == 0:
        if acionar_fortuna():   # acionar_fortuna já atualiza rodadas_fortuna
            rodada_da_fortuna = True

    os.system('cls' if os.name == 'nt' else 'clear')
    grade = gerar_grade()
    ganho = calcular_premio(grade)
    
    # Decrementa as rodadas da fortuna após o cálculo do prêmio
    if rodada_da_fortuna:
        rodadas_fortuna -= 1
        if rodadas_fortuna <= 0:
            rodada_da_fortuna = False

    saldo -= aposta_total
    saldo += ganho
    total_ganho += ganho
    rodadas += 1

    print(f"🎰 RODADA {rodadas}")
    mostrar_grade(grade)
    print(f"\n💸 Ganhou: R$ {ganho:.2f}")
    print(f"💰 Saldo: R$ {saldo:.2f}")
    print(f"✖️  Multiplicador:{visualizar_multi}")
    print(f"🤑  Rodadas da Fortuna!!") if rodada_da_fortuna else None
    print(f"Restam: {rodadas_fortuna} rodadas") if rodada_da_fortuna else None
    rtp_atual = (total_ganho / (rodadas * aposta_total)) * 100
    print(f"📊 RTP Atual: {rtp_atual:.2f}%")

print("\n❌ Saldo insuficiente. Fim de jogo!")

