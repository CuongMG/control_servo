import requests as r


url = 'https://control-servo-c8729-default-rtdb.firebaseio.com/.json'

json = {'angle': 20}

a = 50

json['angle'] = int(a)
res = r.put(url=url, json=json)

