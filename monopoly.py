class Propriedade:
    def __init__(self, preco, aluguel):
        self.preco = preco
        self.aluguel = aluguel
        self.dono = None

class Tabuleiro:
    def __init__(self, config):
        self.propriedades = []
        for propriedade in propriedades:
            self.propriedades.append(Propriedade(propriedade['buy_price'], propriedade['rentPrice']))

class Jogador:
    def __init__(self, perfil):
        self.saldo = config['saldo_inicial']
        self.posicao = -1
        self.propriedades = []
        self.perfil = perfil
        self.bankrupt = False

import random

def jogar_dados():
    return random.randint(1, 6) + random.randint(1, 6)

def comprar_propriedade(jogador, propriedade):
    if jogador.saldo >= propriedade.preco:
        jogador.saldo -= propriedade.preco
        jogador.propriedades.append(propriedade)
        propriedade.dono = jogador
        return True
    return False


def pagar_aluguel(jogador, propriedade):
    if jogador.saldo >= propriedade.aluguel:
        jogador.saldo -= propriedade.aluguel
        propriedade.dono.saldo += propriedade.aluguel
    else:
        propriedade.dono.saldo += jogador.saldo
        jogador.saldo = 0
        jogador.bankrupt = True

def verificar_vencedor(jogadores):
    jogadores_ativos = [jogador for jogador in jogadores if not jogador.bankrupt]
    if len(jogadores_ativos) == 1:
        return jogadores_ativos[0]
    return None

def simular_rodada(jogador, tabuleiro):
    if not jogador.bankrupt:
        jogador.posicao = (jogador.posicao + jogar_dados()) % len(tabuleiro.propriedades)
        propriedade = tabuleiro.propriedades[jogador.posicao]
        if propriedade.dono is None:
            if jogador.perfil == 'cauteloso' and jogador.saldo - propriedade.preco >= config['saldo_restante_cauteloso']:
                comprar_propriedade(jogador, propriedade)
            elif jogador.perfil == 'impulsivo':
                comprar_propriedade(jogador, propriedade)
            elif jogador.perfil == 'aleatorio' and random.choice([True, False]):
                comprar_propriedade(jogador, propriedade)
            elif jogador.perfil == 'exigente' and propriedade.aluguel >= config['aluguel_exigente']:
                comprar_propriedade(jogador, propriedade)
        elif propriedade.dono != jogador:
            pagar_aluguel(jogador, propriedade)


def simular_partida(perfis):
    tabuleiro = Tabuleiro(config['propriedades'])
    jogadores = [Jogador(perfil) for perfil in perfis]
    random.shuffle(jogadores)  # Embaralha a ordem dos jogadores

    for _ in range(config['numero_rodadas']):
        for jogador in jogadores:
            simular_rodada(jogador, tabuleiro)
            vencedor = verificar_vencedor(jogadores)
            if vencedor:
                return vencedor.perfil

    return 'timeOut'

def executar_simulacoes():
    resultados = {
        'timeOut': 0,
        'cauteloso': 0,
        'impulsivo': 0,
        'aleatorio': 0,
        'exigente': 0
    }

    for _ in range(config['numero_simulacoes']):
        vencedor = simular_partida(perfis)
        resultados[vencedor if vencedor != 'timeOut' else vencedor] += 1

    return resultados

import json

def load_config(filename):
    with open(filename, 'r') as file:
        return json.load(file)

config = load_config('configs.json')
propriedades = config['propriedades']

perfis = ['cauteloso', 'impulsivo', 'aleatorio', 'exigente']
resultados = executar_simulacoes()

# Printando os resultados
print(f"Partidas encerradas por 'timeOut': {resultados['timeOut']}")
print(f"Vitórias do cauteloso: {resultados['cauteloso']}")
print(f"Vitórias do impulsivo: {resultados['impulsivo']}")
print(f"Vitórias do aleatório: {resultados['aleatorio']}")
print(f"Vitórias do exigente: {resultados['exigente']}")

perfil_vencedor = max(resultados, key=resultados.get)
print(f"Perfil que mais venceu: {perfil_vencedor}")
