import requests
import json
import asyncio
from json_reader import User_data, get_soccer_inplay_data

TOKEN = '123912-gFtKFSsVVWux0P' #qvuer7@gmail.com
TOKEN = '124424-mA7V9mfOcdhgJ7' #andriizelenko8@gmail.com
#TOKEN = '125008-8jleKNRpXOADcC' # might be azelenko671@gmail.com



User = User_data(682847115)


id = User.open_bets[0]['FI_id']
url = f"https://api.b365api.com/v1/bet365/result?token={TOKEN}&event_id={id}"
resp = requests.get(url)
result = resp.json()
result = result['results'][0]














'''
for idx, data in enumerate(User.open_bets):
    
    if 'success' in data.keys():
        User.closed_bets.append(data)
        User.top_up(data['amount']*data['OD'])
    else:
        
        
'''


get_bet_result(User)




#time_status: 1 - in process, 3-finished, 0 - upcoming
