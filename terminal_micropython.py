import network
import urequests
import time
import json
import os
import uos
import webrepl
import utime
from machine import UART
from time import gmtime
import sys

APNAME = ''
PASSWORD = ''
END = '\n'
SERIALSPEED = 19200
coingeckorequest = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_last_updated_at=true'

uart = UART(0, baudrate=SERIALSPEED, timeout=1000)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
#time.sleep(3)
#print("\n", end="")

uos.dupterm(None, 1)

def sendserial(command):
  #print(command, end=END)
  uart.write(str(command))
  uart.write(str("*"))
  #uart.write('\n')

#def get_serial():
# s = uart.read(500)
# if (s != bytes('', 'utf-8')):
#   #print(s.decode())
#   return s

def callcg():
  while True:
    try:
      response=urequests.get(coingeckorequest)
      response = json.loads(response.content.decode('utf-8'))
      return response
    except:
      print("CGCALLFAIL")
      utime.sleep(10)


def check_connection():
  while (wlan.isconnected() == False):
    sendserial("NOCO")
    input = uart.readline()
    if input != None:
      decoded_input = input.decode("utf-8")
      if (decoded_input[0:3] == "AP:"):
        apstop = decoded_input.find('\r')
        if (apstop > 1):
          APNAME = decoded_input[3:apstop]
          if (decoded_input[apstop+1:apstop+6] == "PASS:"):
            pwstop = decoded_input.find('\r', apstop+6)
            if (pwstop > 1):
              PASSWORD = decoded_input[apstop+6:pwstop]
              sendserial("got apname:")
              sendserial(APNAME)
              sendserial("got password:")
              sendserial(PASSWORD)
              wlan.connect(APNAME, PASSWORD)
      time.sleep(10)
    else:
      sendserial(".")
    #wlan.connect(APNAME, PASSWORD)
    #time.sleep(20)
  else:
    sendserial(".")
    pass

calltimer = 60
pushtimer = 60
listentimer = 1
temptimer = 0
btc_last_call_timestamp = 0
eth_last_call_timestamp = 0


def printprice(prefix, value):
  if (type(value) is float):
    value = int(value)
    #formatted_price = prefix + "$" + '{:,.0f}'.format(value)
    formatted_price = prefix + "$" + '{:,}'.format(value)
  elif (type(value) is int):
    formatted_price = prefix + "$" + '{:,}'.format(value)
  sendserial(formatted_price)


def update(btc_last_call_timestamp, eth_last_call_timestamp):
  response = callcg()
  if response['bitcoin']['last_updated_at'] == btc_last_call_timestamp:
    pass
  else:
    printprice("BTCP", response['bitcoin']['usd'])
    sendserial("BTCT" + str(response['bitcoin']['last_updated_at']))
  if response['ethereum']['last_updated_at'] == eth_last_call_timestamp:
    pass
  else:
    printprice("ETHP", response['ethereum']['usd'])
    sendserial("ETHT" + str(response['ethereum']['last_updated_at']))
  eth_last_call_timestamp = response['ethereum']['last_updated_at']
  btc_last_call_timestamp = response['bitcoin']['last_updated_at']
  #sendserial("#")
  return btc_last_call_timestamp, eth_last_call_timestamp

while True:
  check_connection()
  btc_last_call_timestamp, eth_last_call_timestamp = update(btc_last_call_timestamp, eth_last_call_timestamp)
  calltimer = 5
  while calltimer > 0:
    input = uart.read(500)
    #input = uart.readline()
    #sendserial(input)
    #input = uart.read(100)
    if input == bytes('UPDA', 'utf-8'):
      btc_last_call_timestamp, eth_last_call_timestamp = update(btc_last_call_timestamp, eth_last_call_timestamp)
      #uart.write(str('NEON'))
    elif input == bytes('WIFIGO', 'utf-8'):
      sendserial("OKNEWWIFI...")
    elif (input == bytes('WIFI', 'utf-8')):
      uart.write(str('WIFI'))
      sendserial(str(wlan.ifconfig()))
    else:
      pass
      #uart.write(str(input))
    time.sleep(7)
    calltimer -= 1
