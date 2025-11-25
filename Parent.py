from microbit import *
import radio
import log
import music

radio.config(group=32) #l'alimentation pour recevoir les msgs etc pour microbit

radio.on()
radio.config(group=32, power=6) #avoir access a recevoir les msgs

currentTemp = temperature()
targetTemp = 20
max = -999
min = 999
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
    'etat_sommeil' : etat_sommeil_bebe()
    'musique' : musique()
}) #crees les valeurs pour temp son et lumiere

def log_data():
    log.add({
    'temperature' : temperature(),
    'sound' : microphone.sound_level(),
    'light' : display.read_light_level()
    'etat_sommeil' : etat_sommeil_bebe()
    'musique' : musique()
    })
    #log les entrees chaque 30 sec

running = True
while running:
    temps_maintenu = 1000
    combinaison = False
    A = 0
    B = 0
    key = Image(
            "00900:"
            "09990:"
            "00900:"
            "09900:"
            "00900"
        )
    debut_appui_A = None
    while not combinaison:
        display.show(key)
        if button_b.was_pressed():
            B += 1
            display.show("B")
            sleep(200)
        if button_a.is_pressed():
            if debut_appui_A is None: 
                debut_appui_A = running_time()
            if running_time() - debut_appui_A >= temps_maintenu:
                if A == 1 and B == 1:
                    combinaison = True
                    radio.send(str(etat_sommeil_bebe))
                elif A == 1 and B == 2:
                    combinaison = True
                    radio.send(str(musique())
                else:
                    display.scroll("Reset", 60)
                    A = 0
                    B = 0
                    debut_appui_A = None
        else:
            if debut_appui_A is not None:
                duree = running_time() - debut_appui_A
                if duree < temps_maintenu:
                    A += 1
                    display.show("A")
                    sleep(200)
            debut_appui_A = None
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

    sleep(200)

    #if button_a.was_pressed():
        #running = not running
    #if running:
        #display.show(1)
    #else:
        #display.show(0)
         #sauvegrader du data

    ##temp##
    display.show('.')
    currentTemp = temperature()
    
    if currentTemp < min:
        min = currentTemp
    elif currentTemp > max:
        max = currentTemp

    if currentTemp >= targetTemp + 3:
        music.play(music.JUMP_UP)
        display.scroll("HIGH")

    if currentTemp <= targetTemp - 3:
        music.play(music.JUMP_DOWN)
        display.scroll("LOW")
        
    if button_a.was_pressed():
        display.scroll(min)
    if button_b.was_pressed():
        display.scroll(max)
        
    sleep(1000)
    display.clear()
    sleep(1000)
    #apres avoir appure les boutons A ou B (appui long) A va afficher la temp min, et B va afficher la temp max

    radio.send(str(currentTemp))




