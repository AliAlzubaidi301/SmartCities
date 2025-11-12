import network
import ntptime
import time
import socket
import gc
from machine import Pin, PWM
from time import sleep

# Configuration du réseau Wi-Fi
SSID = "electroProjectWifi"
PASSWORD = "B1MesureEnv"

# Fonction de connexion Wi-Fi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connexion au Wi-Fi...", end="")
        wlan.connect(ssid, password)
        for _ in range(20):  # Timeout ~10s
            if wlan.isconnected():
                break
            print(".", end="")
            time.sleep(0.5)
        print()
    
    if wlan.isconnected():
        print("Connecté ! IP:", wlan.ifconfig()[0])
        return True
    else:
        print("Échec de la connexion Wi-Fi")
        return False

# Fonction de synchronisation de l'heure via NTP
def sync_time():
    try:
        # Déconnexion propre pour éviter les problèmes
        ntptime.host = "pool.ntp.org"  # facultatif, mais fiable
        ntptime.settime()
        print("Heure synchronisée !")
        return True
    except:
        print("Erreur ntptime. Réessai dans 5s...")
        return False

# Connexion au Wi-Fi et synchronisation de l'heure
if connect_wifi(SSID, PASSWORD):
    # Tente plusieurs fois de synchroniser l'heure
    for _ in range(3):
        if sync_time():
            break
        time.sleep(5)

# Configuration du pin pour le servo moteur
servo = PWM(Pin(16))  # Utilisation de Pin 16 pour le signal PWM
servo.freq(50)  # Fréquence pour les servos (50Hz)

# Fonction pour régler l'angle du servo
def set_angle(angle):
    duty = int((angle / 180) * 65535)  # Convertir l'angle en valeur PWM (0-65535)
    print(f"Définition de l'angle : {angle}° | Duty cycle : {duty}")
    servo.duty_u16(duty)  # Utilisation de duty_u16() au lieu de duty()

# Test de mouvement immédiat du servo
print("Test immédiat du servo moteur")
set_angle(90)  # Positionner le servo à 90° (heure 6)
sleep(2)  # Attendre 2 secondes pour voir si le servo bouge
set_angle(0)  # Retourner à 0° (heure 12)
sleep(2)

# Fonction pour récupérer l'heure actuelle en format 24h
def get_hour():
    # Récupérer l'heure actuelle du système (en UTC)
    year, month, day, hour, minute, second, weekday, yearday = time.localtime()
    return hour

# Fonction pour calculer l'angle basé sur l'heure
def calculer_angle_12h(hour):
    # Angle de 0 à 180° pour un cadran de 12 heures
    if hour == 12:
        return 0  # 12h correspond à 0°
    elif hour == 6:
        return 90  # 6h correspond à 90°
    else:
        return (hour % 12) * 30  # Chaque heure est un angle de 30°

# Fonction pour changer le fuseau horaire
def changer_fuseau_horaire(decalage):
    # Décalage UTC
    hour = get_hour() + decalage
    if hour < 0:
        hour += 24
    elif hour >= 24:
        hour -= 24
    return hour

# Fonction pour gérer le bouton poussoir (détecter un double clic)
def double_click(button):
    previous_state = button.value()
    first_click = None
    while button.value() == previous_state:
        time.sleep(0.01)  # Attente de changement d'état
    first_click = time.time()  # Enregistrer le premier clic
    while button.value() != previous_state:
        time.sleep(0.01)  # Attente du relâchement du bouton
    second_click = time.time()  # Enregistrer le deuxième clic
    if second_click - first_click < 1:  # Si les deux clics sont rapides
        return True
    return False

# Configuration du bouton poussoir
button = Pin(18, Pin.IN, Pin.PULL_UP)  # Bouton sur le pin 18

# Variables de fuseau horaire
fuseau_horaire = 0  # UTC par défaut

# Mode 12h ou 24h
mode_24h = False  # Mode 24h désactivé par défaut

# Boucle principale
while True:
    # Vérifier si le bouton est double-cliqué pour changer le mode (24h)
    if double_click(button):
        mode_24h = not mode_24h
        print("Mode 24h activé" if mode_24h else "Mode 12h activé")
        sleep(1)

    # Récupérer l'heure
    hour = get_hour()

    # Ajuster l'heure pour le fuseau horaire
    hour = changer_fuseau_horaire(fuseau_horaire)

    # Si en mode 24h, calculer l'angle entre 0 et 180°
    if mode_24h:
        angle = (hour / 24) * 180  # De 0° (00h) à 180° (24h)
    else:
        # Si en mode 12h, calculer l'angle en fonction de l'heure 12h-12h
        angle = calculer_angle_12h(hour)

    # Afficher l'angle du servo pour l'heure actuelle
    print(f"Heure: {hour} - Angle: {angle}°")
    set_angle(angle)  # Déplacer le servo moteur à l'angle calculé

    # Attendre 1 minute avant de mettre à jour
    sleep(60)

# Nettoyage mémoire
gc.collect()
