'''
Title: maverickEngine.py
Author: Jake Zatecky
Description:
    A side-scrolling shooter game engine.
'''


import pygame, gameEngine, random

pygame.init()
pygame.mixer.init()


class Maverick(gameEngine.SuperSprite):
    '''
    Main user controlled object in game
    
    Notes:
        - controlled by user through Game class
        - has explosion sequence for when properly set
        - maverick flickers when invicible
    '''
    
    def __init__(self, scene, explodeList):
        
        gameEngine.SuperSprite.__init__(self, scene)
        
        self.loadImages()
        self.explodeList = explodeList  # received from parent
        
        # keeps track of the current animation; useful for explosion
        self.pause = 0
        self.frame = 0
        self.delay = 3      
        
        # track's user invincibility as a result of his/her death
        self.invicPause = 0
        self.invicDelay = 3
        self.invicEnd = 0  

        # initial coordinates
        self.INTIAL_X = 50
        self.INTIAL_Y = self.scene.size[1] / 2
        self.x = self.INTIAL_X
        self.y = self.INTIAL_Y
        
        # tracks the swapping of original animation and animation all together
        self.keepSwapping = True
        self.stopAnimation = False
        self.lostGame = False
        self.invic = False  # invincibility; set true for a short while after revive
        
        self.update()  # updates right away    
    
    def loadImages(self):
        ''' simply loading the one image, converting it, and setting it '''
        
        self.imgMaster = pygame.image.load("maverick(einhander).png")
        self.imgMaster = self.imgMaster.convert_alpha()
        
        # sets first image
        self.image = self.imgMaster
        self.rect = self.image.get_rect()        
        
    def update(self):
        ''' runs every frame; periodic checks '''
        
        self.pause += 1
        
        # normal, static image
        if self.pause >= self.delay and self.keepSwapping:

            if self.invic == False:
                self.image = self.imgMaster;
                self.rect = self.image.get_rect()
            # invincible
            else:
                
                self.invicPause += 1
                
                # make a visible flicker
                if self.invicPause == self.invicDelay:
                    
                    # user invincibility over
                    if self.invicEnd == 12:
                        self.invic = False
                        self.invicEnd = 0
                        self.invicPause = 0
                        
                    self.image = pygame.Surface((0, 0))
                    self.invicPause = 0
                    self.invicEnd += 1             
                else:
                    self.image = self.imgMaster;
                    self.rect = self.image.get_rect()            
            
        # explosion; at collision
        elif self.pause >= self.delay and self.stopAnimation == False:
            
            # sets maverick still
            self.setDX(0)
            self.setDY(0)
                
            # next image in frame sequence
            self.image = self.explodeList[self.frame]
            self.rect = self.image.get_rect()
            
            self.pause = 0
            self.frame += 1
            
            # done cycling through explosion
            if self.frame >= len(self.explodeList):
                # user lost game; halt object and set to nothing
                if self.lostGame:
                    self.stopAnimation = True        
                    self.image = pygame.Surface((0, 0))  # now there is no image
                # reset maverick's coordinates and start again
                else:
                    self.keepSwapping = True
                    self.invic = True
                    self.x = self.INTIAL_X
                    self.y = self.INTIAL_Y                      

        self.calcVector()
        self.calcPosition()        
        self.checkBounds()        
        
        # actual coordinates; have to do manually since overwrote update method
        self.rect.left = self.x 
        self.rect.bottom = self.y
        
class Enemy(gameEngine.SuperSprite):
    ''' 
    Main sprite to dodge; generated randomly
    
    Notes
        - each choice has different attack speed and look
        - the enemy supports explosions when contacted with a bullet
        - outOfBounds removes the sprite when no longer needed
    '''
    
    def __init__(self, scene):
        
        gameEngine.SuperSprite.__init__(self, scene)
        
        self.loadImages()
        
        self.choice = random.randrange(0, 2)  # either 0 or 1
        
        self.image = self.enemyList[self.choice]
        self.rect = self.image.get_rect()       
        
        # initial coordinates; based on image height
        self.x = self.scene.size[0] + self.rect.width
        self.y = random.randrange(self.rect.height, self.scene.size[1] - self.rect.height)
        
        self.setBoundAction(self.CONTINUE)
        self.setDX(-7)  # speed toward user
        
        self.stop = False  # halt all movement
        self.explode = False  # set explosion sequence
        self.remove = False  # remove enemy from game
        
        # different pauses for different events
        self.firePause = 0
        self.movePause = 0
        self.framePause = 0
        self.frameDelay = 3
        
        self.frame = 0  # explosion frame
        
        self.moveRate = 1  # forces a decision at the beginning for which y direction to move
        
        # fire rates and initial pause dependent upon which type; choice 1 is the stronger enemy
        if self.choice == 0:
            self.fireRate = 45
            self.pause = 35
        elif self.choice == 1:
            self.fireRate = 25
            self.pause = 20        
        else:
            print("Something went wrong...")
        
        self.update()  # updates right away
        
    def loadImages(self):
        ''' stores all the converted images in the source image for easy loading; both static image and explosions '''
        
        imgMaster = pygame.image.load("enemySheet(gregah.deviantart).png")
        imgMaster = imgMaster.convert()
        
        self.enemyList = []
        self.explodeList = []
        
        self.size = (85, 50)        
        
        offset = [(275, 300), (200, 75)]  # offsets of images to strip

        # extracts and converts images
        for i in range(2):
            
            tmpImg = pygame.Surface(self.size)
            tmpImg.blit(imgMaster, (0, 0), (offset[i], self.size))  # extracts image from master image with given offset and size
            transColor = tmpImg.get_at((1, 1))  # non-alpha transparency
            tmpImg.set_colorkey(transColor)
            
            self.enemyList.append(tmpImg)

        
    def outOfBounds(self):
        ''' merely checks if left the stage to the left; not necessary to check y coordinates'''
        
        outOfBounds = False
        
        # the object is completely off the stage (width included)
        if self.x + self.rect.width <= 0:
            outOfBounds = True
        
        return outOfBounds
    
    def update(self):
        
        self.firePause += 1
        self.movePause += 1
        
        # move object if still set to move and perform other events
        if self.stop == False:
            
            self.x += self.dx
            self.y += self.dy        
            
            self.rect.center = (self.x, self.y)        
        
            # fire a bullet (done in the Game class)
            if self.firePause > self.fireRate:
                self.firePause = 0
            
            # randomly move up, down, or stay still
            if self.movePause == self.moveRate:
                
                choice = random.randrange(0, 3)
                
                if choice == 0:
                    self.setDY(-2)
                elif choice == 1:
                    self.setDY(2)
                else:
                    self.setDY(0)
                    
                self.moveRate = random.randrange(20, 30)
        
        # can explode even when set still
        if self.explode:
            
            self.framePause += 1
            
            if self.framePause == self.frameDelay:
                
                self.framePause = 0                    
                self.image = self.explodeList[self.frame]                           
                self.frame += 1                     
                
                self.setDX(0)
                self.setDY(0)                
                
                if self.frame >= len(self.explodeList):   
                    self.image = pygame.Surface((0, 0))  # now there is no image   
                    self.remove = True
                    self.explode = False    
            
class Bullet(gameEngine.SuperSprite):
    '''
    Weapon for both user and enemy sprites
    
    Notes:
        - only difference between the two are the colors and directions
    '''
    
    def __init__(self, scene, x, y, isEnemy=False):
        
        gameEngine.SuperSprite.__init__(self, scene)
        
        self.size = (4, 4)  # adjust for tastes
        color = (0, 0, 0)  # different colors if enemy or not
        
        self.x = x
        self.y = y        
        
        if isEnemy:
            color = (255, 0, 0)
            self.setDX(-9)
        else:
            color = (0, 255, 255)
            self.setDX(8)
            
        self.imageMaster = pygame.Surface(self.size)
        radius = self.size[0] // 2
        pygame.draw.circle(self.imageMaster, color, (radius, radius), radius)  # places circle at center
        
        self.setBoundAction(self.CONTINUE)
        
        # updates right away
        self.update()
        
    def outOfBounds(self):
        ''' merely checks if left the stage to the left or right'''
        
        outOfBounds = False
        
        # the object is completely off the stage (width included)
        if self.x <= 0:
            outOfBounds = True
        elif self.x >= self.scene.size[1]:
            outOfBounds = True
        
        return outOfBounds        
        
class Game(gameEngine.Scene):
    ''' Main interface through which the user interacts '''
    
    def __init__(self, BUTTON_FG=(0,200,0), BUTTON_BG=(201,201,201)):
        
        gameEngine.Scene.__init__(self)
        self.background.fill((0, 0, 0))
        
        # color schema
        self.BUTTON_FG = BUTTON_FG
        self.BUTTON_BG = BUTTON_BG
        
        self.loadExplode()
        self.maverick = Maverick(self, self.explodeList)
        
        self.enemyList = []  # to dodge and shoot
        self.enemyBulletList = []  # to dodge
        self.deadList = []  # explosion sequence
        self.bulletList = []  # user's bullets
        
        self.lScore = gameEngine.Label(BUTTON_FG, BUTTON_BG)
        self.lScore.size = (250, 40)
        self.lScore.center = (self.size[0] / 2, 465)
        
        self.soExplode = pygame.mixer.Sound("explode.ogg")
        
        self.maverick.setBoundAction(self.maverick.CONTINUE)  # should not be needed; have just in case        
        
        self.sprites = [self.maverick, self.lScore]  # will be blit to the main surface
        
        self.delay = 4
        self.timeDelay = 15  # time before the first enemy appears
        self.difficulty = 0  # can be set through menu
        
        self.pause = 0
        self.time = 0  
        self.score = 0
        self.globalTime = 0
        self.lives = 5
        
        # end state booleans
        self.lost = False
        self.exit = False        
        
    def checkDestroy(self):
        ''' checks if user destroyed an enemy and if the enemy has fully exploded '''
        
        # user bullet collides with enemy
        for bullet in self.bulletList:
            for enemy in self.enemyList:
                
                if bullet.collidesWith(enemy):
                    
                    # higher score for better enemies
                    if enemy.choice == 0:
                        self.score += 50
                    elif enemy.choice == 1:
                        self.score += 75
                    
                    # remove bullet completly
                    self.bulletList.remove(bullet)
                    self.sprites.remove(bullet)
                    
                    # set enemy death sequence
                    enemy.explode = True
                    self.soExplode.play()                    
                    self.enemyList.remove(enemy)
                    self.deadList.append(enemy)
                    
                    # clear screen
                    self.setGroup(self.makeSpriteGroup(self.sprites))    
                    self.screen.blit(self.background, (0, 0))    
                    
        # checks if the explosion on the enemy was complete
        for enemy in self.deadList:
            
            if enemy.remove:
            
                # completely remove enemy
                self.deadList.remove(enemy)
                self.sprites.remove(enemy)
                
                # clear screen
                self.setGroup(self.makeSpriteGroup(self.sprites))    
                self.screen.blit(self.background, (0, 0))                  
                    
    def checkEnemyFire(self):
        ''' checks if enemy has fired '''
        
        for enemy in self.enemyList:
            
            if enemy.firePause == enemy.fireRate:
                
                x = enemy.rect.left
                y = enemy.rect.centery
                
                self.fireEnemy(x, y)
        
    def checkEvents(self):
        ''' looks out for some basic events as the game plays out; most disabled when the player loses '''
        
        self.pause += 1  
        self.time += 1      
        self.globalTime += 1

        self.checkLose()        
        self.checkTime()
        self.checkEnemyFire()
            
        self.checkOutOfBounds()
        self.checkDestroy()
                
    def checkLose(self):
        ''' checks all lose possibilities '''
        
        # collide with enemy; only occurs if the user did not die recently (keepSwapping)
        if self.maverick.keepSwapping and self.maverick.invic == False:
            
            # enemy collides with user
            for enemy in self.enemyList:
                
                if self.maverick.collidesWith(enemy):
                    
                    self.enemyList.remove(enemy)
                    self.sprites.remove(enemy)
                    
                    self.setGroup(self.makeSpriteGroup(self.sprites))    
                    self.screen.blit(self.background, (0, 0))                      
                    
                    self.lose()      
                    
            # enemy bullet collides with user                    
            for enemyBullet in self.enemyBulletList:
                            
                if self.maverick.collidesWith(enemyBullet):
                    
                    self.enemyBulletList.remove(enemyBullet)
                    self.sprites.remove(enemyBullet)
                    
                    self.setGroup(self.makeSpriteGroup(self.sprites))    
                    self.screen.blit(self.background, (0, 0))                      
                    
                    self.lose()                                  
                
    def checkOutOfBounds(self):
        ''' checks if enemy has left the map or user is on an edge'''
        
        for enemy in self.enemyList:
            if enemy.outOfBounds():
                self.enemyList.remove(enemy)             
                self.sprites.remove(enemy)     
                
        if self.maverick.x <= 0:
            self.maverick.x = 0
            
        if self.maverick.x >= self.size[0] - self.maverick.rect.width:
            self.maverick.x = self.size[0] - self.maverick.rect.width
            
        if self.maverick.y <= self.maverick.rect.height:
            self.maverick.y = self.maverick.rect.height
            
        if self.maverick.y >= self.size[1]:
            self.maverick.y = self.size[1]
            
    def checkTime(self):
        ''' generates a new enemy after a certain period of time '''
        
        if self.time % self.timeDelay == 0:
            self.time = 0
            self.generateEnemy()     
            
            # function used to determine the time range given the difficulty
            timeFxn = int( 37 / (self.difficulty + 1) ) 
            
            self.timeDelay = random.randrange(timeFxn - 5, timeFxn + 5)
        
        # game becomes harder as the global time
        if (self.globalTime % 250 == 0):
            self.difficulty += 0.0625
            
    def doEvents(self, event):
        ''' using event defined in scene class '''
        
        # proceeds only if the user did not lose a life recently; user movement
        if self.maverick.keepSwapping:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.maverick.setDY(-4)
                if event.key == pygame.K_s:
                    self.maverick.setDY(4)
                if event.key == pygame.K_a:
                    self.maverick.setDX(-5)
                if event.key == pygame.K_d:
                    self.maverick.setDX(5)
        
        if event.type == pygame.KEYUP:
            
            # fire a bullet
            if event.key == pygame.K_SPACE:
                if self.maverick.keepSwapping:
                    self.fire()  
                    
            # exit game session        
            if event.key == pygame.K_ESCAPE:
                self.exit = True   
                    
            # stop movement                    
            if event.key == pygame.K_w:
                self.maverick.setDY(0)
            if event.key == pygame.K_s:
                self.maverick.setDY(0)
            if event.key == pygame.K_a:
                self.maverick.setDX(0)
            if event.key == pygame.K_d:
                self.maverick.setDX(0)                
                    
    def fire(self):
        ''' fires a projectile from the maverick '''
        
        x = int(self.maverick.rect.centerx + 10)
        y = int(self.maverick.rect.centery + 10)
        
        bullet = Bullet(self, x, y)
        
        self.bulletList.append(bullet)
        self.sprites.append(bullet)
        
        self.setGroup(self.makeSpriteGroup(self.sprites))    
        self.screen.blit(self.background, (0, 0))      

    def fireEnemy(self, x, y):        
        ''' fires a projectile from the enemy '''
        
        bullet = Bullet(self, x, y, True)
        
        self.enemyBulletList.append(bullet)
        self.sprites.append(bullet)
        
        self.setGroup(self.makeSpriteGroup(self.sprites))    
        self.screen.blit(self.background, (0, 0))          
        
            
    def generateEnemy(self):
        ''' generates a new enemy ''' 
        
        enemy = Enemy(self)           
        enemy.explodeList = self.explodeList      
                    
        self.enemyList.append(enemy)
        self.sprites.append(enemy)
        
        self.setGroup(self.makeSpriteGroup(self.sprites))  # reset group on scene
        self.screen.blit(self.background, (0, 0))  # clean scene
        
    def loadExplode(self):
        ''' loads the default explosion set to be used for all objects '''
        
        self.explodeList = []
            
        imgSize = (64, 64)
        offset = []
        
        imgMaster = pygame.image.load("explosionSheet.png")
        imgMaster = imgMaster.convert_alpha()  # alpha transparency      
        
        for i in range(16):
            
            offset.append((i * 64, 128))
            tmpImg = pygame.Surface(imgSize)
            tmpImg.blit(imgMaster, (0, 0), (offset[i], imgSize))
            
            self.explodeList.append(tmpImg)        
        
    def lose(self):
        ''' makes the user lose a life '''
        
        self.soExplode.play()        
        
        self.lives -= 1
        self.lScore.text = "Lives: %d  Score: %d" % (self.lives, self.score)  
        
        # preps for the maverick explosion
        self.maverick.keepSwapping = False
        self.maverick.frame = 0
        self.maverick.pause = 0     
        
        # game over!
        if self.lives == 0:
            self.maverick.lostGame = True
            self.lost = True
            self.stopMovement()
               
    def stopMovement(self):
        ''' makes all sprites halt and prevents generation of new enemies '''
        
        # stops all moving sprites
        self.maverick.setSpeed(0)
        for enemy in self.enemyList:
            enemy.stop = True
            
        for bullet in self.bulletList:
            bullet.setSpeed(0)
            
        for bullet in self.enemyBulletList:
            bullet.setSpeed(0)
            
        # preps for the maverick explosion
        self.maverick.keepSwapping = False
        self.maverick.frame = 0
        self.maverick.pause = 0    
        
    def update(self):
        ''' checks various things; overwrites the inherited scene method '''     
        
        if self.lost == False:   
            self.lScore.text = "Lives: %d  Score: %d" % (self.lives, self.score)  
            self.checkEvents()
        # exit game session
        elif self.exit:
            self.stop()            
        
class Menu(gameEngine.Scene):
    ''' Menu user interacts with before going ahead '''
    
    def __init__(self, BUTTON_FG=(0,200,0), BUTTON_BG=(201,201,201)):
    
        gameEngine.Scene.__init__(self)
        self.background.fill((0, 0, 0))
        
        self.BUTTON_FG = BUTTON_FG
        self.BUTTON_BG = BUTTON_BG
        
        self.generateMenuItems()
        
        self.startGame = False
        self.about = False
        self.settings = False
        
        # to be passed to the game
        self.diff = 0
            
    def generateMenuItems(self):
        ''' creates menu items for user and puts them on the sprite list '''
        
        self.title = gameEngine.Label((178, 34, 34), (0, 0, 0))
        
        self.title.text = "Maverick"
        self.title.center = (self.size[0] / 2, 85)
        self.title.changeFont(35)
        self.title.size = (200, 30)
        
        self.bList = []
        sButtonText= ["Start", "Settings", "About"]
        iButtonY = [(self.size[1] / 2) - 30, self.size[1] / 2, (self.size[1] / 2) + 30]
        
        ''' generates the menu buttons with everything similar expect text and position '''
        for i in range(3):
            button = gameEngine.Button(False, self.BUTTON_FG, self.BUTTON_BG)
            button.text = sButtonText[i]
            y = iButtonY[i]
            
            button.center = (self.size[0] / 2, y)
            self.bList.append(button)
            
        # compiles sprite list 
        self.sprites = [self.title]   
        
        for button in self.bList:
            self.sprites.append(button)
            
    def reset(self):
        self.startGame = False
        self.about = False
        
    def update(self):
        
        # start game
        if self.bList[0].clicked:
            self.startGame = True
            self.stop()        
        elif self.bList[1].clicked:
            self.settings = True
            self.stop()
        elif self.bList[2].clicked:
            self.about = True
            self.stop()
        
class Settings(gameEngine.Scene):
    ''' Provides some options for the user '''
    
    def __init__(self, BUTTON_FG=(0,200,0), BUTTON_BG=(201,201,201)):
    
        gameEngine.Scene.__init__(self)
        self.background.fill((0, 0, 0))

        self.BUTTON_FG = BUTTON_FG
        self.BUTTON_BG = BUTTON_BG
        
        self.generateMenuItems()
        
    def generateMenuItems(self):
        
        self.title = gameEngine.Label((178, 34, 34) , (0, 0, 0))
        self.title.text = "Settings"
        self.title.changeFont(35)
        self.title.size = (200, 60)
        self.title.center = (self.size[0] / 2, 85)       
        
        self.lDiff = gameEngine.Label(self.BUTTON_FG, self.BUTTON_BG)
        self.lDiff.text = "Difficulty"
        self.lDiff.center = (self.size[0] / 2, (self.size[1] / 2) - (self.lDiff.size[1] / 2))
        
        self.sDiff = gameEngine.Scroller(0, 16, 1, self.BUTTON_FG, self.BUTTON_BG)
        self.sDiff.center = (self.size[0] / 2, (self.size[1] / 2) + (self.lDiff.size[1] / 2))
        
        self.back = gameEngine.Button(False, self.BUTTON_FG, self.BUTTON_BG)
        self.back.text = "Back"
        self.back.center = (self.size[0] / 2, (self.size[1] / 2) + self.sDiff.size[1] + 80)
        
        self.sprites = [self.title, self.lDiff, self.sDiff, self.back]
        
    def update(self):
        
        # the difficulty is done really in 1/16 increments
        self.diff = self.sDiff.value / 16
        
        if self.back.clicked:
            self.stop()
            

class About(gameEngine.Scene):
    ''' Tells user about the game'''
    
    def __init__(self, BUTTON_FG=(0,200,0), BUTTON_BG=(201,201,201)):
    
        gameEngine.Scene.__init__(self)
        self.background.fill((0, 0, 0))
        
        self.BUTTON_FG = BUTTON_FG
        self.BUTTON_BG = BUTTON_BG        
        
        self.generateMenuItems()
            
    def generateMenuItems(self):
        self.title = gameEngine.Label((178, 34, 34), (0, 0, 0))
        self.title.text = "About"
        self.title.center = (self.size[0] / 2, 85)
        self.title.changeFont(35)
        self.title.size = (200, 60)        
        
        self.about = gameEngine.MultiLabel(self.BUTTON_FG, self.BUTTON_BG)
        self.about.changeFont(15);  
        self.about.textLines = ["Maverick is a simple side-scroller shooter.",
                                "Use WASD to move, SPACE to fire, and ESC once dead.", "Your maverick will be invicible shortly after death.", "",
                                "Author: Jake Zatecky"]
        self.about.center = (self.size[0] / 2, self.size[1] / 2)
        self.about.size = (500, 35 * 5)
        
        self.back = gameEngine.Button(False, self.BUTTON_FG, self.BUTTON_BG)
        self.back.text = "Back"
        self.back.center = (self.size[0] / 2, (self.size[1] / 2) + self.about.size[1] + 40)
        
        self.sprites = [self.title, self.about, self.back]
        
    def update(self):
        if self.back.clicked:
            self.stop()
        
def main():
    pygame.display.set_caption("Maverick")
    
    keepGoing= True
    
    while keepGoing:
        game = Game()
        game.start()
            
        if game.exitProgram:
            keepGoing = False

if __name__ == "__main__":
    main()
                
