from microbit import *
import radio
import random
import music
import math

#Can be used to filter the communication, only the ones with the same parameters will receive messages
#radio.config(group=23, channel=2, address=0x11111111)
#default : channel=7 (0-83), address = 0x75626974, group = 0 (0-255)

radio.on()
radio.config(group= 32, channel = 6, address = 0x11111111, power = 6) # Alignement de la fréquence et de la puissance sur le bebi parent
key = "KEYWORD" # Clé de chiffrement partagée entre les deux micro:bits
connexion_established = False  # Clé de connexion temporaire pour l'établissement de la connexion

temp_max = -999
temp_min = 999
#detecter le max et min de temperature

name = 'Bebe'
display.scroll(name)

def hashing(string):
	"""
	Hachage d'une chaine de caracteres fournie en parametre.
	Le resultat est une chaine de caracteres.
	Attention : cette technique de hachage n'est pas suffisante (hachage dit cryptographique) pour une utilisation en dehors du cours.

	:param (str) string: la chaine de caracteres a hacher
	:return (str): le resultat du hachage
	"""
	def to_32(value):
		"""
		Fonction interne utilisee par hashing.
		Convertit une valeur en un entier signe de 32 bits.
		Si 'value' est un entier plus grand que 2 ** 31, il sera tronque.

		:param (int) value: valeur du caractere transforme par la valeur de hachage de cette iteration
		:return (int): entier signe de 32 bits representant 'value'
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
        key_index = i % key_length
        #Letters encryption/decryption
        if char.isalpha():
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
    Envoie de données fournie en paramètres
    Cette fonction permet de construire, de chiffrer puis d'envoyer un paquet via l'interface radio du micro:bit

    :param (str) key:       Clé de chiffrement
           (str) type:      Type du paquet à envoyer
           (str) content:   Données à envoyer
	:return none
    """
    #T: type du message
    T = type
    #L : Longeur du message
    L= str(len(content))
    #V = content or value
    V= content
 
    # Assemblage du Format TLV
    packet_TLV = T + "|" + L + "|" + V       # "|" : separateur
 
    #chiffrement du packet
    encrypted_packet = vigenere(packet_TLV, key, decryption=False)
    
    #envoi via radio
    radio.send(encrypted_packet)

#Decrypt and unpack the packet received and return the fields value
def unpack_data(encrypted_packet, key):
    """
    Déballe et déchiffre les paquets reçus via l'interface radio du micro:bit
    Cette fonction renvoit les différents champs du message passé en paramètre

    :param (str) encrypted_packet: Paquet reçu
           (str) key:              Clé de chiffrement
	:return (srt)type:             Type de paquet
            (int)lenght:           Longueur de la donnée en caractères
            (str) message:         Données reçues
    """
                #Déchiffrementdu packet
    decrypted_packet = vigenere(encrypted_packet, key, decryption =True)
 
                     #Extraction du Format TLV
        #séparer selon le délimitieur "|"
    parts = decrypted_packet.split("|")
 
        #verifie que l'on a bien le 3 parties (T, L, V)
    if len(parts) == 3 :
        T = parts[0]                     # Le type
        L = int(parts[1])                # La longueur( converti en e
        V = parts[2]                     # La valeur (donnée)
        return T, L, V
 
      #continuer le code encore manque donnée
    else:
        return "", 0, ""   # renvoi paquet vide en cas d'erreur 

#Unpack the packet, check the validity and return the type, length and content
def receive_packet(packet_received, key):
    """
    Traite les paquets reçue via l'interface radio du micro:bit
    Cette fonction permet de construire, de chiffrer puis d'envoyer un paquet via l'interface radio du micro:bit
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
def calculate_challenge_response(challenge):
    """
    Calcule la réponse au challenge initial de connection avec l'autre micro:bit

    :param (str) challenge:            Challenge reçu
	:return (srt)challenge_response:   Réponse au challenge
    """
    challenge_response = hashing(challenge)
    return challenge_response

#Ask for a new connection with a micro:bit of the same group
def establish_connexion(key):
    """
    Etablissement de la connexion avec l'autre micro:bit
    Si il y a une erreur, la valeur de retour est vide

    :param (str) key:                  Clé de chiffrement
	:return (srt)challenge_response:   Réponse au challenge
    """
#on genere un challlenge aléatoire de 8 chiffres (le challenge)
    challenge = str(random.randint(10000000, 99999999))
    display.scroll("N :" + challenge[:4]) # affiche les 4 premier chiffre du challenge pour debug en cas de probleme de connexion

     # On construit et on envoi un paquet(message) de connexion
    send_packet(key, "0x01", challenge) 
    display.show(Image.ARROW_E)  #le micro:bit affiche qu il cherche a se connecter avec une fleche a droite

    # ensuite on attend une reponse du parent 
    start_time = running_time()      # on enregistre le moment de depart
    while running_time() - start_time < 10000:   # on attendra 10s
        packet = radio.receive()   # on ecoute la radio pour une reponse
        
        # si le paquet à été reçu 
        if packet:
             packet_type, _, response = receive_packet(packet,key)  # dechiffrement et extraction du paquet, ici receive_packet retournera 
             if packet_type == "RESPONSE":
                  expected = hashing(challenge)
                  # on compare la reponse recu a la reponse attendu
                  if response == expected:          # si le hash est correct = authentification reussie
                       display.show(Image.YES)      # connexion établie le micro:bit affiche YES 
                       return expected              # on retourne la reponse attendue
                  else:   
                       # si hash incorrect = echec d authetification 
                       display.show(Image.NO)   
                       return ""   #return vide si echec et bebi affiche NO   

        sleep(100) # pause pour eviter de surcharger le bebi sinon il s'eteint

    display.show(Image.SAD)   # timeout, le parent n'as pas repondu a temps et le bebi affiche NO
    return ""   # return vide si echec

def main():     # ici je retiens que le gosse est actif 
    global connexion_established
    if not connexion_established:
        #ici il est actif il cherche a se connecter au parent
        if button_a.was_pressed():
            result = establish_connexion(key)
            if result :
                connexion_established = True

etats_sommeil = []
symboles = ["-", "1", "2"]
etat_actuel_symbole = "-"
musique_deja_jouee = False
# Fonction gérant l'état de sommeil du bébé
def etat_sommeil_bebe():
    global etat_actuel_symbole
    compteur = [0, 0, 0]
    # Composantes de l'accélération
    x = accelerometer.get_x()
    y = accelerometer.get_y()
    z = accelerometer.get_z()
    # Norme de l'accélération
    acceleration = math.sqrt((x**2) + (y**2) + (z**2))
    # "0" = endormi, "1" = agité, "2" = très agité
    if acceleration <= 1100:
        etats_sommeil.append(0)
    elif 1100 < acceleration <= 1800:
        etats_sommeil.append(1)
    else:
        etats_sommeil.append(2)
    # On supprime chaque fois le premier élément de la liste si plus de 12 éléments
    if len(etats_sommeil) == 12:
         etats_sommeil.pop(0)
    # Si 11 éléments dans la liste
    if len(etats_sommeil) == 11:
        for valeur in etats_sommeil:
            compteur[valeur] += 1
        etat_actuel = compteur.index(max(compteur))
        # On renvoie au bebi parent le symbole correspondant à l'état de sommeil
        etat_actuel_symbole = symboles[etat_actuel]
    # Prend une mesure toutes les secondes
    sleep(1000)

# Fonction jouant une musique pour le bébé
def musique():
	# Musique de Star Wars
	star_wars = [
    	"A4:2","A4:2","A4:2",
    	"F4:1","C5:1",
    	"A4:2","F4:1","C5:1","A4:4",
    	"E5:2","E5:2","E5:2",
    	"F5:1","C5:1",
    	"G5:2","F5:1","C5:1","A4:4",
    	"A5:2","A4:1","A4:1","A5:2","G5:1","F5:1",
    	"E5:2","D5:1","E5:1","F5:2","E5:4",
    	"E5:2","E5:2","E5:2",
    	"F5:1","C5:1",
    	"G5:2","F5:1","C5:1","A4:4",
    	"A5:2","A4:1","A4:1","A5:2","G5:1","F5:1",
    	"E5:2","D5:1","E5:1","F5:2","E5:4"
	]
	music.set_tempo(bpm=60) 
	music.play(star_wars)

def calcul_lumiere():
        if display.read_light_level() < 25 : 
            send_packet(key, "0x03", "lum eteinte")
        elif display.read_light_level() >= 25  and  display.read_light_level() <= 50 :
            send_packet(key, "0x03", "lum tres faible")
        elif display.read_light_level() >= 50  and  display.read_light_level() <= 75 :
            send_packet(key, "0x03", "lum faible")
        elif display.read_light_level() >= 75  and  display.read_light_level() <= 100 :
             send_packet(key, "0x03", "lum moyenne")
        elif display.read_light_level() >= 100  and  display.read_light_level() <= 125 :
             send_packet(key, "0x03", "lum bonne")
        elif display.read_light_level() >= 125  and  display.read_light_level() <= 150 :
             send_packet(key, "0x03", "lum normale")
        elif display.read_light_level() >= 150  and  display.read_light_level() <= 175 :
             send_packet(key, "0x03", "lum haute")
        elif display.read_light_level() >= 175  and  display.read_light_level() <= 200 :
             send_packet(key, "0x03", "lum tres haute")
        else :
             send_packet(key, "0x03", "lum extreme")

running = True
alarme_temp_active = False
while running :
    currentTemp = temperature()
    main()
    etat_sommeil_bebe()

    if currentTemp < temp_min:
        temp_min = currentTemp
    elif currentTemp > temp_max:
        temp_max = currentTemp
        
    # Lancement des différentes fonctions en fonction des messages reçus du bebi parent
    packet = radio.receive()
    if packet:
        type_msg, _, message = receive_packet(packet, key)
        if type_msg == "0x03":
            if message == "etat_sommeil":
                send_packet(key, "0x03", str(etat_actuel_symbole))
            elif message == "musique":
                musique()
            elif message == "temperature":
                send_packet(key, "0x03", str(currentTemp) + "degres")
            elif message == "lumiere":
                calcul_lumiere()
                        
	# Musique automatique si bébé très agité
    if etat_actuel_symbole == "2" and not musique_deja_jouee:
        musique()
        musique_deja_jouee = True
        
    if etat_actuel_symbole != "2":
        musique_deja_jouee = False

    if currentTemp <= 18 and not alarme_temp_active:
        send_packet(key, "0x03", "temp_basse")
        alarme_temp_active = True
    elif currentTemp >= 50 and not alarme_temp_active:
        send_packet(key, "0x03", "temp_haute")
        alarme_temp_active = True
    else:
        alarme_temp_active = False

    sleep(50)
