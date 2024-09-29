

import os

import pygame
import random
from pygame import *
import neat
import pickle
import graphviz
import numpy as np
pygame.mixer.pre_init(44100, -16, 2, 2048) # fix audio delay 
pygame.init()

scr_size = (width,height) = (600,150)
FPS = 60
gravity = 0.6

black = (0,0,0)
white = (255,255,255)
background_col = (235,235,235)

high_score = 0

screen = pygame.display.set_mode(scr_size)
clock = pygame.time.Clock()
pygame.display.set_caption("T-Rex Rush")


def load_image(
    name,
    sizex=-1,
    sizey=-1,
    colorkey=None,
    ):

    fullname = os.path.join('sprites', name)
    image = pygame.image.load(fullname)
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    if sizex != -1 or sizey != -1:
        image = pygame.transform.scale(image, (sizex, sizey))

    return (image, image.get_rect())

def load_sprite_sheet(
        sheetname,
        nx,
        ny,
        scalex = -1,
        scaley = -1,
        colorkey = None,
        ):
    fullname = os.path.join('sprites',sheetname)
    sheet = pygame.image.load(fullname)
    sheet = sheet.convert()

    sheet_rect = sheet.get_rect()

    sprites = []

    sizex = sheet_rect.width/nx
    sizey = sheet_rect.height/ny

    for i in range(0,ny):
        for j in range(0,nx):
            rect = pygame.Rect((j*sizex,i*sizey,sizex,sizey))
            image = pygame.Surface(rect.size)
            image = image.convert()
            image.blit(sheet,(0,0),rect)

            if colorkey is not None:
                if colorkey == -1:
                    colorkey = image.get_at((0,0))
                image.set_colorkey(colorkey,RLEACCEL)

            if scalex != -1 or scaley != -1:
                image = pygame.transform.scale(image,(scalex,scaley))

            sprites.append(image)

    sprite_rect = sprites[0].get_rect()

    return sprites,sprite_rect

def disp_gameOver_msg(retbutton_image,gameover_image):
    retbutton_rect = retbutton_image.get_rect()
    retbutton_rect.centerx = width / 2
    retbutton_rect.top = height*0.52

    gameover_rect = gameover_image.get_rect()
    gameover_rect.centerx = width / 2
    gameover_rect.centery = height*0.35

    screen.blit(retbutton_image, retbutton_rect)
    screen.blit(gameover_image, gameover_rect)

def extractDigits(number):
    if number > -1:
        digits = []
        i = 0
        while(number/10 != 0):
            digits.append(number%10)
            number = int(number/10)

        digits.append(number%10)
        for i in range(len(digits),5):
            digits.append(0)
        digits.reverse()
        return digits

class Dino():
    def __init__(self,sizex=-1,sizey=-1):
        self.images,self.rect = load_sprite_sheet('dino.png',5,1,sizex,sizey,-1)
        self.images1,self.rect1 = load_sprite_sheet('dino_ducking.png',2,1,59,sizey,-1)
        self.rect.bottom = int(0.98*height)
        self.rect.left = width/15
        self.image = self.images[0]
        self.index = 0
        self.counter = 0
        self.score = 0
        self.isJumping = False
        self.isDead = False
        self.isDucking = False
        self.isBlinking = False
        self.movement = [0,0]
        self.jumpSpeed = 11.5

        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width

    def draw(self):
        screen.blit(self.image,self.rect)
        
    def checkbounds(self):
        if self.rect.bottom > int(0.98*height):
            self.rect.bottom = int(0.98*height)
            self.isJumping = False

    def get_data(self):
        if self.isJumping:
            return 0
        elif self.isDucking:
            return 1
        else:
            
            return 2
    

    def update(self):
        if self.isJumping:
            self.movement[1] = self.movement[1] + gravity

        if self.isJumping:
            self.index = 0
        elif self.isBlinking:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1)%2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1)%2

        elif self.isDucking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2 + 2

        if self.isDead:
           self.index = 4

        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.images1[(self.index)%2]
            self.rect.width = self.duck_pos_width
            

        self.rect = self.rect.move(self.movement)
        self.checkbounds()

        if not self.isDead and self.counter % 7 == 6 and self.isBlinking == False:
            self.score += 1
            

        self.counter = (self.counter + 1)

class Cactus(pygame.sprite.Sprite):
    def __init__(self, speed=5, sizex=-1, sizey=-1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images, self.rect = load_sprite_sheet('cacti-small.png', 3, 1, sizex, sizey, -1)
        self.rect.bottom = int(0.98 * height)
        self.rect.left = width + self.rect.width
        self.image = self.images[random.randrange(0, 3)]
        self.movement = [-1 * speed, 0]
        
    def draw(self):
        # Dibuja el cactus
        screen.blit(self.image, self.rect)
        
        # Dibuja la hitbox del cactus (contorno del rectángulo)
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)
        
        # Mostrar las dimensiones en la pantalla
        font = pygame.font.Font(None, 24)
        dimensions_text = f'{self.rect.width}x{self.rect.height}'
        text_surface = font.render(dimensions_text, True, (0, 255, 0))
        screen.blit(text_surface, (self.rect.left, self.rect.top - 20))

    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()

class Ptera(pygame.sprite.Sprite):
    def __init__(self,speed=5,sizex=-1,sizey=-1):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.images,self.rect = load_sprite_sheet('ptera.png',2,1,sizex,sizey,-1)
        self.ptera_height = [height*0.82,height*0.75,height*0.60]
        self.rect.centery = self.ptera_height[int(random.randrange(0,3))]
        self.rect.left = width + self.rect.width
        
        self.image = self.images[0]
        self.movement = [-1*speed,0]
        self.index = 0
        self.counter = 0

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self):
        if self.counter % 10 == 0:
            self.index = (self.index+1)%2
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.counter = (self.counter + 1)
        if self.rect.right < 0:
            self.kill()


class Ground():
    def __init__(self,speed=-5):
        self.image,self.rect = load_image('ground.png',-1,-1,-1)
        self.image1,self.rect1 = load_image('ground.png',-1,-1,-1)
        self.rect.bottom = height
        self.rect1.bottom = height
        self.rect1.left = self.rect.right
        self.speed = speed

    def draw(self):
        screen.blit(self.image,self.rect)
        screen.blit(self.image1,self.rect1)

    def update(self):
        self.rect.left += self.speed
        self.rect1.left += self.speed

        if self.rect.right < 0:
            self.rect.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect.right



class Scoreboard():
    def __init__(self,x=-1,y=-1):
        self.score = 0
        self.tempimages,self.temprect = load_sprite_sheet('numbers.png',12,1,11,int(11*6/5),-1)
        self.image = pygame.Surface((55,int(11*6/5)))
        self.rect = self.image.get_rect()
        if x == -1:
            self.rect.left = width*0.89
        else:
            self.rect.left = x
        if y == -1:
            self.rect.top = height*0.1
        else:
            self.rect.top = y

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self,score):
        score_digits = extractDigits(score)
        self.image.fill(background_col)
        for s in score_digits:
            self.image.blit(self.tempimages[s],self.temprect)
            self.temprect.left += self.temprect.width
        self.temprect.left = 0

class DinoCounter:
    def __init__(self, x=-1, y=-1):
        self.dino_count = 0
        # Cargar los sprites de los números
        self.tempimages, self.temprect = load_sprite_sheet('numbers.png', 12, 1, 11, int(11 * 6 / 5), -1)
        self.image = pygame.Surface((55, int(11 * 6 / 5)))
        self.rect = self.image.get_rect()

        # Posicionar el contador en la pantalla
        if x == -1:
            self.rect.left = width * 0.75
        else:
            self.rect.left = x

        if y == -1:
            self.rect.top = height * 0.1
        else:
            self.rect.top = y

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self, dino_count):
        self.dino_count = dino_count
        self.image.fill(background_col)
        
        # Convertir el número de dinosaurios vivos en dígitos
        digits = extractDigits(self.dino_count)

        # Dibujar los números correspondientes
        for digit in digits:
            self.image.blit(self.tempimages[digit], self.temprect)
            self.temprect.left += self.temprect.width

        # Reiniciar la posición de temprect para la próxima actualización
        self.temprect.left = 0

def introscreen():

    temp_dino = Dino(44,47)
    temp_dino.isBlinking = True
    gameStart = False

    callout,callout_rect = load_image('call_out.png',196,45,-1)
    callout_rect.left = width*0.05
    callout_rect.top = height*0.4

    temp_ground,temp_ground_rect = load_sprite_sheet('ground.png',15,1,-1,-1,-1)
    temp_ground_rect.left = width/20
    temp_ground_rect.bottom = height

    logo,logo_rect = load_image('logo.png',240,40,-1)
    logo_rect.centerx = width*0.6
    logo_rect.centery = height*0.6
    while not gameStart:
        if pygame.display.get_surface() == None:
            print("Couldn't load display surface")
            return True
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        temp_dino.isJumping = True
                        temp_dino.isBlinking = False
                        

        temp_dino.update()

        if pygame.display.get_surface() != None:
            screen.fill(background_col)
            screen.blit(temp_ground[0],temp_ground_rect)
            if temp_dino.isBlinking:
                screen.blit(logo,logo_rect)
                screen.blit(callout,callout_rect)
            temp_dino.draw()

            pygame.display.update()

        clock.tick(FPS)
        if temp_dino.isJumping == False and temp_dino.isBlinking == False:
            gameStart = True

def is_far_enough(new_obstacle_rect, obstacles, min_distance=200):
    for obstacle in obstacles:
        # Calcula la distancia horizontal entre el nuevo objeto y el existente
        
        
        if abs(new_obstacle_rect.left - obstacle.rect.right) < min_distance:
            return False
        
    return True


def gameplay(genomes,config):
    
        global high_score
        gamespeed = 4
        #max_gamespeed=40
        gameOver = False
        
        nets=[]
        dinos=[]
        for id,g in genomes:
            net=neat.nn.FeedForwardNetwork.create(g,config)
            nets.append(net)
            g.fitness=0
            dinos.append(Dino(44,47))
        
        
        new_ground = Ground(-1*gamespeed)
        scb = Scoreboard()
        dino_counter = DinoCounter()
        highsc = Scoreboard(width*0.78)
        counter = 0

        cacti = pygame.sprite.Group()
        pteras = pygame.sprite.Group()
        last_obstacle = pygame.sprite.Group()

        Cactus.containers = cacti
        Ptera.containers = pteras
        


        temp_images,temp_rect = load_sprite_sheet('numbers.png',12,1,11,int(11*6/5),-1)
        HI_image = pygame.Surface((22,int(11*6/5)))
        HI_rect = HI_image.get_rect()
        #HI_image.fill(background_col)
        HI_image.blit(temp_images[10],temp_rect)
        temp_rect.left += temp_rect.width
        HI_image.blit(temp_images[11],temp_rect)
        HI_rect.top = height*0.1
        HI_rect.left = width*0.73
       
        
            
        while not gameOver:
                crear=True
                if pygame.display.get_surface() == None:
                    print("Couldn't load display surface")
                    
                    gameOver = True
                else:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            
                            gameOver = True

                        
                for dino in dinos:

                    for c in cacti:
                        c.movement[0] = -1*gamespeed
                        if pygame.sprite.collide_mask(dino,c):
                            dino.isDead = True
                            

                    for p in pteras:
                        p.movement[0] = -1*gamespeed
                        if pygame.sprite.collide_mask(dino,p):
                            dino.isDead = True
                for obstacle in last_obstacle:
                    
                    # Si el borde derecho del obstáculo está a la izquierda del borde izquierdo del dinosaurio
                    if obstacle.rect.right < dino.rect.left:
                        obstacle.kill()  # Elimina el obstáculo del grupo y de la pantalla
                    
                if len(cacti) < 2:
                        if len(cacti) == 0 and len(pteras)==0:
                        # Crea un nuevo cactus
                            new_cactus = Cactus(gamespeed, 40, 40)
                            # Verifica si el cactus está lo suficientemente lejos de otros obstáculos
                            if is_far_enough(new_cactus.rect, last_obstacle):
                                last_obstacle.add(new_cactus)
                            else:
                                new_cactus.kill()
                        else:
                            for l in last_obstacle:
                                if l.rect.right < width * 0.7 and random.randrange(0, 50) == 10:
                                    new_cactus = Cactus(gamespeed, 40, 40)
                                    if is_far_enough(new_cactus.rect, last_obstacle):
                                        last_obstacle.add(new_cactus)
                                    else:
                                        new_cactus.kill()
                                break
                if len(pteras) == 0 and random.randrange(0, 200) == 10 and counter > 500 :
                        for l in last_obstacle:
                            if l.rect.right < width * 0.8:
                                new_ptera = Ptera(gamespeed, 46, 40)
                                if is_far_enough(new_ptera.rect, last_obstacle):
                                    last_obstacle.add(new_ptera)
                                    
                                else:
                                    new_ptera.kill()
                                    
                            break



                
                for index,dino in enumerate(dinos):
                    closest_obstacle = None
                    min_distance = float('inf')  # Inicializa con un valor muy grande
                    width_obstacle=1
                    height_obstacle=1
                    px=1
                    py=1
                    for obstacle in last_obstacle:
                        # Calcula la distancia horizontal entre el Dino y el obstáculo
                        distance = obstacle.rect.left - dino.rect.right
            
                        # Asegúrate de que el obstáculo esté delante del Dino
                        if distance > 0 and distance < min_distance:
                            min_distance = distance
                            closest_obstacle = obstacle
                        
                        break
   
                    if closest_obstacle:
                        width_obstacle = closest_obstacle.rect.width
                        height_obstacle= closest_obstacle.rect.height
                        
                        px=closest_obstacle.rect.x
                        py=closest_obstacle.rect.y

                    datos_originales=np.array([
                        dino.get_data(),min_distance,gamespeed,
                        py,px,width_obstacle,height_obstacle
                        ])
                    
                    datos_normalizados = (datos_originales - np.min(datos_originales)) /(np.max(datos_originales) - np.min(datos_originales))
                    output=nets[index].activate(datos_normalizados)
                    i=output.index(max(output))
                   
                    if i==0:
                       
                       dino.isDucking=False
                    elif i==1  :
                        if dino.rect.bottom == int(0.98*height):
                                dino.isJumping = True
                                dino.isDucking=False
                                dino.movement[1] = -1*dino.jumpSpeed
                    else:
                        dino.isDucking=True
                        dino.movement[1] = 1*dino.jumpSpeed
                        
                    
            
                remain_dinos=0
                for i , dino in enumerate(dinos):
                    if not dino.isDead:
                        remain_dinos+=1
                        dino.update()
                        scb.update(dino.score)
                        genomes[i][1].fitness+=dino.score
                        
                        
                
                cacti.update()
                pteras.update()
                dino_counter.update(remain_dinos)
                new_ground.update()
                
                highsc.update(high_score)

                if pygame.display.get_surface() != None:
                    screen.fill(background_col)
                    new_ground.draw()
                    dino_counter.draw()
                    scb.draw()
                    
                    
                    if high_score != 0:
                        highsc.draw()
                        screen.blit(HI_image,HI_rect)
                    cacti.draw(screen)
                    pteras.draw(screen)
                    
                    for cactus in cacti:
                        cactus.draw()
                    for dino in dinos:
                        if  not dino.isDead:
                            
                            dino.draw()
                            
                    pygame.display.update()
                clock.tick(FPS)

                if remain_dinos==0:
                    gameOver = True
                    #if dinos[-1].score > high_score:
                        #high_score =dinos[-1].score
                
                if counter%700 == 699:
                    new_ground.speed -= .1
                    gamespeed += .1
                
                counter = (counter + 1)
                
                pygame.display.flip()
                # Recorre todos los obstáculos en el grupo last_obstacle
                
def main():
        global p
        config_path="config-feedforward.txt"
        config=neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path)
        p=neat.Population(config)
        p.add_reporter(neat.StdOutReporter(True))
        stats=neat.StatisticsReporter()
        p.add_reporter(stats)
        winner=p.run(gameplay,1000)
        # 'winner' es el genoma con mejor aptitud
        print(f'Mejor genoma:\n{winner}')
        with open('best_genome.pkl', 'wb') as f:
            pickle.dump(winner, f)
main()
