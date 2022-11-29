import requests as request
import time

counter = 0
while True:
    request.get('http://1f96-107-216-52-202.ngrok.io/notify')
    print('Ping ' + str(counter))
    counter += 1
    time.sleep(30)
