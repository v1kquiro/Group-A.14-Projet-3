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

    if button_a.is_pressed() and button_b.is_pressed():
        display.scroll('A and B')
    elif button_a.is_pressed():
        display.scroll('A')
    elif button_b.is_pressed():
        display.scroll('B')
    sleep(100)
