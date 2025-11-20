from microbit import *
import music

def nourrir() :
    
    while nourrir  :
        
        if  button_b.is_pressed() :

            display.clear()
            
            break
        
        else :
        
            faim = [Image.ANGRY, Image.ARROW_S]
        
            display.show(faim, delay=1000, loop=False)
    
            music.play(music.BA_DING)

def besoin_de_lait() :

    while True :

        nourrir()

        quantite_de_lait()
        
        sleep(10800000)
        

def quantite_de_lait() :

    index = 0 

    index += 1

def montrer_le_lait() :

    while True : 

        """combinaison de bouton"""

