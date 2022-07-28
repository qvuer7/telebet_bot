import json
import requests
import numpy as np
import os
import random
import secrets
import string

TOKEN = '123912-gFtKFSsVVWux0P' #qvuer7@gmail.com
TOKEN = '124424-mA7V9mfOcdhgJ7' #andriizelenko8@gmail.com
#TOKEN = '125008-8jleKNRpXOADcC' # might be azelenko671@gmail.com


def get_soccer_inplay_data():
    #skip esport url:
    url = f'https://api.b365api.com/v1/bet365/inplay_filter?token={TOKEN}&sport_id=1&skip_esports=1'
    url = f'https://api.b365api.com/v1/bet365/inplay_filter?token={TOKEN}&sport_id=1'
    resp = requests.get(url)


    data = soccer_data(resp.json())

    return data


class game_soccer:
    def __init__(self, result):
        # -----------information on the first stage InPlay Filter id search mostly-----------#
        self.data = result  #json(dict) of abstrac game info mentioned further -> dict

        self.league = self.data['league']  #dict of information about all avaliable leagues in play ->dict
        self.league_name = self.league['name']  #league name -> str
        self.league_id = self.league['id']  #league id -> str

        self.home = self.data['home']   #information abour home team -> dict
        self.home_id = self.home['id']  #home team id -> str
        self.home_name = self.home['name'] #home team name -> str

        self.away = self.data['away'] #information about away team -> dict
        self.away_id = self.away['id'] #away team id -> str
        self.away_name = self.away['name'] #away team name -> str

        self.current_score = self.data['ss'] #current score -> str

        self.betsapi_event_id = self.data['our_event_id'] #betsapi event id (not in use) -> str
        self.r_id = self.data['r_id'] #r_id event id -> str
        self.event_id = self.data['ev_id'] #event id -> str
        self.FI_id = self.data['id'] #main useful event id -> str

        #----------------------------------------------------------------------------------------#



    def __getattr__(self, item):
        return self.item

    def __print__(self):
        print(f'game: \n {self.home_name}  {self.current_score} {self.away_name} \n {self.FI_id}')

        print(f'betsapi id: {self.betsapi_event_id}\n r_id {self.r_id} \n event_id: {self.event_id} \n FI_id {self.FI_id}')

    def get_data_from_FI_id(self):

        url = f"https://api.b365api.com/v1/bet365/event?token={TOKEN}&FI={self.FI_id}"
        resp = requests.get(url)
        result = resp.json()
        self.PA_field = []
        c = 0
        for idx, data in  enumerate(result['results'][0]):
            if data['type'] == 'PA':
                if data['OD'] != '0/0':
                    od = data['OD'].split('/')
                    data['OD'] = round(int(od[0]) / int(od[1]) + 1, 2)
                self.PA_field.append(data)
                c+=1
            if c==3 : break


        return self.PA_field

    def get_WDL_odds_keyboard(self):
        if self.PA_field[0]['OD'] != '0/0':
            '''
            print(f"win1: {self.PA_field[0]['OD']} draw: {self.PA_field[1]['OD']} win2: {self.PA_field[2]['OD']}")
            od_left = self.PA_field[0]['OD'].split('/')
            od_draw = self.PA_field[1]['OD'].split('/')
            od_right = self.PA_field[2]['OD'].split('/')

            dec_cod_left = round(int(od_left[0]) / int(od_left[1]) + 1,2)
            dec_cod_draw = round(int(od_draw[0]) / int(od_draw[1]) + 1, 2)
            dec_cod_right = round(int(od_right[0]) / int(od_right[1]) + 1, 2)

            '''
            win_left_text = "П1:{}:{}".format(self.PA_field[0]['NA'], self.PA_field[0]['OD'])
            draw_text = "Ничья"+  ":{}".format(self.PA_field[1]['OD'])
            win_right_text = "П2:{}:{}".format(self.PA_field[2]['NA'],self.PA_field[2]['OD'])


            keyboard = [[win_left_text, draw_text, win_right_text], ['Назад к играм', 'Выйти']]


        else:
            keyboard = [['Назад', 'Выйти']]
        return keyboard

    def get_bet_by_ID(self, ID):
        for idx, data in enumerate(self.PA_field):
            if data['ID'] == ID:
                data['FI_id'] = self.FI_id
                data['home'] = self.home_name
                data['away'] = self.away_name
                data['league'] = self.league_name
                data['score'] = self.current_score
                return data

        return None









class soccer_data:
    def __init__(self, response):
        self.data = response
        self.games = []
        self.leagues = set()
        for result in response['results']:
            self.games.append(game_soccer(result))

            self.leagues.add(result['league']['name'])
        self.leagues = sorted(self.leagues)
        self.games.sort(key=lambda c: c.league_name)

    def get_leagues_keyboard(self):
        keyboard = list(self.leagues.copy())
        for idx, data in enumerate(keyboard):
            keyboard[idx] = 'Лига ' + data

        if len(keyboard)%2 == 0:
            keyboard= np.array(keyboard)
            keyboard = keyboard.reshape(len(keyboard)//2, 2)
            keyboard = keyboard.tolist()
        else:
            last = keyboard[-1]
            keyboard = np.array(keyboard[:-1])
            keyboard = keyboard.reshape(len(keyboard) // 2, 2)
            keyboard = keyboard.tolist()
            keyboard.append([last])
        keyboard.append(['Назад к категориям спорта', 'Выйти'])

        return keyboard

    def get_games_in_league(self, league):

        self.games_in_league = set()

        for game in self.games:
            if game.league_name == league:
                self.games_in_league.add(game)

        return self.games_in_league

    def get_games_keyboard(self):
        keyboard = []
        for game in list(self.games_in_league.copy()):
            keyboard.append([ 'Игра ' + str(game.home_name)+ ' - ' +str(game.away_name)])

        keyboard.append(['Назад к лигам', 'Выйти'])

        return keyboard
    def get_game_by_name(self, name):
        for idx, data in enumerate(self.games_in_league):
            match = str(data.home_name) + ' - ' + str(data.away_name)
            if match == name:
                return data
        return None



class User_data:

    def __init__(self, id):

        self.id = id
        self.path = f"../users/{self.id}.json"
        if str(self.id)+'.json' in os.listdir('../users'):
            self.file = json.load(open(self.path))
            self.balance = self.file['balance']
            self.open_bets = self.file['open_bets']
            self.closed_bets = self.file['closed_bets']

        else:
            self.balance = 0
            self.closed_bets = []
            self.open_bets = []
            with open(self.path, "w+") as outfile:
                json.dump({'balance':0,'open_bets':[], 'closed_bets': []}, outfile, indent = 4)
            self.file = json.load(open(self.path))

    def check_avaliable_balance(self, amount):
        if amount < 0:
            return False
        if self.balance >= amount:
            return True
        else:
            return False

    def add_open_bet(self, bet, amount):
        bet['amount'] = amount
        self.open_bets.append(bet)
        self.file['open_bets'] = self.open_bets

        with open(self.path, "w+") as outfile:
            json.dump(self.file, outfile, indent=4)

    def close_bet(self, bet):
        self.closed_bets.append(bet)
        self.file['closed_bets'] = self.closed_bets

        self.remove_open_bet(bet)
        with open(self.path, "w+") as outfile:
            json.dump(self.file, outfile, indent=4)


    def remove_open_bet(self, bet):
        self.open_bets.remove(bet)
        self.file['open_bets'] = self.open_bets
        with open(self.path, "w+") as outfile:
            json.dump(self.file, outfile, indent=4)


    def change_value(self, key, value):
        self.file[key] = value
        self.key = value
        with open(self.path, "w+") as outfile:
            json.dump(self.file, outfile, indent=4)

    def top_up(self, amount):
        self.balance+=amount
        self.file['balance'] = self.balance
        with open(self.path, "w+") as outfile:
            json.dump(self.file, outfile, indent=4)

    def write_to_file(self):
        self.file['balance'] = self.balance
        self.file['open_bets'] = self.open_bets
        self.file['closed_bets'] = self.closed_bets
        with open(self.path, "w+") as outfile:
            json.dump(self.file, outfile, indent=4)

    def close_bets(self):
        global TOKEN
        still_open_bets = []

        for idx, open_bet in enumerate(self.open_bets):

            id = open_bet['FI_id']
            url = f"https://api.b365api.com/v1/bet365/result?token={TOKEN}&event_id={id}"
            data = requests.get(url)
            data = data.json()
            data = data['results'][0]
            score = data['ss']
            score = score.replace('-', ' ')
            score = score.split()

            if data['time_status'] == '1' or data['time_status'] == '0':

                still_open_bets.append(open_bet)
            else:
                if int(score[0]) > int(score[1]):
                    bet_result = data['home']['name']
                elif int(score[0]) < int(score[1]):
                    bet_result = data['away']['name']
                else:
                    bet_result = 'Draw'
                if bet_result == open_bet['NA']:
                    open_bet['success'] = 1
                    self.balance += open_bet['OD'] * float(open_bet['amount'])
                    open_bet['score'] = [score[0], score[1]]
                    self.closed_bets.append(open_bet)
                else:
                    open_bet['success'] = 0
                    open_bet['score'] = [score[0], score[1]]
                    self.closed_bets.append(open_bet)

        self.open_bets = still_open_bets
        self.write_to_file()

    def get_info_about_closed_and_open_bets(self):
        new_line = '\n'
        text_open_bets = f"Открытые ставки {new_line}"
        text_closed_bets = f"Закрытые ставки {new_line}"

        for idx, open_bet in enumerate(self.open_bets):
            text_open_bets+= f"{idx+1} {open_bet['home']}  {open_bet['score'][0]}-{open_bet['score'][2]}  {open_bet['away']} {new_line}" \
                             f"Ставка: {open_bet['NA']}, коэффициент: {open_bet['OD']}, сумма ставки: {open_bet['amount']}"


        for idx, closed_bet in enumerate(self.closed_bets):
            if idx > 4: break
            if closed_bet['success'] == 1:
                add_text = f"Результат: выигрыш {float(closed_bet['amount'])*float(closed_bet['OD'])}"
            else:
                add_text = f"Результат: проигрыш"
            text_closed_bets += f"{idx+1} {closed_bet['home']}  {closed_bet['score'][0]}-{closed_bet['score'][1]}  {closed_bet['away']} {new_line}" \
                              f"Ставка: {closed_bet['NA']}, коэффициент: {closed_bet['OD']}, сумма ставки: {closed_bet['amount']} {new_line} " \
                                f"{add_text}"

        return f"{text_open_bets} {new_line} ---------------------- {new_line} {text_closed_bets}"


def generate_checks(num, amount):
    f = json.load(open("../payments/vauchers.json"))
    for i in range(num):
        vaucher = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(7))
        f[vaucher] = amount
    with open("../payments/vauchers.json", "w+") as outfile:
        json.dump(f, outfile, indent=4)

def check_voucher(vaucher):
    f = json.load(open("../payments/vauchers.json"))
    if vaucher in f.keys():
        return f[vaucher]
    else:
        return None

def redeem_vaucher(vaucher):
    f = json.load(open("../payments/vauchers.json"))
    del(f[vaucher])
    with open("../payments/vauchers.json", "w+") as outfile:
        json.dump(f, outfile, indent=4)








'''
data = get_soccer_inplay_data()
keyboard = data.get_leagues_keyboard()
league = data.leagues[0]

games = list(data.get_games_in_league(league))

game = str(games[0].home_name) + ' - '+ str(games[0].away_name)
gm = data.get_game_by_name(game)








url = f"https://api.b365api.com/v1/bet365/event?token={TOKEN}&FI={game.FI_id}"
resp = requests.get(url)
result = resp.json()
data = get_data_from_FI_id(resp.json())
print(data.types)
SC_type = data.get_type('SC')
MA_type = data.get_type('MA')
ES_type = data.get_type('ES')
TG_type = data.get_type('TG')

MG_type = data.get_type('MG')
TE_type = data.get_type('TE')
PA_type = data.get_type('PA')
EV_type = data.get_type('EV')

SL_type = data.get_type('SL')

print(f'SC type data: {SC_type}')
print(f'MA type data: {MA_type}')
print(f'ES type data: {ES_type}')
print(f'TG type data: {TG_type}')

print(f'MG type data: {MG_type}')
print(f'TE type data: {TE_type}')
print(f'PA type data: {PA_type}')
print(f'EV type data: {EV_type}')
print(f'SL type data: {SL_type}')

ods = data.get_odds()


print(ods)


'''