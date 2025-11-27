from tkinter import Image
from microbit import *
import radio
import random
import music

#Can be used to filter the communication, only the ones with the same parameters will receive messages
#radio.config(group=23, channel=2, address=0x11111111)
#default : channel=7 (0-83), address = 0x75626974, group = 0 (0-255)



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
    # generer un nombre aleatoire pour aleatoire( 8 chiffres )
    nonce = str(random.randint(10000000, 99999999))  # Générer un nonce aleatoire
    display.scroll("N:" + nonce[:4]) # vas afficher les 4 premieers chiffres

    # on consrtuit le paquet de demande de connexion
    packet_type="CONNECT"
    content = nonce
    #Envoyer le challenge
    send_packet(key, packet_type, content)
    display.show(Image.ARROW_E)  # indique l'envoi du challenge en cours

    #Attendre la réponse (timeout de 2 secondes)
    start_time = running_time()
    timeout = 2000  #2secondes
    while running_time() - start_time < timeout:    
        response_packet = radio.receive()
        if response_packet:
            #Decrypte et déballe la reponse(paquet) réçue
            decrypted = vigenere(response_packet, key, decryption=True)
            parts = decrypted.split('|')

            if len(parts) == 3:
                 response_type = parts[0]
                 received_hash = parts[2]

                 # On verifie que c'est bie une reponse
                if response_type == "RESPONSE":
                    #Calculer ce que devrait etre le hash
                    expected_hash = hashing(nonce)

                    #Comparer
                    if received_hash == expected_hash:
                        display.show(Image.YES) #hash correct !
                        return True # la connexion est bien etablie
                    else:
                        display.show(Image.No) #hash incorrect
                        return False
        sleep(100)




        """  receive_packet(response_packet, key)
            if parts[0] == "RESPONSE":
                received_hash == parts[2].split('|')[0]   
                if received_hash == hashing(nonce):
                    return True                   
        sleep(100)  
    return False #indique le temps mort        

    #Programme principal
display.show(Image.SAD)
                 
                          #On Vérifie si c'est la reponse qu on attend
            expected_response = hashing(nonce)
                if response == expected_response:
                    display.show(Image.YES)    # indique la réception de la réponse correcte
                    return True  # la connexion est bien etablie
                else:
                    display.show(Image.NO)     #indique une réception incorrecte
                    return False  # échec de la reception de la réponse
        sleep(100)

    """
    

def main():
    return True
