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
      sendserial("CGCALLFAIL")
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
      #try:
      # ntptime.settime()
      #except:
      # sendserial("NTPFAIL")
    else:
      sendserial("x")
  else:
    try:
      ntptime.settime()
      #sendserial(str(rtc.datetime()))
      sendserial(".")
      pass
    except:
      sendserial("NTPFAIL")

realoffset = 0
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

def get_utc_offset(input):
  if len(input) == 5:
    value = int(input[4])
    if input[3] == '-':
      value = value * -1
    return value
  elif len(input) == 6:
    value = int(input[4:6])
    if input[3] == '-':
      value = value * -1
    return value
  else:
    return 0

def update(btc_last_call_timestamp, eth_last_call_timestamp, realoffset):
  response = callcg()
  if response['bitcoin']['last_updated_at'] == btc_last_call_timestamp:
    pass
  else:
    printprice("BTCP", response['bitcoin']['usd'])
    formattedtime = utime.localtime(response['bitcoin']['last_updated_at']+realoffset)
    formattedtime = str(formattedtime[3]) + ":" + str("{:02d}".format(formattedtime[4]))
    sendserial("BTCT" + "Last:  " + str(formattedtime))
  if response['ethereum']['last_updated_at'] == eth_last_call_timestamp:
    pass
  else:
    printprice("ETHP", response['ethereum']['usd'])
    formattedtime = utime.localtime(response['ethereum']['last_updated_at']+realoffset)
    formattedtime = str(formattedtime[3]) + ":" + str("{:02d}".format(formattedtime[4]))
    sendserial("ETHT" + "Last:  " + str(formattedtime))
  eth_last_call_timestamp = response['ethereum']['last_updated_at']+realoffset
  btc_last_call_timestamp = response['bitcoin']['last_updated_at']+realoffset
  return btc_last_call_timestamp, eth_last_call_timestamp

while True:
  check_connection()
  if realoffset == 0:
    sendserial("Yes0")
    sendserial("REQTZ")
  # input = uart.read(1000)
  # if (input != None):
  #   decoded_input = input.decode("utf-8")
  #   if (decoded_input[0:3] == "UTC":
  #     timeoffset = get_utc_offset(decoded_input)
  btc_last_call_timestamp, eth_last_call_timestamp = update(btc_last_call_timestamp, eth_last_call_timestamp, realoffset)
  calltimer = 5
  while calltimer > 0:
    #input = uart.readline()
    input = uart.read(500)
    if (input != None):
      decoded_input = input.decode("utf-8")
      if (decoded_input == "UPDA"):
        btc_last_call_timestamp, eth_last_call_timestamp = update(btc_last_call_timestamp, eth_last_call_timestamp)
      elif (decoded_input == "WIFIGO"):
        sendserial("OKNEWWIFI...")
        PASSWORD = '.'
        AP = '.'
        wlan.active(False)
        wlan.active(True)
        wlan.connect(APNAME, PASSWORD)
      #elif (decoded_input == "WIFI"):
      # uart.write(str('WIFI'))
      # sendserial(str(wlan.ifconfig()))
      elif (decoded_input[0:3] == "UTC"):
        timeoffset = get_utc_offset(decoded_input)
        realoffset = timeoffset * 3600
        #sendserial(str(timeoffset))
      else:
        sendserial(str(input))
        pass
        #uart.write(str(input))
    time.sleep(7)
    calltimer -= 1
