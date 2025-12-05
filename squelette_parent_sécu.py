from microbit import *
import radio
import random
import music 

#Can be used to filter the communication, only the ones with the same parameters will receive messages
#radio.config(group=23, channel=2, address=0x11111111)
#default : channel=7 (0-83), address = 0x75626974, group = 0 (0-255)

#Initialisation des variables du micro:bit      
radio.on()
radio.config(group= , channel= , address =  )
connexion_established = False # Indique si la connexion est établie
key = "KEYWORD"               # Clé de chiffrement partagée entre les deux micro:bits
connexion_key = None          # Clé de connexion temporaire pour l'établissement de la connexion
nonce_list = set()            # Liste des nonces déjà vus pour éviter les rejets de connexion
baby_state = 0                # 0 : bébé calme, 1 : bébé qui pleure
set_volume(100)               # volume maximal

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

def main():        # le parent attend le signe de l'enfant
    global connexion_established
    global baby_state

    while True:
        if not connexion_established:
              # ici il est passif il attend la connexion du bebe
            result = respond_to_connexion_request(key)
            if result:
                 connexion_established = True
                 display.show(Image.HAPPY)  # connexion établie le micro:bit affiche HAPPY
        else:
            # le parent reçoit les status du bébé une fois connecté
            incoming = radio.receive()
            if incoming:
                packet_type, _ , message = receive_packet(incoming, key)  # voir comment mettre le msg

                if packet_type == "0x03":  
                    if message == "CRYING":               # packet_type = message 
                        baby_state = 1                     # l etat du bebe est qu il pleur si c'est 0 il ne se passe rien
                        display.show(Image.SAD)
                        music.play(music.POWER_DOWN) 

                    elif message == "GOOD" : # si le bebe est content
                        baby_state = 0
                        display.show(Image.HAPPY)   # indique que le bebe est content
                        music.play(music.POWER_UP)
        sleep(100)  # pause pour eviter de surcharger le parent sinon il s'eteint
main()
