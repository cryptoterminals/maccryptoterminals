# maccryptoterminals
Micropython and related code for ESP8266-based old-world Mac Crypto Price Terminals
This code is associated w/ the NFT project http://twitter.com/cryptoterminals and https://app.rarible.com/yugen
You are welcome to reuse any of this code or plans - the NFTs associated are the unique items with the exception of some unique artwork in the Hypercard stacks

To use this code, you need the following hardware:
-An old-world Mac w/ a DIN8 serial port & Hypercard installed
-I am testing on OS7 because it has a 'Startup Items' folder
-A custom DIN8 to DB9 cable with the following pinout: [TODO ADD Pinout]
-An RS422 to RS232 converter/adapter https://www.amazon.com/gp/product/B0196AO1IG
-An M/M DB9 null modem coupler https://www.amazon.com/gp/product/B07J6TSF6V
-A TTL to RS232 adapter https://www.amazon.com/gp/product/B00LPK0Z9A/
-4 breadboard jumper wires connecting Tx, Rx, 3VC, GND between the TTL and:
-Node MCU ESP8266 https://www.amazon.com/gp/product/B081CSJV2V
[TODO - add photo of completed adapter & full wiring/pinouts]

You need to flash your NodeMCU ESP8266 as per instructions here:
https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html#intro
and, upload the python in this repo using the instructions here (I save as main.py):
https://docs.micropython.org/en/latest/esp8266/quickref.html#webrepl-web-browser-interactive-prompt

I use the client: https://github.com/micropython/webrepl

I found reference code for doing serial interactions within Hypercard at 
https://archive.org/details/hypercard_serialporttoolkit
and
https://www.info-mac.org/viewtopic.php?f=119&t=1049
