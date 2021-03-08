import network
import urequests
import time
import ntptime
import json
import os
import uos
import webrepl
import utime
from machine import UART
from time import gmtime
from machine import RTC
import sys


APNAME = ''
PASSWORD = ''
#END = '\n'
SERIALSPEED = 19200
coingeckorequest = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_last_updated_at=true'

uart = UART(0, baudrate=SERIALSPEED, timeout=1000)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)


uos.dupterm(None, 1)

rtc = RTC()

def sendserial(command):
  uart.write(str(command))
  uart.write(str("*"))
  #uart.write('\n')

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
              wlan.connect(APNAME, PASSWORD)
      time.sleep(10)
      ntptime.settime()
    else:
      sendserial(".")
  else:
    ntptime.settime()
    sendserial(str(rtc.datetime()))

    #sendserial(".")
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
    #sendserial("BTCT" + str(response['bitcoin']['last_updated_at']))
    formattedtime = utime.localtime(response['bitcoin']['last_updated_at'])
    formattedtime = str(formattedtime[3]) + ":" + str("{:02d}".format(formattedtime[4]))
    sendserial("BTCT" + "Last:  " + str(formattedtime) + " UTC")
  if response['ethereum']['last_updated_at'] == eth_last_call_timestamp:
    pass
  else:
    printprice("ETHP", response['ethereum']['usd'])
    formattedtime = utime.localtime(response['ethereum']['last_updated_at'])
    formattedtime = str(formattedtime[3]) + ":" + str("{:02d}".format(formattedtime[4]))
    #sendserial("ETHT" + str(response['ethereum']['last_updated_at']))
    sendserial("ETHT" + "Last:  " + str(formattedtime) + " UTC")
  eth_last_call_timestamp = response['ethereum']['last_updated_at']
  btc_last_call_timestamp = response['bitcoin']['last_updated_at']
  return btc_last_call_timestamp, eth_last_call_timestamp

while True:
  check_connection()
  btc_last_call_timestamp, eth_last_call_timestamp = update(btc_last_call_timestamp, eth_last_call_timestamp)
  calltimer = 5
  while calltimer > 0:
    input = uart.read(500)
    #input = uart.readline()
    if input == bytes('UPDA', 'utf-8'):
      btc_last_call_timestamp, eth_last_call_timestamp = update(btc_last_call_timestamp, eth_last_call_timestamp)
    elif input == bytes('WIFIGO', 'utf-8'):
      sendserial("OKNEWWIFI...")
      PASSWORD = '.'
      AP = '.'
      wlan.active(False)
      wlan.active(True)
      wlan.connect(APNAME, PASSWORD)
    elif (input == bytes('WIFI', 'utf-8')):
      uart.write(str('WIFI'))
      sendserial(str(wlan.ifconfig()))
    else:
      pass
      #uart.write(str(input))
    time.sleep(7)
    calltimer -= 1
