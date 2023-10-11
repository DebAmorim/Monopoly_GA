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

class Classification:
    def __init__(self, coins, position, properties, profile):
        self.coins = coins
        self.position = position
        self.properties = properties
        self.profile = profile

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


def pagar_aluguel(jogador, propriedade, jogadores):
    if jogador.saldo >= propriedade.aluguel:
        jogador.saldo -= propriedade.aluguel
        propriedade.dono.saldo += propriedade.aluguel
    else:
        active_players = [jogador for jogador in jogadores if not jogador.bankrupt]
        classifications.append(Classification(jogador.saldo, len(active_players), jogador.propriedades, jogador.perfil))
        propriedade.dono.saldo += jogador.saldo
        jogador.saldo = 0
        jogador.bankrupt = True
        for property in jogador.propriedades:
            property.dono = None
        

def calcula_saldo_total_jogador(jogador):
    saldo_total = jogador.saldo
    for propriedade in jogador.propriedades:
        saldo_total += propriedade.preco
    return saldo_total

def verificar_vencedor(jogadores, rodada):
    jogadores_ativos = [jogador for jogador in jogadores if not jogador.bankrupt]
    if len(jogadores_ativos) == 1:
        classifications.append(Classification(jogadores_ativos[0].saldo, 1, jogadores_ativos[0].propriedades, jogadores_ativos[0].perfil))
        return jogadores_ativos[0]
    elif config['numero_rodadas']-1 == rodada:
        jogador_vitorioso = None
        for jogador in jogadores:
            if calcula_saldo_total_jogador(jogador) > calcula_saldo_total_jogador(jogador_vitorioso):
                if jogador_vitorioso != None:
                    classifications.append(Classification(jogador.saldo, 1, jogador.propriedades, jogador.perfil))
                    classifications.append(Classification(jogador_vitorioso.saldo, 2, jogador_vitorioso.propriedades, jogador_vitorioso.perfil))
                jogador_vitorioso = jogador
        return jogador_vitorioso
    return None

def simular_rodada(jogador, tabuleiro, jogadores):
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
            pagar_aluguel(jogador, propriedade, jogadores)


def simular_partida(perfis):
    tabuleiro = Tabuleiro(config['propriedades'])
    jogadores = [Jogador(perfil) for perfil in perfis]
    random.shuffle(jogadores)  # Embaralha a ordem dos jogadores

    for rodada in range(config['numero_rodadas']):
        # print(f"rodada atual: {rodada}")
        for jogador in jogadores:
            simular_rodada(jogador, tabuleiro, jogadores)
            vencedor = verificar_vencedor(jogadores, rodada)
            if vencedor:
                for propriedade in tabuleiro.propriedades:
                    if propriedade.dono != None:
                        print(f"Propriedade do vencedor: {propriedade.preco}, dono: {propriedade.dono.perfil}")
                        
                return vencedor.perfil

def executar_simulacoes():

    for _ in range(config['numero_simulacoes']):
        simular_partida(perfis)
        # Ordenando a lista com base no atributo 'position'
        sorted_classifications = sorted(classifications, key=lambda x: x.position)

        for classification in classifications:
            print()
            print(f'Position: {classification.position}, Profile: {classification.profile}, Coins: {classification.coins}, Properties: ')
            for property in classification.properties:
                print(f"Propriedade: preço: {property.preco}, aluguel: {property.aluguel}")
    return classifications

import json

def load_config(filename):
    with open(filename, 'r') as file:
        return json.load(file)
    
classifications = []
config = load_config('configs.json')
propriedades = config['propriedades']

perfis = ['cauteloso', 'impulsivo', 'aleatorio', 'exigente']
executar_simulacoes()


