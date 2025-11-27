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

def envoyer_signal(message):
    radio.send(message)
    display.show("S")
    sleep(300)
    display.clear()

def recevoir_signal(message)
    return radio.receive

log.set_labels('temperature','sound','light','etat_sommeil','musique')
log.add({
    'temperature' : temperature(),
    'sound' : microphone.sound_level(),
    'light' : display.read_light_level(),
    'etat_sommeil' : etat_sommeil_bebe(),
    'musique' : musique()
}) #crees les valeurs pour temp son et lumiere

def log_data():
    log.add({
    'temperature' : temperature(),
    'sound' : microphone.sound_level(),
    'light' : display.read_light_level(),
    'etat_sommeil' : etat_sommeil_bebe(),
    'musique' : musique()
    })
    #log les entrees chaque 30 sec

#def de la boucle de demande de nourrir et son clear
def nourrir() :
    index = 0   
    while True  :      
        if  button_b.was_pressed() :
            display.clear()
            index += 1 
            return index
        else :
            faim = [Image.ANGRY, Image.ARROW_S]
            display.show(faim, delay=1000, loop=False)
            music.play(music.BA_DING)
            
#fait en sorrte que l'alarme se joue toute les 3h et que on puisse utiliser les boutons peit importe le moment.
def total_lait():   
    while True :
        index = 1
        temps_alerte = 10000       
        début = running_time()    
        while True :            
            if button_a.was_pressed() :              
                display.show(index)                
                sleep(2000)               
                display.clear()             
            elif running_time() - début >= temps_alerte :    
                nourrir()                     
                index +=1    
                début = running_time()

running = True
while running:
    temps_maintenu = 1000
    combinaison = False
    A = 0
    B = 0
    debut_appui_A = None
    while not combinaison:
        key = Image(
            "00900:"
            "09990:"
            "00900:"
            "09900:"
            "00900:"
        )
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
                    envoyer_signal("etat_sommeil")
                elif A == 1 and B == 2:
                    combinaison = True
                    envoyer_signal("musique")
                elif A == 1 and B == 3:
                    radio.send("quantite_lait")
                elif A == 1 and B == 1:
                    envoyer_signal("temperature")
                elif A == 2 and B == 1:
                    envoyer_signal("lumiere")
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
    sleep(100)
    #si les boutons A et B sont appuyer

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

    if combinaison = True and button_a.was_pressed():
        combinaison = False


