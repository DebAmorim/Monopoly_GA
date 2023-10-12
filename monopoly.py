'''
Classes

'''

class Property:
    def __init__(self, buy_price, rent_price, color, name, full_set):
        self.buy_price = buy_price
        self.rent_price = rent_price
        self.color = color
        self.name = name
        self.owner = None
        self.full_set = full_set

class Board:
    def __init__(self, config):
        self.properties = []
        for property in properties:
            self.properties.append(Property(property['buy_price'], property['rentPrice'], property['color'], property['name'], property['full_set']))

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

class colors:
    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

'''
Functions - utils

'''

import random
import json
from prettytable import PrettyTable
import logging
import datetime
import os

now = datetime.datetime.now()
date_time = now.strftime("%Y%m%d_%H%M%S")
file_name = f'execution_{date_time}.log'
path = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(path, 'logs')
complete_path = os.path.join(log_path, file_name)

if not os.path.exists(log_path):
    os.makedirs(log_path)

logging.basicConfig(filename=complete_path, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def roll_dices():
    return random.randint(1, 6) + random.randint(1, 6)

def buy_property(player, property, properties):
    if player.coins >= property.buy_price:
        player.coins -= property.buy_price
        player.properties.append(property)
        property.owner = player
        logging.warning(f"{player.profile} bought property: {property.name} | Coins available: {player.coins}")
        # print(f"{player.profile} bought property: {property.name} | Coins available: {player.coins}")
        check_full_set(property, properties)
        return True
    return False

def get_player_balance(player):
    balance = player.coins
    for property in player.properties:
        balance += property.buy_price
    return balance

def make_coins_transfer(total, payer, receiver):
    payer.coins -= total
    receiver.coins -= total
    logging.debug(f"{receiver.profile} received {total} from {payer.profile} | Coins available: {receiver.coins}")
    # print(f"{receiver.profile} received {total} from {payer.profile} | Coins available: {receiver.coins}")

def sell_properties(property, properties, player, debt):
    logging.warning(f"{player.profile} is selling properties to pay a debt of {debt}:")
    # print(f"{player.profile} is selling properties to pay a debt of {debt}:")
    remaining_amount_to_pay = debt - player.coins
    properties_available = []

    #separating properties considering if part of a full set or not
    #because sell a full set property is not the best option
    not_full_set_properties = []
    full_set_properties = []
    for prop in player.properties:
        if prop.full_set:
            full_set_properties.append(prop)
        else:
            not_full_set_properties.append(prop)

    #sorting properties to sell the less valuable first
    sorted_full_set_properties = sorted(full_set_properties, key=lambda x: x.buy_price)
    sorted_not_full_set_properties = sorted(not_full_set_properties, key=lambda x: x.buy_price)
        
    if len(sorted_not_full_set_properties) > 0:
        for prop in sorted_not_full_set_properties:
            properties_available.append(prop)
    if len(sorted_full_set_properties) > 0:
        for prop in sorted_full_set_properties:
            properties_available.append(prop)
    
    #will be avilable to sale the quantity necessary to pay de debt
    properties_to_sale = []
    enough_amount = 0
    for prop in properties_available:
        properties_to_sale.append(prop)
        prop.full_set = False
        prop.owner = None
        player.properties.remove(prop)
        enough_amount += prop.buy_price
        logging.warning(f"sold property: {prop.name}, price: {prop.buy_price}")
        # print(f"sold property: {prop.name}, price: {prop.buy_price}")
        if enough_amount >= remaining_amount_to_pay:
            break

def pay_rent(player, property, players):
    total_rent = property.rent_price
    if property.full_set:
        total_rent = total_rent * 4
    logging.warning(f"{player.profile} has to pay rent({total_rent}) for {property.owner.profile} | Coins before paying: {player.coins}")
    # print(f"{player.profile} has to pay rent({total_rent}) for {property.owner.profile} | Coins before paying: {player.coins}")
    if player.coins >= total_rent:
        make_coins_transfer(total_rent, player, property.owner)
        # player.coins -= total_rent
        # property.owner.coins += total_rent
    else:
        if len(player.properties) > 0 and get_player_balance(player) > total_rent:
            make_coins_transfer(player.coins, player, property.owner)
            sell_properties(property, properties, player, total_rent)
        else:
            declare_bankruptcy(player, players, property)

def declare_bankruptcy(player, players, property):
    active_players = [player for player in players if not player.bankrupt]
    classifications.append(Classification(player.coins, len(active_players), player.properties, player.profile))
    if property.owner != None:
        property.owner.coins += player.coins
    player.coins = 0
    player.bankrupt = True
    logging.error(f"Bankrupt: {player.profile}, coins: {player.coins}")
    # print(f"Bankrupt: {player.profile}, coins: {player.coins}")
    for property in player.properties:
        property.owner = None
        property.full_set = False

def pay_income_tax(player, property, players):
    logging.warning(f"{player.profile} has to pay income tax ({property.rent_price}) | Coins before paying: {player.coins}")
    # print(f"{player.profile} has to pay income tax ({property.rent_price}) | Coins before paying: {player.coins}")
    if player.coins >= property.rent_price:
        player.coins -= property.rent_price
    else:
        if len(player.properties) > 0 and get_player_balance(player) > property.rent_price:
            player.coins = 0
            sell_properties(property, properties, player, property.rent_price)
        else:
            declare_bankruptcy(player, players, property)

        
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
        logging.error(f"Time out - active players: {len(active_palyers)}")
        # print(f"Time out - active players: {len(active_palyers)}")
        update_classification(active_palyers)
        return get_winner()

    return None

def check_full_turn(old_position, new_position, player):
    if new_position < old_position:
        player.coins += config['full_turn_coins']
        logging.debug(f"{player.profile} received coins for full turn ({config['full_turn_coins']}) | Coins available: {player.coins} ")
        # print(f"{player.profile} received coins for full turn ({config['full_turn_coins']}) | Coins available: {player.coins} ")

def check_income_tax(position, board, player, players):
    if board.properties[position].name == 'Imposto de Renda':
        return True
    return False

def check_full_set(property, properties):
    #getting all the same color properties
    same_color_properties = []
    for prop in properties:
        if prop.color == property.color:
            same_color_properties.append(prop)

    #getting all the same owner properties
    same_owner_properties = []
    for prop in same_color_properties:
        if prop.owner == property.owner:
            same_owner_properties.append(prop)

    #checking if all the properties of same color has the same owner, if so, then it's a full set
    if len(same_color_properties) == len(same_owner_properties):
        for prop in properties:
            if prop.owner == property.owner and prop.color == property.color:
                prop.full_set = True
        logging.info(f"It's a FULL SET")
        # print(f"It's a FULL SET")
        return True
    else:
        logging.info(f"It's NOT a full set")
        # print(f"It's NOT a full set")
        return False

def decide_to_buy(player, property, coeficients):
    remaining_balance = player.coins - property.buy_price

    #Checking if the property to buy has the same color of one the player already has
    same_color = 0
    for prop in player.properties:
        if prop.color == property.color:
            same_color = 1
            break

    
    min_remaining_balance = 0
    if remaining_balance>=config['cautious_remaining_balance']:
        min_remaining_balance = 1

    min_rent_price = 0
    if property.rent_price >= config['demmanding_rent']:
        min_rent_price = 1

    impulsivity = 1

    decision = coeficients[0]*(min_remaining_balance) + coeficients[1]*(min_rent_price) + coeficients[2]*(same_color) + coeficients[3]*impulsivity
    if decision > 0:
        return True
    else:
        return False



'''
Functions - game

'''

def execute_round(player, board, players, coeficients):
    if not player.bankrupt:
        old_position = player.position
        player.position = (player.position + roll_dices()) % len(board.properties)
        new_position = player.position
        property = board.properties[player.position]
        logging.info(f"{player.profile} is at {property.name} | Coins available {player.coins}")
        # print(f"{player.profile} is at {property.name} | Coins available {player.coins}")

        check_full_turn(old_position, new_position, player)

        if check_income_tax(new_position, board, player, players):
            pay_income_tax(player, property, players)

        elif property.owner == None:
            if player.profile == 'CAUTIOUS' and player.coins - property.buy_price >= config['cautious_remaining_balance']:
                buy_property(player, property, board.properties)
            elif player.profile == 'IMPULSIVE':
                buy_property(player, property, board.properties)
            elif player.profile == 'RANDOM' and random.choice([True, False]):
                buy_property(player, property, board.properties)
            elif player.profile == 'DEMMANDING' and property.rent_price >= config['demmanding_rent']:
                buy_property(player, property, board.properties)
            elif player.profile == 'GA' and decide_to_buy(player, property, coeficients):
                buy_property(player, property, board.properties)
            
        elif property.owner != player:
            pay_rent(player, property, players)

def execute_match(profiles, coeficients):
    board = Board(config['properties'])
    players = [Player(profile) for profile in profiles]
    random.shuffle(players)

    for round in range(config['number_of_rounds']):
        for player in players:
            execute_round(player, board, players, coeficients)
            vencedor = check_winner(players, round)
            if vencedor:                        
                for player in players:
                    if player.profile == 'GA':
                        return player

def play(coeficients):

    logging.info("######################################################")
    logging.info(f"MATCH PARAMETERS:")
    logging.info(f"INITIAL_COINS: {config['initial_coins']}")
    logging.info(f"CAUTIOUS_REMAINING_BALANCE: {config['cautious_remaining_balance']}")
    logging.info(f"MAX_ROUNDS: {config['number_of_rounds']}")
    logging.info(f"FULL_TURN_COINS: {config['full_turn_coins']}")
    logging.info(f"DEMMANDING_RENT: {config['demmanding_rent']}")
    logging.info('')
    logging.info(f"GA PARAMETERS:")
    logging.info(f"MIN_RENT: {config['demmanding_rent']}")
    logging.info(f"REMAINING_BALANCE: {config['cautious_remaining_balance']}")
    logging.info(f"COEFICIENT 0: {coeficients[0]}")
    logging.info(f"COEFICIENT 1: {coeficients[1]}")
    logging.info(f"COEFICIENT 2: {coeficients[2]}")
    logging.info(f"COEFICIENT 3: {coeficients[3]}")
    logging.info("######################################################")
    logging.info('')
    logging.info('')

    for _ in range(config['number_of_matches']):
        GA_player = execute_match(profiles, coeficients)
        GA_position = 0

        for classification in classifications:
            print()
            print(colors.BLUE + f'{classification.position} - {classification.profile}, Coins: {classification.coins}\nProperties: ' + colors.RESET)

            logging.info('')
            logging.info("######################################################")
            logging.info(f'{classification.position} - {classification.profile}, Coins: {classification.coins}\nProperties: ') 

            table = PrettyTable()
            table.field_names = [f"{colors.GREEN}Color{colors.RESET}", f"{colors.GREEN}Name{colors.RESET}", f"{colors.GREEN}Rent Price{colors.RESET}", f"{colors.GREEN}Buy Price{colors.RESET}"]
            

            for property in classification.properties:
                table.add_row([property.color, property.name, property.rent_price, property.buy_price])
                logging.info(f"{property.color} - {property.name} - rent: { property.rent_price}")
            print(table)
            if classification.profile == "GA":
                GA_position = classification.position
                
        
        
            


        GA_classification = 0
        GA_classification = get_player_balance(GA_player) + 1000 * (5 - GA_position + 1)

        print(f"GA profile: {GA_player.profile}")
        print(f"GA balance: {get_player_balance(GA_player)}")
        print(f"GA position: {GA_position}")

    print(GA_classification)
    return GA_classification


'''
Declarations

'''

classifications = []
config = load_config('configs.json')
properties = config['properties']
profiles = ['CAUTIOUS', 'IMPULSIVE', 'RANDOM', 'DEMMANDING', 'GA']
coeficients = [0.5, 0.5, 0.5, 0.5]

# play(coeficients)


