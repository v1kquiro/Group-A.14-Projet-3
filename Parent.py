from microbit import *
import radio
import log
import music
import random


radio.on() # Activation de la radio
radio.config(group=32, power=6) # Mise en place de la fréquence et de la puissance de la radio

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
display.scroll(name) # Nomer le microbit pour les différencier

# Fonction pour envoyer des messages au microbit bebe 
def envoyer_signal(message):
    radio.send(message)
    display.show("S")
    sleep(300)
    display.clear()

log.set_labels('temperature','sound','light','etat_sommeil','musique')
log.add({
    'temperature' : temperature(),
    'sound' : microphone.sound_level(),
    'light' : display.read_light_level(),
}) #crees les valeurs pour temp son et lumiere

def log_data():
    log.add({
    'temperature' : temperature(),
    'sound' : microphone.sound_level(),
    'light' : display.read_light_level(),
    })
    #log les entrees chaque 30 sec

#def de la boucle de demande de nourrir et son clear

def nourrir() :
    index = 0   
    while True  :      

        faim = [Image.ANGRY, Image.ARROW_S]
        display.show(faim, delay=1000, loop=False)
        music.play(music.BA_DING)
        
        if  button_b.was_pressed() :
            display.clear()
            index += 1 
            sleep(2000)
            return index
        else :
            
            display.show(faim, delay=1000, loop=False)
            music.play(music.BA_DING)


def total_lait():   
    while True :
        index = 1 
        temps_alerte = 10000       
        début = running_time()    
        while True :            
           if button_a.is_pressed() :
                index += 1
                display.show(index)
                sleep(1000) 
                display.clear()
           if button_b.is_pressed() :
                index = index - 1 
                display.show(index)
                sleep(1000) 
                display.clear()
           if running_time() - début < temps_alerte :
                if pin_logo.is_touched():
                    display.show(index)                
                    if pin_logo.is_touched() :               
                        sleep(1000) 
                        display.clear()             
           elif running_time() - début >= temps_alerte :    
                nourrir()                     
                index +=1    
                début = running_time()


# Fonction permettant de jouer au jeu snake
def snake():
    # Variables
    score = 0
    game_over = False
    lumiere = 0
    up = (0, -1)
    down = (0, 1)
    left = (-1, 0)
    right = (1, 0)
    direction = up
    # Situations initiale
    snake = [(2, 2)]
    fruit = (random.randint(0, 4), random.randint(0, 4))

    # Boucle principale
    while not game_over:
        # Si bouton A pressé
        if button_a.was_pressed():
            # Mouvements en fonction de la direction du serpent
            if direction == up:
                direction = left
            elif direction == left:
                direction = down
            elif direction == down:
                direction = right
            elif direction == right:
                direction = up
        # Si bouton B pressé
        if button_b.was_pressed():
            # Mouvements en fonction de la direction du serpent
            if direction == up:
                direction = right
            elif direction == left:
                direction = up
            elif direction == down:
                direction = left
            elif direction == right:
                direction = down
        # Actualisation de la tête du serpent
        direction_en_x = snake[0][0] + direction[0]
        direction_en_y = snake[0][1] + direction[1]
        # Si serpent touche les bords de l'écran, il est téléporté à l'opposé
        if direction_en_x< 0:
            direction_en_x= 4
        elif direction_en_x > 4:
            direction_en_x = 0
        if direction_en_y < 0:
            direction_en_y = 4
        elif direction_en_y > 4:
            direction_en_y = 0
        nouvelle_direction = (direction_en_x, direction_en_y)
        # Nettoyage de l'écran
        display.clear()
        # Game over si le serpent touche son corps
        if nouvelle_direction in snake:
            game_over = True
        else:
            # Si le serpent ne touche pas son corps
            snake.insert(0, nouvelle_direction)
        # Si le serpent mange un fruit (corps grandi)
        if nouvelle_direction == fruit:
            fruit = (random.randint(0, 4), random.randint(0, 4))
            score += 1
            while fruit in snake:
                fruit = (random.randint(0, 4), random.randint(0, 4))
        else:
            snake.pop()
            
        # Fruit
        display.set_pixel(fruit[0], fruit[1], 4)
        # Serpent
        for i in range(len(snake)):
            if i == 0:
                lumiere = 9
            else:
                lumiere = 7
            display.set_pixel(snake[i][0], snake[i][1], lumiere)
        # Actualisation toutes les 750 millisecondes
        sleep(750)
        
    # Si game_over == True
    display.scroll("GAME OVER", 50)
    display.scroll(str(score), 200)

# Boucle principale
running = True
while running:
    # Recevoir et display des messages du microbit bebe 
    message = radio.receive()
    if message:
        display.scroll(str(message))
    # Variables utiles pour les différentes combinaisons du menu principal
    temps_maintenu = 1000
    combinaison = False
    A = 0
    B = 0
    debut_appui_A = None
    # Tant qu'aucune combinaison correcte n'a été rentrée
    while not combinaison:
        # Image de clé
        key = Image(
            "00900:"
            "09990:"
            "00900:"
            "09900:"
            "00900:"
        )
        display.show(key)
        # Si bouton B pressé
        if button_b.was_pressed():
            B += 1
            display.show("B")
            sleep(200)
        # Les deux cas de figure si bouton A pressé
        if button_a.is_pressed():
            if debut_appui_A is None: 
                debut_appui_A = running_time()
            else:
                if debut_appui_A is not None:
                    duree = running_time() - debut_appui_A
                    if duree >= temps_maintenu:
                        if A == 1 and B == 1:
                            combinaison = True
                            envoyer_signal("etat_sommeil")
                        elif A == 1 and B == 2:
                            combinaison = True
                            envoyer_signal("musique")
                        elif A == 1 and B == 3:
                            radio.send("quantite_lait")
                        elif A == 2 and B == 1:
                            envoyer_signal("temperature")
                        elif A == 3 and B == 1:
                            envoyer_signal("lumiere")
                        elif A == 2 and B == 2:
                            snake()
                        else:
                            display.scroll("Reset", 60)
                        A = 0
                        B = 0
                    else:
                        A += 1
                        display.show("A")
                        sleep(200)
                    debut_appui_A = None
    sleep(100)

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

    # Pour retourner au menu principal 
    if combinaison == True and button_a.was_pressed():
        combinaison = False







