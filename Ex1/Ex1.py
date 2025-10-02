
#Test
from machine import Pin
import time

led = Pin(13, Pin.OUT)
btn = Pin(14, Pin.IN, Pin.PULL_DOWN)

ValeurClick = 1
bloque = False  

def btn_Click(pin):
    global ValeurClick, bloque
    if bloque == False:          
        ValeurClick += 1

        if ValeurClick > 3:
            ValeurClick = 1

        print(ValeurClick)

        bloque = True      

def ClignotementRapide():
    if ValeurClick != 1: 
        return
    led.toggle()
    time.sleep(0.5)

def ClignotementPlusRapide():
    if ValeurClick != 2:
        return
    led.toggle()
    time.sleep(0.25)

def PasDeClignotement():
    if ValeurClick == 3:
        led.value(0) 

# Déclenche sur front descendant uniquement
# btn.irq(trigger=Pin.IRQ_FALLING, handler=callback)

# Déclenche sur les deux fronts
# btn.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=callback)

# Interruption 'hard' (exécution immédiate en contexte ISR)
# btn.irq(trigger=Pin.IRQ_RISING, handler=callback, hard=True)
btn.irq(trigger=Pin.IRQ_ | Pin.IRQ_FALLING, handler=btn_Click)

while True:
    if btn.value() == 0:
        bloque = False
    
    ClignotementRapide()
    ClignotementPlusRapide()
    PasDeClignotement()
