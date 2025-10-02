from machine import Pin
import time

led = Pin(13, Pin.OUT)
btn = Pin(14, Pin.IN, Pin.PULL_DOWN)

ValeurClick = 1
bloque = False  
ValeurSlip = 0.5 

def btn_Click(pin):
    global ValeurClick, bloque
    if not bloque:          
        ValeurClick += 1
        if ValeurClick > 6:  
            ValeurClick = 1
        print(ValeurClick)
        bloque = True      

def ClignotementRapide():
    global ValeurSlip, ValeurClick
    
    if ValeurClick == 6:    
        led.value(0)
        time.sleep(0.1)       
    else:
        led.toggle()
        ValeurSlip = 0.5 / ValeurClick   
        time.sleep(ValeurSlip)

btn.irq(trigger=Pin.IRQ_RISING, handler=btn_Click)

while True:
    if btn.value() == 0:  
        bloque = False
    ClignotementRapide()
