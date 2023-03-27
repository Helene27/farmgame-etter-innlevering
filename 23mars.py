# bakgrunn av LuminousDragonGames, hentet fra https://opengameart.org/content/perfectly-seamless-grass
# pug-animasjon av AntumDeluge, hentet fra https://opengameart.org/content/pug-rework
# høne-animasjon av AntumDeluge, hentet fra https://opengameart.org/content/chick
# musikk av Alexandr Zhelanov, hentet fra https://opengameart.org/content/casual-game-track
# bjeffe-lyd av apolloaiello, hentet fra https://pixabay.com/sound-effects/small-dog-81977/
# hønelyd av IMadeIt, hentet fra https://opengameart.org/content/chicken-sound-effect
# wooshelyd av Nightflame, hentet fra https://pixabay.com/sound-effects/swinging-staff-whoosh-strong-08-44658/
# kilde til hvordan legge til tekst: https://www.geeksforgeeks.org/python-display-text-to-pygame-window/ 
# høyballer, lyn og hønsehus tegnet av Thea i Gimp

# kilde til inspirasjon til henting av og animasjon med spritesheets fra coding with russ på youtube:
    # https://www.youtube.com/watch?v=M6e3_8LHc7A
    # https://www.youtube.com/watch?v=nXOVcOBqFwM&t=757s




# importerer pygame-biblioteket
import pygame as pg
# importerer sys som hjelper med å lukke spillet
import sys
# importerer randint og randrange funksjonene fra random-biblioteket
from random import randint, randrange


# Konstanter
WIDTH = 1000  # bredden til vinduet
HEIGHT = 600 # høyden til vinduet
SIZE = (WIDTH, HEIGHT) # størrelsen til vinduet

BLUE = (80,210,240)
WHITE = (255,255,255)


# Initiere pygame
pg.init()

# Lager en overflate (surface) vi kan tegne på
surface = pg.display.set_mode(SIZE)


# henter inn bakgrunnsbilde (med dimensjoner 384 × 224)
backgroundImg = pg.image.load("bilder/gress.png")
#skalerer bakgrunnsbilde til ønsket størrelse
backgroundImg = pg.transform.scale(backgroundImg, (WIDTH,HEIGHT))


#laster inn musikkfilen
pg.mixer.music.load("lyd/gamemusic.ogg")
#spiller musikken (-1 ganger gir at den loopes evig)
pg.mixer.music.play(loops=-1)
#setter musikkvolumet (verdi mellom 0 og 1)
pg.mixer.music.set_volume(0.5)


#henter inn bjeffe-lyd
barking = pg.mixer.Sound("lyd/dog.ogg")
#lager en variabel som sier at bjeffe-lyden ikke skal spilles
play_barking = False

#henter inn kakle-lyd
cackling = pg.mixer.Sound("lyd/chicken.ogg")
#lager en variabel som sier at kakle-lyden ikke skal spilles
play_cackling = False

#henter inn wooshe-lyd
woosh = pg.mixer.Sound("lyd/woosh.mp3")

#henter font og skriftstørrelse
font = pg.font.SysFont("Arial",48)




# lager en liste som sier hvor mange bilder det er i hver animasjon
animation_steps = 3
# lager en timer som sier hvor ofte animasjonen skal endre
last_update = pg.time.get_ticks()
# i millisekunder
animation_cooldown = 100




#lager en klasse for hundens spritesheet
class SpriteSheet():
    #konstruktør
    def __init__(self, image):
        self.sheet = image
    
    #metode som henter kun det bildet vi skal vise fra spritesheetet
    def get_image(self, frame, width, height, scale, direction):
        #sier at om figuren beveger seg opp skal vi bruke den øverste rekken med bilder
        if direction == "up":
            y = height*0
        #om figuren beveger seg til høyre skal vi bruke rekke nummer 2 med bilder
        if direction == "right":
            y = height*1
        #om figuren beveger seg ned skal vi bruke rekke nummer 3 med bilder
        if direction == "down":
            y = height*2
        #om figuren beveger seg til venstre skal vi bruke rekke nummer 4 med bilder
        if direction == "left":
            y = height*3
        #lager et surface til bildet
        image = pg.Surface((width, height)).convert_alpha()
        #tegner kun det bildet fra spritesheetet vi vil ha (frame*width gir det bildet bortover vi vil ha)
        image.blit(self.sheet, (0,0), ((frame * width), y, width, height))
        #skalerer bildet til størrelsen vi vil ha
        image = pg.transform.scale(image, (width * scale, height * scale))
    
        #returnerer den skalerte versjonen av bildet vi skal vise
        return image




#lager en klasse for kyllingens spritesheet som fungerer på lik måte som SpriteSheet-klassen
class SpriteSheetChick():
    #konstruktør
    def __init__(self, image):
        self.sheet = image
    
    #metode som henter kun det bildet vi skal bruke fra spritesheetet
    def get_image(self, frame, width, height, scale, direction):
        if direction == "up":
            y = 38
        if direction == "right":
            y = 38+62
        if direction == "down":
            y = 38+124
        if direction == "left":
            y = 38+184
        image = pg.Surface((width, height)).convert_alpha()
        image.blit(self.sheet, (0,0), ((frame*48 + 11), y, width, height))
        image = pg.transform.scale(image, (width * scale, height * scale))
    
        return image




#henter først spritesheetet med 12 pug-bilder (convert_alpha gjør at bildet bruker samme pixel-format som skjermen)
sprite_sheet_image = pg.image.load("bilder/pug.png").convert_alpha()
#sender spritesheetet gjennom SpriteSheet-klassen, slik at det blir skalert og delt opp i 12 enkeltbilder
sprite_sheet = SpriteSheet(sprite_sheet_image)

#henter spritesheetet med 12 kylling-bilder
sprite_sheet_image2 = pg.image.load("bilder/chick.png").convert_alpha()
#skalerer og deler opp spritesheetet i 12 enkeltbilder
sprite_sheet2 = SpriteSheetChick(sprite_sheet_image2)




# klasse for karakterene
class Character:
    # konstruktør
    def __init__(self, x, y, image, direction, size, scale, sprite_sheet): 
        self.x = x
        self.y = y
        self.image = image
        self.size = size
        self.scale = scale
        self.sprite_sheet = sprite_sheet
        
        #laster inn bilde
        self.characterImg = pg.image.load(image)
        
        #får høyden og bredden til karakteren ved å finne rektangelet rundt karakteren
        self.characterRect = self.characterImg.get_rect()
        self.h = self.characterRect.height
        self.w = self.characterRect.width
        
        #setter en x- og y-fart til karakteren
        self.vx = 0
        self.vy = 0
        
        #retning den begynner å peke i
        self.direction = direction
        #lengde siden sist gang animasjonen oppdaterte seg begynner på 0 millisekunder når programmet kjøres
        self.last_update = 0
        #begynner på det første bildet i animasjonen
        self.frame = 0
        
    
    #lager en metode som tegner karakteren til skjermen
    def draw(self):
        #tom liste for hvilken frame vi skal vise
        animation_list = []
        #itererer gjennom bildene i animasjonen og legger det til i listen, slik at vi vet hvor langt vi er kommet i animasjonen
        for i in range(animation_steps):
            animation_list.append(self.sprite_sheet.get_image(i, self.size, self.size, self.scale, self.direction))
        
        # henter hvor lang tid det har gått akkurat nå
        current_time = pg.time.get_ticks()
        #oppdaterer seg hvis det har gått lengre tid enn cooldownen
        if current_time - self.last_update >= animation_cooldown:
            #sier at den kun skal endre frames om karakteren beveger seg
            if not(self.vy == 0 and self.vx == 0):
                #sier at vi skal til neste frame
                self.frame += 1
                #oppdaterer tiden slik at cooldown starter på nytt
                self.last_update = current_time
                #hvis vi er på siste frame, starter animasjonen på nytt
                if self.frame >= len(animation_list):
                    self.frame = 0
        
        #tegner animasjonen til skjerm
        surface.blit(animation_list[self.frame], (self.x, self.y))
       
    
    #metode som oppdaterer posisjonen til karakteren
    def update(self):
        self.x += self.vx
        self.y += self.vy
       



#lager en klasse for pug-karakteren som arver av karakter-klassen
class Pug(Character):
    #konstruktør
    def __init__(self, x, y, image, direction, size, scale, sprite_sheet):
        super().__init__(x, y, image, direction, size, scale, sprite_sheet)
        # sier at karakteren ikke er skjult, og den skal derfor vises - bruker dette lengre ned i programmet
        self.hidden = False
        
    
    #metode som gjør at karakteren kan bevege seg
    def move(self):
        #gir fart = 0 her slik at figuren står stille når ingen knapper trykkes
        self.vx = 0
        self.vy = 0
       
        #henter inn status på tastaturknappene - om de blir trykket på
        keys  = pg.key.get_pressed()
        
        #sjekker om venstre piltast trykkes på
        if keys[pg.K_LEFT]:
            #setter karakterens retning til å gå mot venstre
            self.direction = "left"
            #gir kollisjon med venstre vegg
            if self.x > 0:
                #gir fart mot venstre
                self.vx = -4
        
        #elif gjør at den ikke kan gå på skrå, men også at vi kun har én direction-verdi lagret om gangen
        #sjekker om høyre piltast trykkes på
        elif keys[pg.K_RIGHT]:
            #setter karakterens retning til å gå mot høyre
            self.direction = "right"
            #gir kollisjon med høyre vegg
            if self.x + self.size + 11 < WIDTH:
                #gir fart mot høyre
                self.vx = 4
        
        #sjekker om piltast opp trykkes på
        elif keys[pg.K_UP]:
            #setter karakterens retning til å gå opp
            self.direction = "up"
            #gir kollisjon med toppen
            if self.y + 11 > 0:
                #gir fart oppover
                self.vy = -4
        
        #sjekker om piltast ned trykkes på
        elif keys[pg.K_DOWN]:
            #setter karakterens retning til å gå ned
            self.direction = "down"
            #gir kollisjon med bunnen
            if self.y + self.size + 16 < HEIGHT:
                #gir fart nedover
                self.vy = 4
        



#lager en klasse for kylling-karakteren som arver av karakter-klassen
class Chick(Character):
    #konstruktør
    def __init__(self, x, y, image, direction, size, scale, sprite_sheet):
        super().__init__(x, y, image, direction, size, scale, sprite_sheet)
        self.hidden = False
    
    #metode for kyllingens bevegelse
    def move(self):
        self.vx = 0
        self.vy = 0
       
        #henter inn status på tastaturknappene - om de blir trykket på
        keys = pg.key.get_pressed()
        
        #sjekker om knappen "a" blir trykket på
        if keys[pg.K_a]:
            self.direction = "left"
            #gir kollisjon med venstre vegg
            if self.x > 0:
                #gir fart mot venstre
                self.vx = -4
        
        #sjekker om knappen "d" blir trykket på
        elif keys[pg.K_d]:
            self.direction = "right"
            #gir kollisjon med høyre vegg
            if self.x + self.size + 11 < WIDTH:
                #gir fart mot høyre
                self.vx = 4
        
        #sjekker om knappen "w" blir trykket på
        elif keys[pg.K_w]:
            self.direction = "up"
            #gir kollisjon med toppen
            if self.y + 11 > 0:
                #gir fart oppover
                self.vy = -4
        
        #sjekker om knappen "s" blir trykket på
        elif keys[pg.K_s]:
            self.direction = "down"
            #gir kollisjon med bunnen
            if self.y + self.size + 22 < HEIGHT:
                #gir fart nedover
                self.vy = 4




#lager en klasse for rektangler/firkanter
class Rektangel:
    #konstruktør
    def __init__(self, x, y, w, h, image, scale):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.image = image
        self.scale = scale
        #henter inn bildet til objektet
        self.rektangelImg = pg.image.load(self.image)
        #skalerer objektet
        self.rektangelImg = pg.transform.scale(self.rektangelImg, (self.w * self.scale, self.h * self.scale))
        #lager et rektangel rundt objektet
        self.rektangelRect = self.rektangelImg.get_rect()
        #henter x- og y-verdien til det skalerte objektet (brukt i kollisjonene)
        self.rektangelRect.x = x
        self.rektangelRect.y = y
        #henter høyden og bredden til det skalerte objektet
        self.h = self.rektangelRect.height
        self.w = self.rektangelRect.width
    
    #metode som tegner objektet
    def draw(self):
        surface.blit(self.rektangelImg, (self.x, self.y))





game_version = randint(1,5)

def gamemaker():
    global hoyballer, lyn, pug, chick, honsehus
    global play_cackling, play_barking
    #lager en tom liste for høyballene
    hoyballer = []
    #lager en tom liste for lynene
    lyn = []

    play_cackling = False
    play_barking = False
    
    pg.mixer.music.play()

    #lager en variabel som tilfeldig sier hvilken av spillversjonene som skal kjøres
    #game_version = randint(1,5)
    #game_version = 5

    #spillversjon 1
    if game_version == 1:
        #lager høyballobjekter
        hoyballer.append(Rektangel(100*8, 50, 64, 64, "bilder/hoyball.png", 1.5625))
        hoyballer.append(Rektangel(100*6, 100 + 50, 64, 64, "bilder/hoyball.png", 1.5625))
        hoyballer.append(Rektangel(100*4, 100*2 + 50, 64, 64, "bilder/hoyball.png", 1.5625))
        hoyballer.append(Rektangel(100*2, 100*3 + 45, 64, 64, "bilder/hoyball.png", 1.5625))
        hoyballer.append(Rektangel(100*7, 100*4 + 45, 64, 64, "bilder/hoyball.png", 1.5625))
        
        #lager flere høyballer samtidig, i rekker eller kolonner
        for i in range(2):
            hoyballer.append(Rektangel(100*8 + i*100, 100 + 50, 64, 64, "bilder/hoyball.png", 1.5625))
            hoyballer.append(Rektangel(100*6 + i*100, 100*3 + 45, 64, 64, "bilder/hoyball.png", 1.5625))
            
        for i in range(3):
            hoyballer.append(Rektangel(100*4 + i*100, 50, 64, 64, "bilder/hoyball.png", 1.5625))
            hoyballer.append(Rektangel(100*2 + i*100, 100*4 + 45, 64, 64, "bilder/hoyball.png", 1.5625))
        
        
        #pug objekt
        pug = Pug(300, 190, "bilder/pug.png", "right", 32, 1.5, sprite_sheet)

        #kylling objekt
        chick = Chick(910, 500, "bilder/chick.png", "left", 26, 1.8, sprite_sheet2)

        #hønsehus objekt
        honsehus = Rektangel(50,40,50,50, "bilder/honsehus.png", 4)
        
        #lyn objekt
        lyn.append(Rektangel(435,375,13,22,"bilder/lyn.png",1.8))
        lyn.append(Rektangel(90,430,13,22,"bilder/lyn.png",1.8))
        lyn.append(Rektangel(835,5,13,22,"bilder/lyn.png",1.8))
        
        
        
        
    #spillversjon 2 
    if game_version == 2:
        #høyballobjekter
        hoyballer.append(Rektangel(100, 100*3, 64, 64, "bilder/hoyball.png", 1.5625))
        hoyballer.append(Rektangel(100*2, 100, 64, 64, "bilder/hoyball.png", 1.5625))
        hoyballer.append(Rektangel(100*3, 100, 64, 64, "bilder/hoyball.png", 1.5625))

        for i in range(2):
            hoyballer.append(Rektangel(100*3, 100*3 + i*100, 64, 64, "bilder/hoyball.png", 1.5625))
            hoyballer.append(Rektangel(100*5, 100*2 + i*100, 64, 64, "bilder/hoyball.png", 1.5625))
            hoyballer.append(Rektangel(100*6, 100*3 + i*100, 64, 64, "bilder/hoyball.png", 1.5625))
            hoyballer.append(Rektangel(100*8, 100*4 + i*100, 64, 64, "bilder/hoyball.png", 1.5625))

        
        #pug objekt
        pug = Pug(650, 120, "bilder/pug.png", "left", 32, 1.5, sprite_sheet)

        #kylling objekt
        chick = Chick(40, 500, "bilder/chick.png", "right", 26, 1.8, sprite_sheet2)

        #hønsehus objekt
        honsehus = Rektangel(760,40,50,50, "bilder/honsehus.png", 4)

        #lyn objekter
        lyn.append(Rektangel(435,340,13,22,"bilder/lyn.png",1.5))
        lyn.append(Rektangel(630,540,13,22,"bilder/lyn.png",1.5))
        lyn.append(Rektangel(85,75,13,22,"bilder/lyn.png",1.5))
        
        
            

    # spillversjon 3
    if game_version == 3:
        #høyballobjekter
        hoyballer.append(Rektangel(100*3, 100, 64, 64, "bilder/hoyball.png", 1.5625))
        hoyballer.append(Rektangel(100*5, 0, 64, 64, "bilder/hoyball.png", 1.5625))
        hoyballer.append(Rektangel(100*8, 100*2, 64, 64, "bilder/hoyball.png", 1.5625))
        hoyballer.append(Rektangel(100*6, 100*4, 64, 64, "bilder/hoyball.png", 1.5625))
        
        for i in range(2):
            hoyballer.append(Rektangel(100, 100*3 + i*100, 64, 64, "bilder/hoyball.png", 1.5625))
            hoyballer.append(Rektangel(100*2, 100 + i*100*3, 64, 64, "bilder/hoyball.png", 1.5625))
            hoyballer.append(Rektangel(100*7, 100 + i*100, 64, 64, "bilder/hoyball.png", 1.5625))

        for i in range(3):
            hoyballer.append(Rektangel(100*4, 600-100*(i+1), 64, 64, "bilder/hoyball.png", 1.5625))
            

        #pug objekt
        pug = Pug(100*5 + 30, 100*5 + 30, "bilder/pug.png", "up", 32, 1.7, sprite_sheet)

        #kylling objekt
        chick = Chick(34, 34, "bilder/chick.png", "right", 26, 2, sprite_sheet2)

        #hønsehus objekt
        honsehus = Rektangel(800,400,50,50, "bilder/honsehus.png", 4)

        #lyn objekt
        lyn.append(Rektangel(280,270,13,22,"bilder/lyn.png",2))
        lyn.append(Rektangel(550,200,13,22,"bilder/lyn.png",2))




    #spillversjon 4
    if game_version == 4:
        #høyballobjekter
        hoyballer.append(Rektangel(100*2, 0, 64, 64, "bilder/hoyball.png", 1.5625))
        hoyballer.append(Rektangel(100*5, 100 * 3, 64, 64, "bilder/hoyball.png", 1.5625))
        
        for i in range(2):
            hoyballer.append(Rektangel(100 + i*100, 100*2, 64, 64, "bilder/hoyball.png", 1.5625))
            hoyballer.append(Rektangel(100*4 + i*100, 100*4, 64, 64, "bilder/hoyball.png", 1.5625))
            hoyballer.append(Rektangel(100*7, 100 * 3 + i * 100, 64, 64, "bilder/hoyball.png", 1.5625))
            hoyballer.append(Rektangel(100*8, 100 * 2 + i * 100, 64, 64, "bilder/hoyball.png", 1.5625))
            
        for i in range(3):
            hoyballer.append(Rektangel(100*4 + i*100, 100, 64, 64, "bilder/hoyball.png", 1.5625))


        #pug objekt
        pug = Pug(100*2.8, 100*3.5, "bilder/pug.png", "right", 32, 1.5, sprite_sheet)

        #kylling objekt
        chick = Chick(910, 34, "bilder/chick.png", "left", 26, 1.8, sprite_sheet2)

        #hønsehus objekt
        honsehus = Rektangel(50,350,50,50, "bilder/honsehus.png", 4)

        #lyn objekt
        lyn.append(Rektangel(230,125,13,22,"bilder/lyn.png",2))
        lyn.append(Rektangel(630,300,13,22,"bilder/lyn.png",2))
        lyn.append(Rektangel(880,480,13,22,"bilder/lyn.png",2))




    #spillversjon 5
    if game_version == 5:
        #høyballobjekter
        hoyballer.append(Rektangel(64*10, 64*5, 64,  64, "bilder/hoyball.png", 1))
        hoyballer.append(Rektangel(64*14 - 5, 64*2, 64,  64, "bilder/hoyball.png", 1))
        
        for i in range(2):
            hoyballer.append(Rektangel(0, 64*3 + 64*i, 64,  64, "bilder/hoyball.png", 1))
            hoyballer.append(Rektangel(64, 64*3 + 64*i, 64,  64, "bilder/hoyball.png", 1))
            hoyballer.append(Rektangel(64*2, 64*6 + 64*i, 64,  64, "bilder/hoyball.png", 1))
            hoyballer.append(Rektangel(64*5, 64*6 + 64*i, 64,  64, "bilder/hoyball.png", 1))
            hoyballer.append(Rektangel(64*3 + i*64, 64*7, 64,  64, "bilder/hoyball.png", 1))
            hoyballer.append(Rektangel(64*4, 64*3 + i*64, 64,  64, "bilder/hoyball.png", 1))
            hoyballer.append(Rektangel(64*10 + i*64, 64, 64,  64, "bilder/hoyball.png", 1))
            hoyballer.append(Rektangel(64*10 + i*64, 64*4, 64,  64, "bilder/hoyball.png", 1))
            hoyballer.append(Rektangel(64*8, 64*3 + i*64, 64,  64, "bilder/hoyball.png", 1))
            hoyballer.append(Rektangel(64*7, 64*6 + i*64, 64,  64, "bilder/hoyball.png", 1))
            hoyballer.append(Rektangel(64*2, i*64, 64,  64, "bilder/hoyball.png", 1))
            hoyballer.append(Rektangel(64*13 - 5, 64 + i*64, 64,  64, "bilder/hoyball.png", 1))
            
            
        for i in range(3):
            hoyballer.append(Rektangel(64*4 + i*64, 64*2, 64,  64, "bilder/hoyball.png", 1))
            hoyballer.append(Rektangel(64*13, 64*4 + i*64, 64,  64, "bilder/hoyball.png", 1))
        
        for i in range(4):
            hoyballer.append(Rektangel(64*10 + i*64, 64*7, 64,  64, "bilder/hoyball.png", 1))
            
        
        #pug objekt
        pug = Pug(64*6 * 1.5 + 10, 64*4 * 1.5, "bilder/pug.png", "left", 32, 1.3, sprite_sheet)

        #kylling objekt
        chick = Chick(34, 34, "bilder/chick.png", "down", 26, 1.5, sprite_sheet2)

        #hønsehus objekt
        honsehus = Rektangel( 64*11, 64*5,50,50, "bilder/honsehus.png", 2.54)

        #lyn objekt
        lyn.append(Rektangel(50,450,13,22,"bilder/lyn.png",1.5))
        lyn.append(Rektangel(530,75,13,22,"bilder/lyn.png",1.5))
        lyn.append(Rektangel(64*6 + 20,64*4 + 11,13,22,"bilder/lyn.png",1.5))
        lyn.append(Rektangel(935, 375,13,22,"bilder/lyn.png",1.5))



#global hoyballer, lyn, pug, chick, honsehus
#lager en tekst dersom hunden vinner som kan vises til skjerm med hvit skrift og blå bakgrunn
textPug = font.render("Pug vinner! trykk enter", True, WHITE,BLUE)
#finner rektangelet rundt teksten
textRectPug = textPug.get_rect()
#setter midten til tekstens rektangel = midten av hele skjermen
textRectPug.center = (WIDTH // 2, HEIGHT // 2)


#lager tekst dersom kyllingen vinner
textChick = font.render("Kylling vinner! trykk enter", True, WHITE,BLUE)
#finner rektangelet rundt teksten
textRectChick = textChick.get_rect()
#setter midten til tekstens rektangel = midten av hele skjermen
textRectChick.center = (WIDTH // 2, HEIGHT // 2)


def gameplayer():
    global hoyballer, lyn, pug, chick, honsehus
    #lager en metode som sjekker kollisjon mellom kyllingen og hønsehuset, altså om kyllingen vinner
    def collisionChickHonsehus(chick, honsehus):
        #henter den globale variabelen som sier om kakle-lyd kan spilles
        global play_cackling
        #sjekker om kyllingens x-verdi kolliderer med hønsehusets x-verdi
        if chick.x + chick.size - 11 >= honsehus.x and chick.x + 38 <= honsehus.x + honsehus.w:
            #sjekker om kyllingens y-verdi kolliderer med hønsehusets y-verdi
            if chick.y + chick.size >= honsehus.y and chick.y + 38 <= honsehus.y + honsehus.h:
                #pug skal bli borte dersom kylling vinner
                pug.hidden = True
                
                #stopper bakgrunnsmusikk
                pg.mixer.music.stop()
                #spiller kakle-lyd så lenge den ikke allerede spilles (dette gjør at den bare spilles én gang og ikke oppå seg selv)
                if not play_cackling:
                    #sier at kakle-lyden kan spilles
                    play_cackling = True
                    #spiller kaklelyd
                    cackling.play()
                   
        
                    
                
                
                #skriver vinnertekst for kyllingen
                surface.blit(textChick, textRectChick)
         



    #lager en metode som sjekker kollisjon mellom hunden og kyllingen, altså om hunden vinner
    def collisionPugChick(pug, chick):
        #henter den globale variabelen som sier om bjeffe-lyd kan spilles
        global play_barking
        #sjekker om kyllingens x-verdi kolliderer med hundens x-verdi
        if chick.x + chick.size >= pug.x and chick.x <= pug.x + pug.size:
            #sjekker om kyllingens y-verdi kolliderer med hundens y-verdi
            if chick.y + chick.size >= pug.y and chick.y <= pug.y + pug.size:
                #kylling blir borte dersom hunden vinner
                chick.hidden = True
                
                #stopper bakgrunnsmusikk
                pg.mixer.music.stop()
                #hvis bjeffing ikke allerede spilles (dette gjør at den bare spilles én gang og ikke oppå seg selv)
                if not play_barking:
                    #sier at bjeffe-lyden kan spilles
                    play_barking = True
                    #spiller bjeffelyd
                    barking.play()
                    
                
                #skriver vinnertekst for hunden
                surface.blit(textPug, textRectPug)
                



    #lager en metode som sjekker kollisjon mellom hunden og hønsehuset
    def collisionPugHonsehus(pug, honsehus):
        #lager et nytt rektangel rundt hunden med de skalerte x- og y-verdiene
        ny_rect = pg.Rect(pug.x + pug.vx, pug.y + pug.vy, pug.size * pug.scale, pug.size * pug.scale)
        
        #sjekker for kollisjon mellom hund og hønsehus (colliderect sjekker om rektanglene overlapper noe sted)
        if pg.Rect.colliderect(ny_rect, honsehus.rektangelRect):
            #hvis hunden treffer overnfra eller nedenfra skal fart i y-retning stoppe
            if pug.direction in ("up", "down"):
                pug.vy = 0
            #hvis hunden treffer fra siden skal fart i x-retning stoppe
            if pug.direction in ("left", "right"):
                pug.vx = 0




    #metode som sjekker kollisjon mellom lynene og karakterene
    def collisionLynChickPug(lyn, chick, pug):
        #lager et nytt rektangel rundt hunden med de skalerte x- og y-verdiene
        ny_rect = pg.Rect(pug.x + pug.vx, pug.y + pug.vy, pug.size * pug.scale, pug.size * pug.scale)
        
        #lager et nytt rektangel rundt kyllingen med de skalerte x- og y-verdiene
        ny_rect2 = pg.Rect(chick.x + chick.vx, chick.y + chick.vy, chick.size * chick.scale, chick.size * chick.scale)
        
        #sjekker om hunden kolliderer med et av lynene
        for lynet in lyn:
            if pg.Rect.colliderect(ny_rect, lynet.rektangelRect):
                #stopper wooshe-lyd om det spilles fra før av
                woosh.stop()
                #spiller wooshelyd
                woosh.play()
                
                #dersom det er kollisjon skal hundens fart øke i den retningen den beveger seg i
                if pug.direction == "up":
                    pug.vy = -10
                elif pug.direction == "down":
                    pug.vy = 10
                elif pug.direction == "left":
                    pug.vx = -10
                elif pug.direction == "right":
                    pug.vx = 10
        
            
            #sjekker om kyllingen kolliderer med et av lynene
            if pg.Rect.colliderect(ny_rect2, lynet.rektangelRect):
                #stopper wooshe-lyd om det spilles fra før av
                woosh.stop()
                #spiller wooshelyd
                woosh.play()
                #dersom det er kollisjon skal kyllingens fart øke i den retningen den beveger seg i
                if chick.direction == "up":
                    chick.vy = -10
                elif chick.direction == "down":
                    chick.vy = 10
                elif chick.direction == "left":
                    chick.vx = -10
                elif chick.direction == "right":
                    chick.vx = 10
            




    #lager en metode for kollisjon mellom høyballene og karakterene
    def collisionHoyballPugChick(hoyballer,pug,chick):
        #lager et nytt rektangel rundt hunden med de skalerte x- og y-verdiene
        ny_rect = pg.Rect(pug.x + pug.vx, pug.y + pug.vy, pug.size * pug.scale, pug.size * pug.scale)
        
        #lager et nytt rektangel rundt kyllingen med de skalerte x- og y-verdiene
        ny_rect2 = pg.Rect(chick.x + chick.vx, chick.y + chick.vy, chick.size * chick.scale, chick.size * chick.scale)
        
        
        
        #går gjennom alle høyballene
        for hoyball in hoyballer:
            #sjekker for kollisjon mellom hund og høyballene
            if pg.Rect.colliderect(ny_rect, hoyball.rektangelRect):
                #hvis hunden treffer ovenfra eller nedenfra skal fart i y-retning stoppe
                if pug.direction in ("up", "down"):
                    pug.vy = 0
                #hvis hunden treffer fra siden skal fart i x-retning stoppe
                if pug.direction in ("left", "right"):
                    pug.vx = 0
            
            #sjekker for kollisjon mellom kylling og høyballene
            if pg.Rect.colliderect(ny_rect2, hoyball.rektangelRect):
                #hvis kyllingen treffer ovenfra eller nedenfra skal fart i y-retning stoppe
                if chick.direction in ("up", "down"):
                    chick.vy = 0
                #hvis kyllingen treffer fra siden skal fart i x-retning stoppe
                if chick.direction in ("left", "right"):
                    chick.vx = 0


    #tegner høyballene
    for hoyball in hoyballer:
        hoyball.draw()

    #tegner lyn
    for lynet in lyn:
        lynet.draw()
    
    
    #sjekker kollisjon mellom kylling og hønsehus
    collisionChickHonsehus(chick, honsehus)
    #sjekker kollisjon mellom pug og kylling
    collisionPugChick(pug, chick)
    #sjekker kollisjon mellom pug og hønsehus
    collisionPugHonsehus(pug, honsehus)
    #sjekker kollisjon mellom karakterene og høyballene
    collisionHoyballPugChick(hoyballer,pug,chick)
    #sjekker kollisjon mellom lyn og karakterer
    collisionLynChickPug(lyn,chick,pug)
    
    
    #tegner hønsehus
    honsehus.draw()
    

    
    #så lenge høna ikke har tapt skal den vises og oppdateres
    if not chick.hidden:
        #oppdaterer posisjonen
        chick.update()
        #sier at kyllingen kan bevege seg så lenge hunden er med i spillet
        if not pug.hidden:
            #beveger seg
            chick.move()
        #tegner høne til skjermen
        chick.draw()
    #hvis høna vinner skal den stå stille
    if pug.hidden:
        chick.vx = 0
        chick.vy = 0
    
    
    #så lenge hunden ikke har tapt skal den vises og oppdateres
    if not pug.hidden:
        #oppdaterer posisjonen
        pug.update()
        #sier at hunden kan bevege seg så lenge kyllingen er med i spillet
        if not chick.hidden:
            #beveger seg
            pug.move()
        #tegner hunden til skjermen
        pug.draw()
    #hvis hunden vinner skal den stå stille
    if chick.hidden:
        pug.vx = 0
        pug.vy = 0



def infoScreen():
    textInfo = font.render("Trykk mellomrom for å starte", True, WHITE,BLUE)
    textInfo2 = font.render("hund: piltaster, kylling: wasd", True, WHITE, BLUE)
    textRectInfo = textInfo.get_rect()
    textRectInfo2 = textInfo2.get_rect()
    textRectInfo.center = (WIDTH // 2, HEIGHT // 2 - 40)
    textRectInfo2.center = (WIDTH // 2, HEIGHT // 2 + 40)
    
    surface.blit(textInfo, textRectInfo)
    surface.blit(textInfo2, textRectInfo2)

def endScreen():
    textEnd = font.render("Spillet er over", True, WHITE,BLUE)
    textEnd2 = font.render("Trykk space for å spille igjen, enter for å avslutte", True, WHITE, BLUE)
    textRectEnd = textEnd.get_rect()
    textRectEnd2 = textEnd2.get_rect()
    textRectEnd.center = (WIDTH // 2, HEIGHT // 2 - 40)
    textRectEnd2.center = (WIDTH // 2, HEIGHT // 2 + 40)
    
    surface.blit(textEnd, textRectEnd)
    surface.blit(textEnd2, textRectEnd2)
    


run = True
start = True
game = False
gameover = False




# Spill-løkken
while run:
    
    while start:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                start = False
                run = False 
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    game = True
                    gamemaker()
                    start = False
            
        
        # legger bakgrunnsbilde på skjermen
        surface.blit(backgroundImg, (0,0))
        
        infoScreen()
        
        pg.display.flip()
    
    while game:
        surface.blit(backgroundImg, (0,0))
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                game = False
                
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    game = False
                    gameover = True
        
        
        gameplayer()
        
        
        # Etter vi har tegner alt, "flipper" vi displayet
        pg.display.flip()
    
    while gameover:
        surface.blit(backgroundImg, (0,0))
        endScreen()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                gameover = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    game_version = randint(1,5)
                    gamemaker()
                    game = True
                    gameover = False
                    
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    gameover = False
                    run = False
        
        pg.display.flip()


# Avslutter pygame når spilløkken ikke lenger kjøres
pg.quit()
# hjelper med å avslutte spillet
# gir en melding om "process ended with exit code 0", som betyr at alt gikk som det skulle
sys.exit()





