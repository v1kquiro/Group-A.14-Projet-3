from microbit import *
import radio
import log
import music
import random


radio.on()
radio.config(group= 32, channel = 6, address = 0x11111111, power = 6  )
connexion_established = False # Indique si la connexion est établie
key = "KEYWORD"               # Clé de chiffrement partagée entre les deux micro:bits
connexion_key = None          # Clé de connexion temporaire pour l'établissement de la connexion
nonce_list = set()            # Liste des nonces déjà vus pour éviter les rejets de connexion
baby_state = 0                # 0 : bébé calme, 1 : bébé qui pleure
set_volume(100)               # volume maximal

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

def hashing(string):
	"""
	Hachage d'une chaîne de caractères fournie en paramètre.
	Le résultat est une chaîne de caractères.
	Attention : cette technique de hachage n'est pas suffisante (hachage dit cryptographique) pour une utilisation en dehors du cours.

	:param (str) string: la chaîne de caractères à hacher
	:return (str): le résultat du hachage
	"""
    
	def to_32(value):
		"""
		Fonction interne utilisée par hashing.
		Convertit une valeur en un entier signé de 32 bits.
		Si 'value' est un entier plus grand que 2 ** 31, il sera tronqué.

		:param (int) value: valeur du caractère transformé par la valeur de hachage de cette itération
		:return (int): entier signé de 32 bits représentant 'value'
		"""
		value = value % (2 ** 32)
		if value >= 2**31:
			value = value - 2 ** 32
		value = int(value)
		return value

	if string:
		x = ord(string[0]) << 7
		m = 1000003
		for c in string:
			x = to_32((x*m) ^ ord(c))
		x ^= len(string)
		if x == -1:
			x = -2
		return str(x)
	return ""
    
def vigenere(message, key, decryption=False):
    text = ""                   
    key_length = len(key)
    key_as_int = [ord(k) for k in key]

    for i, char in enumerate(str(message)):
        #Letters encryption/decryptio
        if char.isalpha():
            key_index = i % key_length
            if decryption:
                modified_char = chr((ord(char.upper()) - key_as_int[key_index] + 26) % 26 + ord('A'))
            else : 
                modified_char = chr((ord(char.upper()) + key_as_int[key_index] - 26) % 26 + ord('A'))
            #Put back in lower case if it was
            if char.islower():
                modified_char = modified_char.lower()
            text += modified_char
        #Digits encryption/decryption
        elif char.isdigit():
            key_index = i % key_length
            if decryption:
                modified_char = str((int(char) - key_as_int[key_index]) % 10)
            else:  
                modified_char = str((int(char) + key_as_int[key_index]) % 10)
            text += modified_char
        else:
            text += char
    return text
    
def send_packet(key, type, content):
    """
    Envoi de données fournies en paramètres
    Cette fonction permet de construire, de chiffrer puis d'envoyer un paquet via l'interface radio du micro:bit

    :param (str) key:       Clé de chiffrement
           (str) type:      Type du paquet à envoyer
           (str) content:   Données à envoyer
	:return none
    """
    # construction du format  TYPE|LONGUEUR|CONTENU/VALEUR
    
    #T: type du message
    T = type
    #L : Longeur du message
    L = str(len(content))
    #V = content or value
    V = content
    
    # Assemblage du Format TLV
    packet_TLV = T + "|" + L + "|" + V       # "|" : separateur
    
    #chiffrement du packet
    encrypted_packet = vigenere(packet_TLV, key, decryption=False)
    #envoi via radio
    radio.send(encrypted_packet)

#Unpack the packet, check the validity and return the type, length and content
def unpack_data(encrypted_packet, key):
    """
    Déballe et déchiffre les paquets reçus via l'interface radio du micro:bit
    Cette fonction renvoit les différents champs du message passé en paramètre

    :param (str) encrypted_packet: Paquet reçu
           (str) key:              Clé de chiffrement
	:return (srt)type:             Type de paquet
            (int)length:           Longueur de la donnée en caractères
            (str) message:         Données reçue
    """
    #Déchiffrementdu packet
    decrypted_packet = vigenere(encrypted_packet, key, decryption =True)
    
                        #Extraction du Format TLV
    #séparer selon le délimitieur "|"
    parts = decrypted_packet.split("|")
    
    #verifie que l'on a bien le 3 parties (T, L, V)
    if len(parts) == 3 :
        T = parts[0]                     # Le type
        L = int(parts[1])                # La longueur( converti en entier)
        V = parts[2]                     # La valeur (donnée)
        return T, L, V
    
    #continuer le code encore manque donnée
    else:
        return "", 0, ""   # renvoi paquet vide en cas d'erreur 
          
def receive_packet(packet_received, key):
    """
    Traite les paquets reçus via l'interface radio du micro:bit
    Cette fonction utilise la fonction unpack_data pour renvoyer les différents champs du message passé en paramètre
    Si une erreur survient, les 3 champs sont retournés vides

    :param (str) packet_received: Paquet reçue
           (str) key:              Clé de chiffrement
	:return (srt)type:             Type de paquet
            (int)lenght:           Longueur de la donnée en caractère 
            (str) message:         Données reçue
    """
    try:
        T, L, V = unpack_data(packet_received, key)
        return T, L, V
    
    except: 
        return "",0, ""  
              
#Calculate the challenge response 
def calculate_challenge_response(challenge):    # ce lui le nonce
    """
    Calcule la réponse au challenge initial de connection envoyé par l'autre micro:bit

    :param (str) challenge:            Challenge reçu
	:return (srt)challenge_response:   Réponse au challenge
    """

    challenge_response = hashing(challenge) 
    return challenge_response

def verification_nonce(nonce):
    """
    Vérifie si le nonce a dejà été utilisé
    return True si le nonce nouveau(donc accepte)
    return False si le nonce  nonce déjà vu(réjette)
    
    :param(str): nonce: Nonce a vérifer
    :return (bool): True si c'est nouveau et False si c'est déja utilisé
    """
    global nonce_list

    if nonce in nonce_list:
         return False   # si le nonce est déjà utilisé
    else: 
         nonce_list.add(nonce)
         return True  # seulement si le nonce est nouveau


#Respond to a connexion request by sending the hash value of the number received
def respond_to_connexion_request(key):
    """
    Réponse au challenge initial de connection avec l'autre micro:bit
    Si il y a une erreur, la valeur de retour est vide

    :param (str) key:                   Clé de chiffrement
	:return (srt) challenge_response:   Réponse au challenge
    """
    global connexion_key
    #on Attend un message de connexion
    packet = radio.receive()
    
    if packet:
         #On dechiffre et déballe le paquet reçu
        packet_type, _, nonce = receive_packet(packet, key)
               #On verifie le nonce 
        if packet_type == "0x01":         
            # si le nonce est nouveau on accepte la connexion
            if verification_nonce(nonce):  
                response = calculate_challenge_response(nonce) 
                connexion_key = response  # on stock la reponse pour la session de connexion
                   #on envoi la reponse au bebe au parent 
                send_packet(key, "RESPONSE", response)
                display.show(Image.YES)  # indique l'envoi de la réponse en cours par un YES
                return response
            else:
           # le nonce est déjà vu alors 
                display.show(Image.NO)   #nonce incorecte la  connex. est refusée et le micro:bit affiche NO
                return ""
    
    return ""   


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
           if pin_logo.is_touched() :
                index += 1
                display.show(index)
                sleep(1000) 
                display.clear()
           if pin_logo.is_touched() and button_b.is_pressed()  :
                index = index - 1 
                display.show(index)
                sleep(1000) 
                display.clear()
           if running_time() - début < temps_alerte :
                if button_b.is_pressed():
                    display.show(index)                
                    if button_b.is_pressed()  :               
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

def main():# le parent attend le signe de l'enfant
    global connexion_established
    global baby_state

running = True
action = None
while running:
    if not connexion_established:
            # ici il est passif il attend la connexion du bebe
        result = respond_to_connexion_request(key)
        if result:
                connexion_established = True
                display.show(Image.HAPPY)  # connexion établie le micro:bit affiche HAPPY

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
                        send_packet(key, "0x03", "etat_sommeil")
                        action = "sommeil"
                        combinaison = True
                    elif A == 1 and B == 2:
                        send_packet(key, "0x03", "musique")
                        action = "musique"
                        combinaison = True
                    elif A == 2 and B == 1:
                        send_packet(key, "0x03", "temperature")
                        action = "temperature"
                        combinaison = True
                    elif A == 3 and B == 1:
                        send_packet(key, "0x03", "lumiere")
                        action = "lumiere"
                        combinaison = True
                    elif A == 2 and B == 2:
                        action = "snake"
                        combinaison = True
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
    
    # Attente de la réponse du bébé
    packet = radio.receive()
    if packet:
        type_msg, _, message = receive_packet(packet, key)
        if type_msg == "0x03":
            display.clear()
            display.scroll(message)
            
    # Pour retourner au menu principal 
    if combinaison == True and button_a.was_pressed():
        combinaison = False
main()
