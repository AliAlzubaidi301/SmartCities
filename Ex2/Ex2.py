# ==============================================================
#    - GP16 : buzzer (PWM)
#    - GP20 : LED (pour voir quand ca joue)
#    - GP28 : potentiometre (volume) 0..65535
#    - GP18 : bouton poussoir (next piste, anti-rebond)
#
#  Principe : on joue des listes (note, duree). Si on appui sur le
#         bouton poussoire, on coupe la note/melodie en cours immediatement
#         et on passe a la suivante (sans attendre la fin).
#
#  Le Potentiometre défènis le volume : je limite vers ~60% pour eviter son saturer
# ==============================================================

from machine import Pin, PWM, ADC
import time

# je crée les objects
bzr = PWM(Pin(16))              # buzzer 
bzr.freq(1000)                  # frequence de base (peu importe, on la change apres)

# --- LED améliorée : passe en PWM et suit le volume (luminosité proportionnelle) ---
led1 = PWM(Pin(20))             # LED en PWM (au lieu de sortie binaire)
led1.freq(1000)                 # fréquence PWM "confort" pour la LED (pas de scintillement)

potar = ADC(Pin(28))            # le potar pour regler le volume 
bp = Pin(18, Pin.IN, Pin.PULL_DOWN)  # bouton 

# ---------- Les notes ----------
# cle = nom de la note (style "A4"), valeur = frequence en Hz.
NOTES2 = {
    "A4": 440,  "AS4": 466, "B4": 494,
    "C5": 523,  "CS5": 554, "D5": 587, "DS5": 622, "E5": 659, "F5": 698, "FS5": 740,
    "G5": 784,  "GS5": 831, "A5": 880, "AS5": 932, "B5": 988,
    "C6": 1047, "CS6": 1109, "D6": 1175, "DS6": 1245, "E6": 1319, "F6": 1397, "FS6": 1480,
    "G6": 1568, "GS6": 1661, "A6": 1760, "AS6": 1865, "B6": 1976,
    "C7": 2093, "CS7": 2217, "D7": 2349, "DS7": 2489, "E7": 2637, "F7": 2794, "FS7": 2960,
    "G7": 3136, "A7": 3520
}

# ---------- "P" = Pause (silence) ----------
MELO_1 = [
    ("E7", 0.125), ("E7", 0.125), ("P", 0.125), ("E7", 0.125),
    ("P", 0.125), ("C7", 0.125), ("E7", 0.125), ("P", 0.125),
    ("G7", 0.125), ("P", 0.375), ("G6", 0.125), ("P", 0.375),
    ("C7", 0.125), ("P", 0.25),  ("G6", 0.125), ("P", 0.25),
    ("E6", 0.125), ("P", 0.25),  ("A6", 0.125), ("P", 0.125),
    ("B6", 0.125), ("P", 0.125), ("AS6",0.125), ("A6", 0.125),
    ("G6", 0.083), ("E7", 0.083), ("G7", 0.083), ("A7", 0.125),
    ("F7", 0.125), ("G7", 0.125), ("P", 0.125), ("E7", 0.125),
    ("C7", 0.125), ("D7", 0.125), ("B6", 0.125)
]

MELO_2 = [
    ("A4", 0.5), ("A4", 0.5), ("F5", 0.5), ("C6", 0.5),
    ("A5", 0.5), ("F5", 0.5), ("C6", 0.5), ("A5", 0.9),
    ("E5", 0.45), ("E5", 0.45), ("E5", 0.45), ("F5", 0.45),
    ("C6", 0.45), ("G5", 0.45), ("F5", 0.45), ("C6", 0.45),
    ("A5", 0.9)
]

MELO_3 = [
    ("D5", 0.25), ("D5", 0.25), ("D5", 0.25), ("D5", 0.25),
    ("D5", 0.25), ("F5", 0.25), ("G5", 0.5),
    ("A5", 0.25), ("A5", 0.25), ("A5", 0.25), ("A5", 0.25),
    ("A5", 0.25), ("G5", 0.25), ("F5", 0.5),
    ("D5", 0.25), ("F5", 0.25), ("G5", 0.5)
]

MELO_4 = [
    ("E6", 0.5), ("G6", 0.5), ("FS6", 0.5), ("E6", 0.5),
    ("B6", 0.75), ("A6", 0.25), ("FS6", 0.5), ("E6", 0.5),
    ("G6", 0.5), ("FS6", 0.5), ("D6", 0.75), ("E6", 0.25)
]

MELO_5 = [
    ("G5", 0.4), ("C6", 0.4), ("DS6", 0.4), ("F6", 0.8),
    ("G5", 0.4), ("C6", 0.4), ("DS6", 0.4), ("F6", 0.8),
    ("G5", 0.4), ("C6", 0.4), ("E6", 0.4),  ("F6", 0.8)
]

MELO_6 = [
    ("C6", 0.30), ("C6", 0.30), ("D6", 0.30), ("E6", 0.45),
    ("C6", 0.30), ("E6", 0.30), ("D6", 0.60),
    ("C6", 0.30), ("D6", 0.30), ("E6", 0.45), ("F6", 0.30), ("E6", 0.45),
    ("D6", 0.30), ("C6", 0.30), ("D6", 0.60)
]

MELO_7 = [
    ("G5", 0.40), ("G5", 0.40), ("A5", 0.40), ("F5", 0.40),
    ("G5", 0.40), ("A5", 0.40), ("B5", 0.80),
    ("A5", 0.40), ("B5", 0.40), ("C6", 0.80),
    ("B5", 0.40), ("A5", 0.40), ("G5", 0.80)
]

MELO_8 = [
    ("C6", 0.35), ("G5", 0.35), ("A5", 0.35), ("B5", 0.35),
    ("C6", 0.50), ("D6", 0.50), ("E6", 0.80),
    ("C6", 0.35), ("E6", 0.35), ("D6", 0.50), ("C6", 0.50),
    ("B5", 0.50), ("A5", 0.50), ("G5", 0.80)
]

MELO_9 = [
    ("E5", 0.35), ("F5", 0.35), ("G5", 0.35), ("A5", 0.50),
    ("G5", 0.35), ("F5", 0.35), ("E5", 0.50),
    ("E5", 0.35), ("F5", 0.35), ("G5", 0.35), ("A5", 0.50),
    ("G5", 0.35), ("F5", 0.35), ("E5", 0.80)
]

# Liste globale des Notes
PLAYLIST = [
    ("1) Piste", MELO_1),
    ("2) Piste", MELO_2),
    ("3) Piste", MELO_3),
    ("4) Piste", MELO_4),
    ("5) Piste", MELO_5),
    ("6) Piste", MELO_6),
    ("7) Piste", MELO_7),
    ("8) Piste", MELO_8),
    ("9) Piste", MELO_9),
]

idx = 0               # index de la piste courante dans PLAYLIST
stop_now = False      # quand il est a True on coupe immediatement ce qui joue
bp_old = 0            # memorise l'ancien etat du bouton (pour detecter le front)
t_last_ms = 0         # dernier instant d'appui (ms) pour l'anti-rebond
ANTI_REBOND_MS = 200  # 200 ms ca marche bien pr eviter les "sauts"


def volume_depuis_potar():
    """
    Lis le potar 16 bits (0..65535) et mappe vers 60% max.
    """
    brut = potar.read_u16()
    # 39321 = 0.6 * 65535
    return int((brut / 65535) * 39321)

def voir_bouton():
    """
    Detecte un front montant sur le bouton.
    Si un vrai clic est detecté on passe a la piste suivante immediatement
    (en mettant stop_now = True pour couper la note/melodie en cours).
    """
    global stop_now, idx, bp_old, t_last_ms
    etat = bp.value()
    now = time.ticks_ms()

    # front montant = ancien 0 -> nouveau 1
    if etat == 1 and bp_old == 0:
        # verif anti-rebond via delai mini
        if time.ticks_diff(now, t_last_ms) > ANTI_REBOND_MS:
            idx = (idx + 1) % len(PLAYLIST)   # next piste (on boucle)
            stop_now = True                   # demande d'arret immediat
            print("➡ Changement immédiat vers :", PLAYLIST[idx][0])
            t_last_ms = now  # mémorise le temps de ce clic

    # mise a jour pour la prochaine fois
    bp_old = etat

def jouer_une_note(nom_note, duree_s):
    """
    Joue une note pendant duree_s secondes.
    - Si nom_note == "P" -> c un silence (on attend mais de maniere "reactive")
    - A CHAQUE 10 ms : on re-lis le bouton, on maj le volume,
      et on coupe tout de suite si stop_now devient True.
    """
    global stop_now

    # cas du silence : on "attend" par petites tranches (10ms)
    if nom_note == "P":
        fin = time.ticks_add(time.ticks_ms(), int(duree_s * 1000))
        while time.ticks_diff(fin, time.ticks_ms()) > 0:
            voir_bouton()            # check bouton souvent = reactivite++
            if stop_now:
                return               # on sort direct si demande de stop
            time.sleep(0.01)
        # LED éteinte pendant le silence
        led1.duty_u16(0)
        return

    # note normale : on recupere la frequence
    f = NOTES2.get(nom_note, None)
    if f is None:
        # note inconnue -> on remplace par un silence "meme duree"
        jouer_une_note("P", duree_s)
        return

    # Configure la frequence PWM
    bzr.freq(f)

    # joue par tranches de 10ms pour rester arreteable a tout moment
    t_fin = time.ticks_add(time.ticks_ms(), int(duree_s * 1000))
    while time.ticks_diff(t_fin, time.ticks_ms()) > 0:
        voir_bouton()
        if stop_now:
            break  # on coupe net la note si clic

        # MAJ volume en live (on peut tourner le potar pendant la note)
        d = volume_depuis_potar()
        bzr.duty_u16(d if d > 0 else 0)

        # --- LED améliorée : luminosité = même duty que le son ---
        led1.duty_u16(d if d > 0 else 0)

        time.sleep(0.01)

    # fin de note (ou coupure) -> coupe le son et la LED
    bzr.duty_u16(0)
    led1.duty_u16(0)

def jouer_suite(notes_durees):
    global stop_now
    stop_now = False  
    for n, d in notes_durees:
        jouer_une_note(n, d)
        if stop_now:
            break  # on arrete la melodie courante sans attendre

while True:
    # on récupere la piste courante (label + contenu)
    label, suite = PLAYLIST[idx]
    print("▶ Lecture :", label)

    # on lance la lecture (interrompable)
    jouer_suite(suite)

    # si pas de clic, ca reboucle sur la meme piste = lecture continue
