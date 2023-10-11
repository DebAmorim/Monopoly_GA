class Property:
    def __init__(self, buy_price, rent_price):
        self.buy_price = buy_price
        self.rent_price = rent_price
        self.owner = None

class Board:
    def __init__(self, config):
        self.properties = []
        for property in properties:
            self.properties.append(Property(property['buy_price'], property['rentPrice']))

class Player:
    def __init__(self, profile):
        self.coins = config['initial_coins']
        self.position = -1
        self.properties = []
        self.profile = profile
        self.bankrupt = False

class Classification:
    def __init__(self, coins, position, properties, profile):
        self.coins = coins
        self.position = position
        self.properties = properties
        self.profile = profile

import random

def roll_dices():
    return random.randint(1, 6) + random.randint(1, 6)

def buy_property(player, property):
    if player.coins >= property.buy_price:
        player.coins -= property.buy_price
        player.properties.append(property)
        property.owner = player
        return True
    return False


def pay_rent(player, property, players):
    if player.coins >= property.rent_price:
        player.coins -= property.rent_price
        property.owner.coins += property.rent_price
    else:
        active_players = [player for player in players if not player.bankrupt]
        classifications.append(Classification(player.coins, len(active_players), player.properties, player.profile))
        property.owner.coins += player.coins
        player.coins = 0
        player.bankrupt = True
        print(f"Bankrupt: {player.profile}")
        for property in player.properties:
            property.owner = None
        

def get_player_balance(player):
    balance = player.coins
    for property in player.properties:
        balance += property.buy_price
    return balance

def update_classification(players):
    player_balances = [(get_player_balance(player), player) for player in players]

    player_balances.sort(reverse=True, key=lambda x: x[0])

    for i, (balance, player) in enumerate(player_balances, start=1):
        classification = Classification(balance, i, player.properties, player.profile)
        classifications.append(classification)

def get_winner():
    for classification in classifications:
        if classification.position == 1:
            return classification.profile

def check_winner(players, round):
    active_palyers = [player for player in players if not player.bankrupt]
    if len(active_palyers) == 1:
        classifications.append(Classification(active_palyers[0].coins, 1, active_palyers[0].properties, active_palyers[0].profile))
        return active_palyers[0]
    elif config['number_of_rounds']-1 == round:
        print(f"Time out - active players: {len(active_palyers)}")
        update_classification(active_palyers)
        return get_winner()

        # for player in players:
        #     if get_player_balance(player) > get_player_balance(jogador_vitorioso):
        #         if jogador_vitorioso != None:
        #             classifications.append(Classification(player.coins, 1, player.properties, player.profile))
        #             classifications.append(Classification(jogador_vitorioso.coins, 2, jogador_vitorioso.properties, jogador_vitorioso.profile))
        #         jogador_vitorioso = player
        # return jogador_vitorioso
    return None

def check_full_turn(old_position, new_position, player):
    if new_position < old_position:
        player.coins += config['full_turn_coins']

def execute_round(player, board, players):
    if not player.bankrupt:
        old_position = player.position
        player.position = (player.position + roll_dices()) % len(board.properties)
        new_position = player.position
        check_full_turn(old_position, new_position, player)
        property = board.properties[player.position]
        if property.owner is None:
            if player.profile == 'cautious' and player.coins - property.buy_price >= config['cautious_remaining_balance']:
                buy_property(player, property)
            elif player.profile == 'impulsive':
                buy_property(player, property)
            elif player.profile == 'random' and random.choice([True, False]):
                buy_property(player, property)
            elif player.profile == 'demmanding' and property.rent_price >= config['demmanding_rent']:
                buy_property(player, property)
            
        elif property.owner != player:
            pay_rent(player, property, players)


def execute_match(profiles):
    board = Board(config['properties'])
    players = [Player(profile) for profile in profiles]
    random.shuffle(players)

    for round in range(config['number_of_rounds']):
        for player in players:
            execute_round(player, board, players)
            vencedor = check_winner(players, round)
            if vencedor:
                for property in board.properties:
                    if property.owner != None:
                        print(f"Winner's property: {property.buy_price}, owner: {property.owner.profile}")
                        
                return vencedor

def play():

    for _ in range(config['number_of_matches']):
        execute_match(profiles)

        for classification in classifications:
            print()
            print(f'Position: {classification.position}, Profile: {classification.profile}, Coins: {classification.coins}, Properties: ')
            for property in classification.properties:
                print(f"Property: price: {property.buy_price}, rent: {property.rent_price}")
    return classifications

import json

def load_config(filename):
    with open(filename, 'r') as file:
        return json.load(file)
    
classifications = []
config = load_config('configs.json')
properties = config['properties']

profiles = ['cautious', 'impulsive', 'random', 'demmanding']
play()


