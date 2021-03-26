# maccryptoterminals
Micropython and related code for ESP8266-based old-world Mac Crypto Price Terminals

This code is associated w/ the NFT project http://twitter.com/cryptoterminals and https://opensea.io/assets/0x2532a770211bf10435c70d889357b1a820260be1/1

![Mac Crypto Terminal](https://github.com/cryptoterminals/maccryptoterminals/blob/main/Screenshot_2021-03-09_15-25-08.png?raw=true)

You are welcome to reuse any of this code or plans - the NFTs associated are the unique items with the exception of some unique artwork in the Hypercard stacks

To use this code, you need the following hardware:

* An old-world Mac w/ a DIN8 serial port & Hypercard installed
* I am testing on OS7 because it has a 'Startup Items' folder
* A custom 4 wire DIN8 to DB9 cable with the following pinout - the DIN8 connects to the modem/printer port on the Mac - the DB9 connects to the RS422 side of the adapter linked below and in the photo:

 DIN8F MAC SIDE _______________________ DIN8M CABLE END
 
 ___8__7__6______________________________6__7__8
 
 ___5__4__3______________________________3__4__5
 
 ____2__1_________________________________1__2
 
  * Cable:
  * DB9F   <>    DIN8M                         
  * 1 ----------- 8 RxD+                          
  * 2 ----------- 5 RxD-                          
  * 3 ----------- 6 TxD+                          
  * 4 ----------- 3 TxD-
* An RS422 to RS232 converter/adapter https://www.amazon.com/gp/product/B0196AO1IG
* An M/M DB9 null modem coupler https://www.amazon.com/gp/product/B07J6TSF6V
* A TTL to RS232 adapter https://www.amazon.com/gp/product/B00LPK0Z9A/
* 4 breadboard jumper wires STRAIGHT connecting Tx<->Tx, Rx<->Rx, 3VC<->3V, GND<->GND between the TTL and:
* Node MCU ESP8266 https://www.amazon.com/gp/product/B081CSJV2V


![cable chain](https://github.com/cryptoterminals/maccryptoterminals/blob/main/IMG_7368.jpg?raw=true)


You need to flash your NodeMCU ESP8266 as per instructions here:

https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html#intro

and, upload the python in this repo using the instructions here (I save as main.py which runs on startup by default per the Micropython setup):

https://docs.micropython.org/en/latest/esp8266/quickref.html#webrepl-web-browser-interactive-prompt

I use the client: https://github.com/micropython/webrepl

I found reference code for doing serial interactions within Hypercard at 

https://archive.org/details/hypercard_serialporttoolkit

and

https://www.info-mac.org/viewtopic.php?f=119&t=1049

YOU NEED A HYPERCARD STACK WITH THE SERIAL XCMD AND XFCN EMBEDDED FOR THIS TO WORK! The example stacks above provide this. The serial commands won't work unless you have these embedded in your stack (I think you call this part of the 'resource fork'). You can simply start with one of these and delete the cards and scripts you don't want, or even all of them, but your stack needs to be based on a file that had these resources attached (I think this was/is done in ResEdit). The toolkit linked on archive.org includes the actual source code for the XCMD and XFCNs that get attached (I believe it's written in Pascal) 

![cable chain2](https://github.com/cryptoterminals/maccryptoterminals/blob/main/IMG_7369.jpg?raw=true)
