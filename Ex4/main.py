from machine import Pin, ADC
from time import ticks_ms, ticks_diff, sleep_ms
import neopixel
import urandom

# Classe pour détecter un battement sonore
class DetecteurSon:
    def __init__(self, broche_micro=26, seuil=18000, delai_ms=100):  # Délai réduit à 100 ms
        # On prépare l'ADC sur la broche du micro
        self.micro = ADC(broche_micro)
        # Valeur au-dessus de laquelle on considère que c'est un battement
        self.seuil = seuil
        # Pour éviter de détecter 10 fois le même son
        self.delai_ms = delai_ms
        self.derniere_detection = 0

    def lire_niveau(self):
        """Lit la valeur brute du micro (0 -> 65535)."""
        return self.micro.read_u16()

    def detecter_battement(self):
        """Retourne True quand il y a un pic sonore."""
        maintenant = ticks_ms()
        valeur = self.lire_niveau()

        # On regarde si on a dépassé le seuil
        if valeur > self.seuil:
            # On vérifie aussi qu'on ne vient pas de détecter juste avant
            if ticks_diff(maintenant, self.derniere_detection) > self.delai_ms:
                self.derniere_detection = maintenant
                return True

        return False


# Programme principal
# - Utilise le détecteur de son
# - Change la couleur de la LED RGB à chaque battement
# - Calcule le BPM
# - Enregistre la moyenne chaque minute dans un fichier texte

# Paramètres matériel
BROCHE_LED = 18    # D18 sur la Pico
NB_LED = 1         # Nombre LED

def couleur_aleatoire(anneau):
    """Change la LED avec une couleur au hasard."""
    r = urandom.getrandbits(8)
    v = urandom.getrandbits(8)
    b = urandom.getrandbits(8)

    # Éviter le noir complet
    if r < 30 and v < 30 and b < 30:
        r = 255

    anneau[0] = (r, v, b)
    anneau.write()

def enregistrer_bpm(moyenne_bpm):
    """Écrit la valeur dans un fichier texte.
    On ouvre/écrit/ferme pour éviter de perdre les données.
    """
    try:
        with open("bpm.txt", "a") as f:
            f.write("BPM moyen : " + str(moyenne_bpm) + "\n")
    except OSError:
        # Si la carte n'aime pas écrire, on ignore juste
        pass

def main():
    # Initialisation matériel
    led = neopixel.NeoPixel(Pin(BROCHE_LED), NB_LED)
    detecteur = DetecteurSon()

    # Pour le calcul du BPM
    instants_battements = []  # On va stocker les temps des battements
    debut_minute = ticks_ms()  # Pour savoir quand 60 secondes sont passées

    # Petite couleur de départ
    led[0] = (0, 0, 50)
    led.write()

    while True:
        if detecteur.detecter_battement():
            # Changement de couleur à chaque battement
            couleur_aleatoire(led)

            # On enregistre l'instant du battement
            maintenant = ticks_ms()
            instants_battements.append(maintenant)

            # Pour éviter que la liste soit trop longue
            if len(instants_battements) > 20:
                instants_battements.pop(0)

        # Toutes les 60 secondes, on calcule une moyenne et on écrit
        maintenant = ticks_ms()
        if ticks_diff(maintenant, debut_minute) > 60_000:
            # Calcul du BPM moyen sur la minute
            bpm_moyen = 0

            if len(instants_battements) >= 2:
                # On calcule les intervalles entre battements
                intervalles = []
                for i in range(1, len(instants_battements)):
                    dt = ticks_diff(instants_battements[i], instants_battements[i-1])
                    intervalles.append(dt)

                if len(intervalles) > 0:
                    # Moyenne en ms
                    moyenne_ms = sum(intervalles) / len(intervalles)
                    # Conversion en BPM : 60000 ms / période
                    bpm_moyen = int(60000 / moyenne_ms)

            # On enregistre dans le fichier
            enregistrer_bpm(bpm_moyen)

            # On repart pour une nouvelle minute
            debut_minute = maintenant
            instants_battements = []

        # On évite de boucler trop vite
        sleep_ms(5)  # Moins de délai pour plus de réactivité

# Lance le programme
if __name__ == "__main__":
    main()
