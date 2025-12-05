#from tkinter import Image
from microbit import *
import radio
import random
import music

#Can be used to filter the communication, only the ones with the same parameters will receive messages
#radio.config(group=23, channel=2, address=0x11111111)
#default : channel=7 (0-83), address = 0x75626974, group = 0 (0-255)


radio.on()
radio.config(group = 32, channel = 6, address = 0x11111111, power = 6 )
key = "KEYWORD" # Clé de chiffrement partagée entre les deux micro:bits
connexion_established = False  # Clé de connexion temporaire pour l'établissement de la connexion

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
     # construction du format  TYPE|LONGUEUR|CONTENU/VALEUR
 
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
    # ici on calcule la reponse au challenge en hachant le challenge
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

    while True:
        if not connexion_established:
              #ici il est actif il cherche a se connecter au parent
            if button_a.was_pressed():
                result = establish_connexion(key)
                if result :
                    connexion_established = True
        else:
              # le bebi envoi un status
             if button_a.was_pressed():
                  send_packet(key, "0x03", "CRYING")   # le bebe est en pleur ( etat d'eveil du nourrisson)
                  display.show(Image.SAD)   # indique que le bebe pleur
                  music.play(music.BA_DING)   
             elif button_b.was_pressed():
                  send_packet(key, "0x03", "GOOD")  # le bebe est content
                  display.show(Image.HAPPY)   # indique que le bebe est content
                  music.play(music.POWER_UP) 
        sleep(100)  # pause pour eviter de surcharger le bebi sinon il s'eteint
        
