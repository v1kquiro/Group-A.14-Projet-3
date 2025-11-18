from microbit import *
import radio
import log

radio.config(group=32) #l'alimentation pour recevoir les msgs etc pour microbit

radio.on()
radio.send('message')
radio.config(group=32, power=6) #avoir access a recevoir les msgs

currentTemp = temperature()
max = currentTemp
min = currentTemp
#detecter le max et min de temperature

count = 0
score = 0
score += 1
display.scroll(score)

name = 'Parent'
display.scroll(name) #nommee la microbit

log.set_labels('temperature','sound','light')
log.add({
    'temperature' : temperature(),
    'sound' : microphone.sound_level(),
    'light' : display.read_light_level()
}) #crees les valeurs pour temp son et lumiere

@run_every(s=30)
def log_data():
    log.add({
    'temperature' : temperature(),
    'sound' : microphone.sound_level(),
    'light' : display.read_light_level()
    })
    #log les entrees chaque 30 sec

running = False
while True:
    message = radio.receive()
    if message:
        display.scroll(message)
        #recevoir les msgs

    if button_a.is_pressed() and button_b.is_pressed():
        display.scroll('A and B')
    elif button_a.is_pressed():
        display.scroll('A')
    elif button_b.is_pressed():
        display.scroll('B')
    sleep(100)
    #si les boutons A et B sont appuyer

    sleep(10000)

    if button_a.was_pressed():
        running = not running
    if running:
        display.show(1)
    else:
        display.show(0)
         #sauvegrader du data

    display.show('.')
    currentTemp = temperature()
    if currentTemp < min:
        min = currentTemp
    elif currentTemp > max:
        max = currentTemp
    if button_a.was_pressed():
        display.scroll(min)
    if button_b.was_pressed():
        display.scroll(max)
    sleep(1000)
    display.clear()
    sleep(1000)
    #affiche la temp min et max du microbit chaque 30 sec apres avoir appuye un bouton (a ou b)
    
