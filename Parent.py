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

def recevoir_signal(message):
    return radio.receive

def etat_sommeil_bebe():
    mouvement = accelerometer.get_strength()
    if mouvement < 1500:
        return 1
    else:
        return 0

def musique():
    return 0

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

        faim = [Image.ANGRY, Image.ARROW_S]
        display.show(faim, delay=1000, loop=False)
        music.play(music.BA_DING)
        
        if  button_b.was_pressed() :
            display.clear()
            index += 1 
            return index
        else :
            
            display.show(faim, delay=1000, loop=False)
            music.play(music.BA_DING)


def total_lait():   
    while True :
        index = 1
        temps_alerte = 5000       
        début = running_time()    
        while True :            
            if running_time() - début < temps_alerte :
                if button_b.is_pressed() :
                    display.show(index)                
                    if button_b.is_pressed() :               
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
        if button_a.was_pressed():
            if direction == up:
                direction = left
            elif direction == left:
                direction = down
            elif direction == down:
                direction = right
            elif direction == right:
                direction = up
        if button_b.was_pressed():
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
        # Téléportations et collisions
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
        if nouvelle_direction in snake:
            game_over = True
        else:
            snake.insert(0, nouvelle_direction)
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
        sleep(750)
        
    # Si game_over == True
    display.scroll("GAME OVER", 50)
    display.scroll(str(score), 200)

# Boucle principale
running = True
while running:
    temps_maintenu = 1000
    combinaison = False
    A = 0
    B = 0
    debut_appui_A = None
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
        # Si bouton b appuyé
        if button_b.was_pressed():
            B += 1
            display.show("B")
            sleep(200)
        # Les deux cas de figure si bouton a appuyé
        if button_a.is_pressed():
            if debut_appui_A is None: 
                debut_appui_A = running_time()
            # Appui maintenu sur le bouton A (+ que 1 sec)
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
                elif A == 3 and B == 1:
                    snake()
                # Si aucune combinaison ne correspond
                else:
                    display.scroll("Reset", 60)
                    A = 0
                    B = 0
                    debut_appui_A = None
        else:
            if debut_appui_A is not None:
                duree = running_time() - debut_appui_A
                # Appui court sur le bouton A
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

    # Pour retourner au menu principal 
    if combinaison == True and button_a.was_pressed():
        combinaison = False

