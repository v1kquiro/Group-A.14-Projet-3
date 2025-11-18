from microbit import *
import radio

radio.config(group=23)

radio.on()
radio.send('hello')
radio.config(group=23, power=3)

while True:
    message = radio.receive()
    if message:
        display.scroll(message)
