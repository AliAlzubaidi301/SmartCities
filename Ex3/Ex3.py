from machine import Pin, PWM, ADC, I2C
from time import sleep, ticks_ms, ticks_diff
from lcd1602 import LCD1602
import dht

# Initialisation des broches
potentiometre = ADC(Pin(26))  # A0 pour lire la consigne de température
led = PWM(Pin(18))            # LED sur la pin D18
led.freq(1000)
buzzer = PWM(Pin(20))         # Buzzer sur la pin D20

# Initialisation de l'I2C pour l'écran LCD et le capteur DHT
i2c_lcd = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
lcd = LCD1602(i2c_lcd, 2, 16)
lcd.display()

capteur_dht = dht.DHT11(Pin(16))  # Capteur DHT11 sur la pin D16

# Convertir la lecture du potentiomètre en température
def potentiometre_vers_temp(valeur):
    return 15.0 + (valeur / 65535.0) * 20.0

# Fonction pour l'animation de la LED (éclaircissement/diminution)
def animation_led(step=256, delay=0.006):
    for i in range(0, 65535, step):
        led.duty_u16(i)  # Augmenter la luminosité
        sleep(delay)
    for i in range(65535, 0, -step):
        led.duty_u16(i)  # Diminuer la luminosité
        sleep(delay)

# Fonction pour faire clignoter la LED à une fréquence donnée
def clignoter_led(frequence_hz, duree_s):
    periode = 1.0 / frequence_hz
    fin = ticks_ms() + int(duree_s * 1000)
    while ticks_ms() < fin:
        led.duty_u16(50000)  # LED allumée
        sleep(periode / 2)
        led.duty_u16(0)       # LED éteinte
        sleep(periode / 2)

# Fonction d'alarme avec animation (non-bloquante)
def boucle_alarme(consigne, temperature):
    buzzer.freq(1000)
    buzzer.duty_u16(30000)

    message = "!!! ALARME !!!   "
    etape = "defiler"
    i_defilement = 0
    dernier_lcd_ms = ticks_ms()
    DELAI_SCROLL_LCD = 150
    DELAI_CLIGNOTEMENT = 300
    compteur_clignotement = 0
    visible = True

    dernier_led_ms = ticks_ms()
    DELAI_LED = 80

    dernier_dht_ms = ticks_ms()
    DELAI_DHT = 1000
    dernier_pot_ms = ticks_ms()
    DELAI_POT = 150

    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.print(message)

    while True:
        maintenant = ticks_ms()

        # --- LED rapide en continu ---
        if ticks_diff(maintenant, dernier_led_ms) >= DELAI_LED:
            dernier_led_ms = maintenant
            if led.duty_u16() > 0:
                led.duty_u16(0)
            else:
                led.duty_u16(50000)

        # --- Animation LCD ---
        if etape == "defiler":
            if ticks_diff(maintenant, dernier_lcd_ms) >= DELAI_SCROLL_LCD:
                dernier_lcd_ms = maintenant
                lcd.scrollDisplayLeft()
                i_defilement += 1
                if i_defilement >= (len(message) + 25):
                    lcd.clear()
                    lcd.setCursor(0, 0)
                    lcd.print(message)
                    etape = "clignoter"
                    compteur_clignotement = 0
                    visible = True
                    dernier_lcd_ms = maintenant

        elif etape == "clignoter":
            if ticks_diff(maintenant, dernier_lcd_ms) >= DELAI_CLIGNOTEMENT:
                dernier_lcd_ms = maintenant
                if visible:
                    lcd.clear()
                else:
                    lcd.clear()
                    lcd.setCursor(0, 0)
                    lcd.print(message)
                visible = not visible
                compteur_clignotement += 1
                if compteur_clignotement >= 10:
                    etape = "defiler"
                    i_defilement = 0
                    lcd.clear()
                    lcd.setCursor(0, 0)
                    lcd.print(message)
                    dernier_lcd_ms = maintenant

        # Re-lecture du potentiomètre pour ajuster la consigne
        if ticks_diff(maintenant, dernier_pot_ms) >= DELAI_POT:
            dernier_pot_ms = maintenant
            consigne = potentiometre_vers_temp(potentiometre.read_u16())

        # Re-lecture de la température
        if ticks_diff(maintenant, dernier_dht_ms) >= DELAI_DHT:
            dernier_dht_ms = maintenant
            try:
                capteur_dht.measure()
                temperature = capteur_dht.temperature()
            except OSError:
                pass

        # Condition de sortie d'alarme
        if (temperature - consigne) <= 3:
            break

        sleep(0.01)

    buzzer.duty_u16(0)
    led.duty_u16(0)
    lcd.clear()

# Fonction principale
def main():
    while True:
        # Lecture des capteurs (hors alarme)
        consigne = potentiometre_vers_temp(potentiometre.read_u16())
        try:
            capteur_dht.measure()
            temperature = capteur_dht.temperature()
        except OSError:
            sleep(0.2)
            continue
        sleep(0.05)

        difference = temperature - consigne

        if difference <= 0:
            # Normal : LED respiration, LCD valeurs, buzzer off
            buzzer.duty_u16(0)
            lcd.clear()
            lcd.setCursor(0, 0)
            lcd.print("Consigne: {:.1f}C".format(consigne))
            lcd.setCursor(0, 1)
            lcd.print("Ambiante: {:.1f}C".format(temperature))
            animation_led()

        elif 0 < difference <= 3:
            # Vigilance : LED 0.5 Hz, LCD valeurs, buzzer off
            buzzer.duty_u16(0)
            lcd.clear()
            lcd.setCursor(0, 0)
            lcd.print("Consigne: {:.1f}C".format(consigne))
            lcd.setCursor(0, 1)
            lcd.print("Ambiante: {:.1f}C".format(temperature))
            clignoter_led(frequence_hz=0.5, duree_s=2)

        else:
            # Alarme : LED rapide + buzzer + LCD animé
            boucle_alarme(consigne, temperature)

# Lancer le programme
if __name__ == "__main__":
    main()
