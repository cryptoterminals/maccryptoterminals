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

APNAME = 'yourapname'
PASSWORD = 'yourwifipassword'
END = '\n'
SERIALSPEED = 19200
coingeckorequest = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_last_updated_at=true'



uart = UART(0, baudrate=SERIALSPEED)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(APNAME, PASSWORD)
time.sleep(3)
print("\n", end="")
print(wlan.isconnected())

#print(json.loads(urequests.get(https://api.coingecko.com/api/v3/ping).content.decode('utf-8'))))

def sendserial(command):
	#print(command, end=END)
	uart.write(str(command))
	uart.write(str("*"))
	#uart.write('\n')

def get_serial():
	s = uart.read(500)
	if (s != bytes('', 'utf-8')):
		#print(s.decode())
		return s

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
	if (wlan.isconnected() == False):
		sendserial("NOCO")
		#aplist = wlan.scan()
		#sendserial("APLIST")
		#sendserial(aplist)
		try:
			ap = get_serial()
			if (ap[0:3] == "AP__"):
				print("GOT_AP:" + ap)
		except:
			print("NO_AP_RESPONSE")
			time.sleep(10)				
		sendserial("APPW")
		wifipw = get_serial()
		if (wifipw != ""):
			wlan.connect(ap, wifipw)
	else:
		pass

calltimer = 60
pushtimer = 60
listentimer = 1
temptimer = 0
btc_last_call_timestamp = 0
eth_last_call_timestamp = 0

uos.dupterm(None, 1)

while True:
	#sendserial("calllingcg")
	#uart.write("callingcg")
	response = callcg()
	if response['bitcoin']['last_updated_at'] == btc_last_call_timestamp:
		#sendserial("no new btc updates")
		pass
	else:
		sendserial("BTCP" + str(response['bitcoin']['usd']))
		sendserial("BTCT" + str(response['bitcoin']['last_updated_at']))
	if response['ethereum']['last_updated_at'] == eth_last_call_timestamp:
		print("no new eth updates")
		#pass
	else:
		sendserial("ETHP" + str(response['ethereum']['usd']))
		sendserial("ETHT" + str(response['ethereum']['last_updated_at']))
	eth_last_call_timestamp = response['ethereum']['last_updated_at']
	btc_last_call_timestamp = response['bitcoin']['last_updated_at']
	calltimer = 5
	while calltimer > 0:
		input = uart.read(500)
		#input = uart.readline()
		#sendserial(input)
		#input = uart.read(100)
		if input == bytes('XENON', 'utf-8'):
			uart.write(str('NEON'))
		#elif (bytes(input[0:5]) == bytes('WIFIGO', 'utf-8')):
			#uart.write(str('NEWAP'))
		elif (input == bytes('WIFI', 'utf-8')):
			uart.write(str('WIFI'))
			sendserial(str(wlan.ifconfig()))
		else:
			uart.write('.')
			uart.write(str(input))
			uart.write(str("*"))
		time.sleep(7)
		calltimer -= 1
	
