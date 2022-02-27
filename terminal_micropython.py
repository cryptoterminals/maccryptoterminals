import network
import urequests
import time
import ntptime
import json
import os
import uos
import webrepl
import utime
from utime import time
from machine import UART
#from time import gmtime
from machine import RTC
import sys

APNAME = ''
PASSWORD = ''
SERIALSPEED = 19200
coingeckorequest = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,usd-coin,tether,dai&vs_currencies=usd&include_last_updated_at=true&include_24hr_change=true'
punksrequest = 'http://www.punksfloorprice.com'
#punksrequest = 'http://punksfloor-env.eba-bxyj2puu.us-east-1.elasticbeanstalk.com/'

uart = UART(0, baudrate=SERIALSPEED, timeout=1000)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

uos.dupterm(None, 1)

rtc = RTC()

def sendserial(command):
    uart.write(str(command))
    uart.write(str("*"))

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
        #utime.sleep(5)
        input = uart.readline()
        if input != None:
            decoded_input = input.decode("utf-8")
            #sendserial(decoded_input) # For debug only
            if (decoded_input[0:3] == "AP:"):
                apstop = decoded_input.find('\r')
                if (apstop > 1):
                    APNAME = decoded_input[3:apstop]
                    if (decoded_input[apstop+1:apstop+6] == "PASS:"):
                        pwstop = decoded_input.find('\r', apstop+6)
                        if (pwstop > 1):
                            PASSWORD = decoded_input[apstop+6:pwstop]
                            wlan.connect(APNAME, PASSWORD)
            utime.sleep(10)
        else:
            pass
    else:
        try:
            ntptime.settime()
            sendserial(".")
            pass
        except:
            sendserial("NTPFAIL")

realoffset = 0
calltimer = 60
pushtimer = 60
listentimer = 1
temptimer = 0
punkslast = 0
btc_last_call_timestamp = 0
eth_last_call_timestamp = 0
usdc_last_call_timestamp = 0
usdt_last_call_timestamp = 0
dai_last_call_timestamp = 0

def printprice(prefix, value):
    if ((prefix == "USDC") or (prefix == "USDT") or (prefix == "DAIP")):
        formatted_price = prefix + "$" + '{:,.2f}'.format(value)
        #formatted_price = prefix + "$" + str(value)    ### was commented before LEAVE!
    elif (type(value) is float):
        value = int(value)
        #formatted_price = prefix + "$" + '{:,.0f}'.format(value)
        formatted_price = prefix + "$" + '{:,}'.format(value)
    elif (type(value) is int):
        formatted_price = prefix + "$" + "{:,}".format(value)
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

def update(btc_last_call_timestamp, eth_last_call_timestamp, usdc_last_call_timestamp, usdt_last_call_timestamp, dai_last_call_timestamp, realoffset):
    response = callcg()
    if response['bitcoin']['last_updated_at']+realoffset == btc_last_call_timestamp:
        pass
    else:
        printprice("BTCP", response['bitcoin']['usd'])
        formattedtime = utime.localtime(response['bitcoin']['last_updated_at']+realoffset)
        formattedtime = str(formattedtime[3]) + ":" + str("{:02d}".format(formattedtime[4]))
        sendserial("BTCT" + str(formattedtime))
        if (response['bitcoin']['usd_24h_change'] > 0):
            sendserial("BTCD" + "UP  " + str("{:.2f}".format(response['bitcoin']['usd_24h_change'])) + "%")
        elif (response['bitcoin']['usd_24h_change'] < 0):
            sendserial("BTCD" + "down  " + str("{:.2f}".format(response['bitcoin']['usd_24h_change']*-1)) + "%")
    if response['ethereum']['last_updated_at']+realoffset == eth_last_call_timestamp:
        pass
    else:
        printprice("ETHP", response['ethereum']['usd'])
        formattedtime = utime.localtime(response['ethereum']['last_updated_at']+realoffset)
        formattedtime = str(formattedtime[3]) + ":" + str("{:02d}".format(formattedtime[4]))
        sendserial("ETHT" + str(formattedtime))
        if (response['ethereum']['usd_24h_change'] > 0):
            sendserial("ETHD" + "UP  " + str("{:.2f}".format(response['ethereum']['usd_24h_change'])) + "%")
        elif (response['ethereum']['usd_24h_change'] < 0):
            sendserial("ETHD" + "down  " + str("{:.2f}".format(response['ethereum']['usd_24h_change']*-1)) + "%")
    if response['usd-coin']['last_updated_at']+realoffset == usdc_last_call_timestamp:
        pass
    else:
        printprice("USDC", response['usd-coin']['usd'])
    if response['tether']['last_updated_at']+realoffset == usdt_last_call_timestamp:
        pass
    else:
        printprice("USDT", response['tether']['usd'])
    if response['dai']['last_updated_at']+realoffset == dai_last_call_timestamp:
        pass
    else:
        printprice("DAIP", response['dai']['usd'])

    usdc_last_call_timestamp = response['usd-coin']['last_updated_at']+realoffset
    usdt_last_call_timestamp = response['tether']['last_updated_at']+realoffset
    dai_last_call_timestamp = response['dai']['last_updated_at']+realoffset
    eth_last_call_timestamp = response['ethereum']['last_updated_at']+realoffset
    btc_last_call_timestamp = response['bitcoin']['last_updated_at']+realoffset
    return btc_last_call_timestamp, eth_last_call_timestamp, usdc_last_call_timestamp, usdt_last_call_timestamp, dai_last_call_timestamp

def punksupdate(punkslast):
    if ((punkslast == 0) or ((time() - punkslast) > 1800)):
        try:
            response = urequests.get(punksrequest)
            punksfloorpos = response.text.find("punksfloor:")
            punksfloorpos2 = response.text.find("ETH")
            punksfloor = response.text[punksfloorpos+11:punksfloorpos2+3]
            sendserial("PNKF" + punksfloor)
            punkssalepos = response.text.find("punkslast:")
            punkssalepos2 = response.text[punkssalepos:].find("ETH")
            punkssale = response.text[punkssalepos+10:punkssalepos+punkssalepos2+3]
            sendserial("PNKL" + punkssale)
            punkslast = time()
            return punkslast
        except:
            sendserial("PNKF" + "NA")
            return punkslast
    else:
        return punkslast


while True:
    check_connection()
    if realoffset == 0:
        sendserial("REQTZ")
    btc_last_call_timestamp, eth_last_call_timestamp, usdc_last_call_timestamp, usdt_last_call_timestamp, dai_last_call_timestamp = update(btc_last_call_timestamp, eth_last_call_timestamp, usdc_last_call_timestamp, usdt_last_call_timestamp, dai_last_call_timestamp, realoffset)
    punkslast = punksupdate(punkslast)
    calltimer = 5
    while calltimer > 0:
        input = uart.read(500)
        if (input != None):
            decoded_input = input.decode("utf-8")
            if (decoded_input == "UPDA"):
                btc_last_call_timestamp, eth_last_call_timestamp, usdc_last_call_timestamp, usdt_last_call_timestamp = update(btc_last_call_timestamp, eth_last_call_timestamp, spi_last_call_timestamp, realoffset)
            elif (decoded_input == "WIFIGO"):
                sendserial("OKNEWWIFI...")
                PASSWORD = '.'
                AP = '.'
                wlan.active(False)
                wlan.active(True)
                wlan.connect(APNAME, PASSWORD)
            elif (decoded_input[0:3] == "UTC"):
                timeoffset = get_utc_offset(decoded_input)
                realoffset = timeoffset * 3600
                #sendserial(str(timeoffset))
            else:
                sendserial(str(input))
                pass
                #uart.write(str(input))
        utime.sleep(7)
        calltimer -= 1
