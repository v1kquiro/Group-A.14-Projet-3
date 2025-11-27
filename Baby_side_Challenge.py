from microbit import *
import radio
import random
import music

#Can be used to filter the communication, only the ones with the same parameters will receive messages
#radio.config(group=23, channel=2, address=0x11111111)
#default : channel=7 (0-83), address = 0x75626974, group = 0 (0-255)

radio.config(group=32) #l'alimentation pour recevoir les msgs etc pour microbit

radio.on()
radio.config(group=32, power=6) #avoir access a recevoir les msgs


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
    
#Calculate the challenge response
def calculate_challenge_response(challenge):
    """
    Calcule la réponse au challenge initial de connection avec l'autre micro:bit

    :param (str) challenge:            Challenge reçu
	:return (srt)challenge_response:   Réponse au challenge
    """
    
#Ask for a new connection with a micro:bit of the same group
def establish_connexion(key):
    """
    Etablissement de la connexion avec l'autre micro:bit
    Si il y a une erreur, la valeur de retour est vide

    :param (str) key:                  Clé de chiffrement
	:return (srt)challenge_response:   Réponse au challenge
    """

etats_sommeil = []
symboles = ["-", "1", "2"]
def etat_sommeil_bebe():
    compteur = [0, 0, 0]
    x = accelerometer.get_x()
    y = accelerometer.get_y()
    z = accelerometer.get_z()
    # Norme de l'accélération
    acceleration = math.sqrt((x**2) + (y**2) + (z**2))
    # "-" = endormi, "1" = agité, "2" = très agité
    if acceleration <= 1100:
        etats_sommeil.append(0)
    elif 1100 < acceleration <= 1500:
        etats_sommeil.append(1)
    else:
        etats_sommeil.append(2)
    if len(etats_sommeil) == 12:
         etats_sommeil.pop(0)
    if len(etats_sommeil) == 11:
        for valeur in etats_sommeil:
            compteur[valeur] += 1
        etat_actuel = compteur.index(max(compteur))
        display.show(symboles[etat_actuel])
    sleep(100)

def musique():
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

def main():
    return True
while running :
	    message = radio.receive()
    if message:
        display.scroll(message)


"""renvoi la luminosité au be:bi parent => manque la fct send package"""

def nv_de_lum():

    if display.read_light_level() < 25 : 

        """envoi d' un package disant lumière éteinte et 0"""
    
    elif display.read_light_level() >= 25  and  display.read_light_level() <= 50 :

       """envoi d' un package disant lumière presque éteinte et 1"""

    elif display.read_light_level() >= 50  and  display.read_light_level() <= 75 :

        """envoi d' un package disant lumière très faible et 2"""

    elif display.read_light_level() >= 50  and  display.read_light_level() <= 75 :

         """envoi d' un package disant lumière  faible et 3"""

    elif display.read_light_level() >= 75  and  display.read_light_level() <= 100 :

        """envoi d' un package disant lumière moyenne et 4"""

    elif display.read_light_level() >= 100  and  display.read_light_level() <= 125 :

        """envoi d' un package disant lumière  bonne et  5"""

    elif display.read_light_level() >= 125  and  display.read_light_level() <= 150 :

        """envoi d' un package disant lumière  normale et 6"""   
        
    elif display.read_light_level() >= 150  and  display.read_light_level() <= 175 :

        """envoi d' un package disant lumière  haute et 7""" 


    elif display.read_light_level() >= 175  and  display.read_light_level() <= 200 :

        """envoi d' un package disant lumière très haute et 8"""

    else :

        """"envoi d' un package disant lumière extrème et 9"""

	while True:
		temp = temperature()
		radio.send("TEMP" + str(temp))

		msg = radio.receive()
		if msg:
			if msg == "TEMP":
				radio.send("TEMP"+str(temp))
				display.clear()

		"""calcul le nv de lumière pour pouvoir couper la lumière des leds du be:bi"""
    	if display.read_light_level() < 25 :
            
            for larg in range(5) :
                
                for haut in range(5) :
                   
                    display.set_pixel(larg,haut,0)

