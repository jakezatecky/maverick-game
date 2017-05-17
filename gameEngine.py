"""
    gameEngine.py 
    high-level tools to simplify pygame programming
    for Game Programming - The L-Line
    by Andy Harris, 2006
"""

import pygame, math
pygame.init()

class BasicSprite(pygame.sprite.Sprite):
    """ use this sprite when you want to 
        direcectly control the sprite with dx and dy
        or want to extend in another direcection than DirSprite
    """
    def __init__(self, scene):
        pygame.sprite.Sprite.__init__(self)
        self.screen = scene.screen
        self.image = pygame.Surface((25, 25))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.x = 100
        self.y = 100
        self.dx = 0
        self.dy = 0

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.checkBounds()
        self.rect.left = self.x 
        self.rect.bottom = self.y
        
    def __checkBounds(self):
        scrWidth = self.screen.get_width()
        scrHeight = self.screen.get_height()
        
        if self.x + self.rect.width > scrWidth:
            self.x = 0
        if self.x < 0:
            self.x = scrWidth
        if self.y > scrHeight:
            self.y = 0
        if self.y - self.rect.height < 0:
            self.y = scrHeight

class SuperSprite(pygame.sprite.Sprite):
    """ An enhanced Sprite class
        expects a gameEngine.Scene class as its one parameter
        Use methods to change image, direction, speed
        Will automatically travel in direction and speed indicated
        Automatically rotates to point in indicated direction
        Five kinds of boundary collision
    """

    def __init__(self, scene):
        pygame.sprite.Sprite.__init__(self)
        self.scene = scene
        self.screen = scene.screen
        
        #create constants
        self.WRAP = 0
        self.BOUNCE = 1
        self.STOP = 2
        self.HIDE = 3
        self.CONTINUE = 4
        
        #create a default text image as a placeholder
        #This will usually be changed by a setImage call
        self.font = pygame.font.Font("freesansbold.ttf", 30)
        self.imageMaster = self.font.render(">sprite>", True, (0, 0,0), (0xFF, 0xFF, 0xFF))
        self.image = self.imageMaster
        self.rect = self.image.get_rect()
        
        #create properties
        #most will be changed through method calls
        self.x = 200
        self.y = 200
        self.dx = 0
        self.dy = 0
        self.direc = 0
        self.rotation = 0
        self.speed = 0
        self.maxSpeed = 10
        self.minSpeed = -3
        self.boundAction = self.WRAP
        self.pressed = False
        self.oldCenter = (100, 100)
    
    def update(self):
        self.oldCenter = self.rect.center
        self.checkEvents()
        self.rotate()
        self.calcVector()
        self.calcPosition()
        self.checkBounds()
        self.rect.left = self.x 
        self.rect.bottom = self.y
    
    def checkEvents(self):
        """ overwrite this method to add your own event code """
        pass

    def rotate(self):
        """ PRIVATE METHOD
            change visual orientation based on 
            rotation property.
            automatically called in update.
            change rotation property directly or with 
            rotateBy(), setAngle() methods
        """
        oldCenter = self.rect.center
        self.oldCenter = oldCenter
        self.image = pygame.transform.rotate(self.imageMaster, self.rotation)
        self.rect = self.image.get_rect()
        self.rect.center = oldCenter
    
    def calcVector(self):
        """ calculates dx and dy based on speed, direc
            automatically called in update() 
        """
        theta = self.direc / 180.0 * math.pi
        self.dx = math.cos(theta) * self.speed
        self.dy = math.sin(theta) * self.speed
        self.dy *= -1
    
    def calcPosition(self):
        """ calculates the sprites position adding
            dx and dy to x and y.
            automatically called in update()
        """
        self.x += self.dx
        self.y += self.dy

    def checkBounds(self):
        """ checks boundary and acts based on 
            self.BoundAction.
            WRAP: wrap around screen (default)
            BOUNCE: bounce off screen
            STOP: stop at edge of screen
            HIDE: move off stage and wait
            CONTINUE: keep going at present course and speed
            
            automatically called by update()
        """
        
        scrWidth = self.screen.get_width()
        scrHeight = self.screen.get_height()
        
        #create variables to simplify checking
        offRight = offLeft = offTop = offBottom = offScreen = False
        
        if (self.x + self.rect.width) > scrWidth:
            offRight = True
        if self.x < 0:
            offLeft = True
        if self.y > scrHeight:
            offBottom = True
        if (self.y - self.rect.height) < 0:
            offTop = True
            
        if offRight or offLeft or offTop or offBottom:
            offScreen = True
        
        if self.boundAction == self.WRAP:
            if offRight:
                self.x = 0
            if offLeft:
                self.x = scrWidth
            if offBottom:
                self.y = 0
            if offTop:
                self.y = scrHeight
        
        elif self.boundAction == self.BOUNCE:
            if offLeft or offRight:
                self.dx *= -1
            if offTop or offBottom:
                self.dy *= -1
                
            self.updateVector()
            self.rotation = self.direc
        
        elif self.boundAction == self.STOP:
            if offScreen:
                self.speed = 0
        
        elif self.boundAction == self.HIDE:
            if offScreen:
                self.speed = 0
                self.setPosition((-1000, -1000))
        
        elif self.boundAction == self.CONTINUE:
            pass
            
        else:
            # assume it's CONTINUE - keep going forever
            pass    
    
    def setSpeed(self, speed):
        """ immediately sets the objects speed to the 
            given value.
        """
        self.speed = speed

    def speedUp(self, amount):
        """ changes speed by the given amount
            Use a negative value to slow down
        """
        self.speed += amount
        if self.speed < self.minSpeed:
            self.speed = self.minSpeed
        if self.speed > self.maxSpeed:
            self.speed = self.maxSpeed
    
    def setAngle(self, direc):
        """ sets both the direcection of motion 
            and visual rotation to the given angle
            If you want to set one or the other, 
            set them direcectly. Angle measured in degrees
        """            
        self.direc = direc
        self.rotation = direc
    
    def turnBy (self, amt):
        """ turn by given number of degrees. Changes
            both motion and visual rotation. Positive is
            counter-clockwise, negative is clockwise 
        """
        self.direc += amt
        if self.direc > 360:
            self.direc = amt
        if self.direc < 0:
            self.direc = 360 - amt
        self.rotation = self.direc
    
    def rotateBy(self, amt):
        """ change visual orientation by given
            number of degrees. Does not change direcection
            of travel. 
        """
        self.rotation += amt
        if self.rotation > 360:
            self.rotation = amt
        if self.rotation < 0:
            self.rotation = 360 - amt
    
    def setImage (self, image):
        """ loads the given file name as the master image
            default setting should be facing east.  Image
            will be rotated automatically """
        self.imageMaster = pygame.image.load(image)
        self.imageMaster = self.imageMaster.convert()
    
    def setDX(self, dx):
        """ changes dx value and updates vector """
        self.dx = dx
        self.updateVector()
    
    def addDX(self, amt):
        """ adds amt to dx, updates vector """
        self.dx += amt
        self.updateVector()
        
    def setDY(self, dy):
        """ changes dy value and updates vector """
        self.dy = dy
        self.updateVector()

    def addDY(self, amt):
        """ adds amt to dy and updates vector """
        self.dy += amt
        self.updateVector()
    
    def setComponents(self, components):
        """ expects (dx, dy) for components
            change speed and angle according to dx, dy values """
            
        (self.dx, self.dy) = components
        self.updateVector()
        
    def setBoundAction (self, action):
        """ sets action for boundary.  Values are
            self.WRAP (wrap around edge - default)
            self.BOUNCE (bounce off screen changing direction)
            self.STOP (stop at edge of screen)
            self.HIDE (move off-stage and stop)
            self.CONTINUE (move on forever)
            Any other value allows the sprite to move on forever
        """
        self.boundAction = action

    def setPosition (self, position):
        """ place the sprite direcectly at the given position
            expects an (x, y) tuple
        """
        (self.x, self.y) = position
        
    def moveBy (self, vector):
        """ move the sprite by the (dx, dy) values in vector
            automatically calls checkBounds. Doesn't change 
            speed or angle settings.
        """
        (dx, dy) = vector
        self.x += dx
        self.y += dy
        print(dy)
        print(dx)
        self.__checkBounds()

    def forward(self, amt):
        """ move amt pixels in the current direcection
            of travel
        """
        
        #calculate dx dy based on current direcection
        radians = self.direc * math.pi / 180
        dx = amt * math.cos(radians)
        dy = amt * math.sin(radians) * -1
        
        self.x += dx
        self.y += dy
        
    def addForce(self, amt, angle):
        """ apply amt of thrust in angle.
            change speed and direc accordingly
            add a force straight down to simulate gravity
            in rotation direcection to simulate spacecraft thrust
            in direc direcection to accelerate forward
            at an angle for retro-rockets, etc.
        """

        #calculate dx dy based on angle
        radians = angle * math.pi / 180
        dx = amt * math.cos(radians)
        dy = amt * math.sin(radians) * -1
        
        self.dx += dx
        self.dy += dy
        self.updateVector()
        
    def updateVector(self):
        #calculate new speed and angle based on dx, dy
        #call this any time you change dx or dy
        
        self.speed = math.sqrt((self.dx * self.dx) + (self.dy * self.dy))
        
        dy = self.dy * -1
        dx = self.dx
        
        radians = math.atan2(dy, dx)
        self.direc = radians / math.pi * 180

    def setSpeedLimits(self, maxSpeed, minSpeed):
        """ determines maximum and minimum
            speeds you will allow through
            speedUp() method.  You can still
            direcectly set any speed you want
            with setSpeed() Default values:
                max: 10
                min: -3
        """
        self.maxSpeed = maxSpeed
        self.minSpeed = minSpeed

    def dataTrace(self):
        """ utility method for debugging
            print major properties
            extend to add your own properties
        """
        print("x: %d, y: %d, speed: %.2f, direc: %.f, dx: %.2f, dy: %.2f" % \
              (self.x, self.y, self.speed, self.direc, self.dx, self.dy))
            
    def mouseDown(self):
        """ boolean function. Returns True if the mouse is 
            clicked over the sprite, False otherwise
        """
        self.pressed = False
        if pygame.mouse.get_pressed() == (1, 0, 0):
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.pressed = True
        return self.pressed
    
    def clicked(self):
        """ Boolean function. Returns True only if mouse
            is pressed and released over sprite
            
        """
        released = False
        if self.pressed:
            if pygame.mouse.get_pressed() == (0, 0, 0):
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    released = True
            return released
        
    def collidesWith(self, target):
        """ boolean function. Returns True if the sprite
            is currently colliding with the target sprite,
            False otherwise
        """
        collision = False
        if self.rect.colliderect(target.rect):
            collision = True
        return collision
    
    def collidesGroup(self, target):
        """ wrapper for pygame.sprite.spritecollideany() function
            simplifies checking sprite - group collisions
            returns result of collision check (sprite from group 
            that was hit or None)
        """
        collision = pygame.sprite.spritecollideany(self, target)
        return collision
        
    def distanceTo(self, point):
        """ returns distance to any point in pixels
            can be used in circular collision detection
        """
        (pointx, pointy) = point
        dx = self.x - pointx
        dy = self.y - pointy
        
        dist = math.sqrt((dx * dx) + (dy * dy))
        return dist
    
    def direcTo(self, point):
        """ returns direcection (in degrees) to 
            a point """
        
        (pointx, pointy) = point
        dx = self.x - pointx
        dy = self.y - pointy
        dy *= -1
        
        radians = math.atan2(dy, dx)
        direc = radians * 180 / math.pi
        direc += 180
        return direc
    
    def drawTrace(self, color=(0x00, 0x00, 0x00)):
        """ traces a line between previous position
            and current position of object 
        """
        pygame.draw.line(self.scene.background, color, self.oldCenter,
                         self.rect.center, 3)
        self.screen.blit(self.scene.background, (0, 0))
    
class Scene(object):
    """ encapsulates the IDEA / ALTER framework
        properties:
        sprites - a list of sprite objects
            that forms the primary sprite group
        background - the background surface
        screen - the display screen
        
        it's generally best to add all sprites 
        as attributes, so they can have access
        to each other if needed   
        
        --- custom game scence --- 
    """
    
    def __init__(self):
        """ initialize the game engine
            set up a sample sprite for testing
        """
        pygame.init()
        
        self.size = (640, 480)
        
        self.screen = pygame.display.set_mode(self.size)
        
        
        self.screen
        self.background = pygame.Surface(self.screen.get_size())
        self.background.fill((0, 0, 0))
        
        self.sampleSprite = SuperSprite(self)
        self.sampleSprite.setSpeed(3)
        self.sampleSprite.setAngle(0)
        self.sampleSprite.boundAction = self.sampleSprite.WRAP
        self.sprites = [self.sampleSprite]
        self.groups = []
    
        self.exitProgram = False
    
    def start(self):
        """ sets up the sprite groups
            begins the main loop
        """
        self.mainSprites = pygame.sprite.OrderedUpdates(self.sprites)
        self.groups.append(self.mainSprites)
        
        self.screen.blit(self.background, (0, 0))
        self.clock = pygame.time.Clock()
        self.keepGoing = True
        while self.keepGoing:
            self.__mainLoop()

    def stop(self):
        """stops the loop"""
        self.keepGoing = False
    
    def __mainLoop(self):
        """ manage all the main events 
            automatically called by start
        """
        self.clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.keepGoing = False
                self.exitProgram = True
            self.doEvents(event)
        
        self.update()
        for group in self.groups:
            group.clear(self.screen, self.background)
            group.update()
            group.draw(self.screen)
        
        pygame.display.flip()

    def makeSpriteGroup(self, sprites):
        """ create a group called groupName
            containing all the sprites in the sprites 
            list.  This group will be added after the 
            sprites group, and will automatically
            clear, update, and draw
        """
        tempGroup = pygame.sprite.OrderedUpdates(sprites)
        return tempGroup
    
    def addGroup(self, group):
        """ adds a sprite group to the groups list for
            automatic processing 
        """
        self.groups.append(group)
        
    def setGroup(self, group):
        
        self.groups = [group]

    def doEvents(self, event):
        """ overwrite this method to add your own events.
            Works like normal event handling, passes event
            object
        """
        pass
        
    def update(self):
        """ happens once per frame, after event parsing.
            Overwrite to add your own code, esp event handling
            that doesn't require event obj. (pygame.key.get_pressed, 
            pygame.mouse.get_pos, etc)
            Also a great place for collision detection
        """
        
            
    def setCaption(self, title):
        """ set's the scene's title text """
        pygame.display.set_caption(title)

class Label(pygame.sprite.Sprite):
    """ a basic label 
        properties: 
            font: font to use
            text: text to display
            fgColor: foreground color
            bgColor: background color
            center: position of label's center
            size: (width, height) of label
            fontSize: size of font
            
        Modifications: 
            - fontSize, changeFont, fgColor, bgColor
            - centered font in y position
            
    """
    
    def __init__(self, fgColor=((0x00, 0x00, 0x00)), 
                 bgColor=((0xFF, 0xFF, 0xFF)), fontName="freesansbold.ttf"):
        
        pygame.sprite.Sprite.__init__(self)
        self.text = ""
        self.fgColor = fgColor
        self.bgColor = bgColor
        self.center = (100, 100)
        
        self.fontSize = 20
        self.size = (150, 30)
        
        self.font = pygame.font.Font(fontName, self.fontSize)      
        
    def changeFont(self, fontSize=20, fontName="freesansbold.ttf"):
        ''' changes the font to suit a different purpose '''
        self.fontSize = fontSize
        self.font = pygame.font.Font(fontName, fontSize)

    def update(self):
        self.image = pygame.Surface(self.size)
        self.image.fill(self.bgColor)
        fontSurface = self.font.render(self.text, True, self.fgColor, self.bgColor)
        
        # center the text inside the image
        xPos = (self.image.get_width() - fontSurface.get_width()) / 2
        yPos = (self.image.get_height() - fontSurface.get_height()) / 2
        
        self.image.blit(fontSurface, (xPos, yPos))
        self.rect = self.image.get_rect()
        self.rect.center = self.center

class Button(Label):
    """ a button based on the label 
        same properties as label +
        active: True if user is clicking on sprite
                False if user is not currently clicking
        clicked: True when user releases mouse over a 
                 currently active button
                 
        Modifications:
            - update method changed to emulate traditional button and scroller behavior
    """

    def __init__(self, scroller=False, fgColor=(0, 0, 0), bgColor=(0xCC, 0xCC, 0xCC)):
        Label.__init__(self, fgColor, bgColor)
        self.active = False
        self.clicked = False
        self.mouseDown = False
        self.allowActive = True
        
        self.scroller = scroller
        self.fgColor = fgColor
        self.bgColor = bgColor
        self.BUTTON_BG = bgColor  # reverts to this when pressed on
    
    def update(self):
        ''' extensive modifications '''
        
        ''' make this area more organized:
            have booleans hover, and the such to make this less ad hoc and nicer beginning
        '''
        
        Label.update(self)
        
        self.clicked = False
        
        # hover look when over a button
        if pygame.mouse.get_pressed() == (0, 0, 0) and self.scroller == False:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.bgColor = (105, 105, 105)
            else:
                self.bgColor = self.BUTTON_BG  # revert back
        # simple boolean for code simplification
        elif pygame.mouse.get_pressed() == (1, 0, 0):
            self.mouseDown = True
        
        if self.mouseDown and self.allowActive:
            # set active if the mouse is over the button, down,
            # and with active detection allowed
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.active = True
                
                # this occurs only for regular buttons; gives 'pressed' appearance
                if self.scroller == False:
                    self.bgColor = (50, 50, 50)
                
            self.allowActive = False  # no longer allowed to set active (regardless of whether hit or not)
        
        # only for the scroller to make it more usual:
        # stops active the moment the mouse is no longer on the scroller (unlike regular butons)
        if self.mouseDown and self.scroller:
            if self.rect.collidepoint(pygame.mouse.get_pos()) == False:
                self.active = False
            
        # once released will allow the user to set the button active again    
        if pygame.mouse.get_pressed() == (0, 0, 0):
            
            self.allowActive = True
            self.mouseDown = False

            # special execution when mouse release and the button is active
            if self.active == True:
                self.active = False
                self.bgColor = self.BUTTON_BG  # revert background
                
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    self.clicked = True  # execute

class Scroller(Button):
    """ like a button, but has a numeric value that 
        can be decremented by clicking on left half
        and incremented by clicking on right half.
        new atributes:
            value: the scroller's numeric value
            minValue: minimum value
            maxValue: maximum value
            increment: How much is added or subtracted
            format: format of string interpolation
            
            Modifications:
                - allowed constructor to set min, max, and inc values
                - gives more of a delay for the values such that the user has
                  finer control
    """
    
    def __init__(self, iMin=0, iMax=10, iInc=1, fgColor=(0, 0, 0), bgColor=(0xCC, 0xCC, 0xCC)):
        Button.__init__(self, True, fgColor, bgColor)
        self.minValue = iMin
        self.maxValue = iMax
        self.increment = iInc
        self.value = 5
        self.format = "<<  %.2f  >>"
        
        self.pause = 0
        self.delay = 3
        
    def update(self):
        
        Button.update(self)
        
        self.pause += 1
        
        if self.pause == self.delay:
            self.pause = 0
        
            if self.active:
                mousePos = pygame.mouse.get_pos()
                
                if mousePos[0] < self.rect.centerx:
                    self.value -= self.increment
                    if self.value < self.minValue:
                        self.value = self.minValue
                else:
                    self.value += self.increment
                    if self.value > self.maxValue:
                        self.value = self.maxValue

        self.text = self.format % self.value

class MultiLabel(pygame.sprite.Sprite):
    """ accepts a list of strings, creates a multi-line
        label to display text 
        same properties as label except textLines
        is a list of strings. There is no text
        property.
        Set the size manually. Vertical size should be at 
        least 30 pixels per line (with the default font)
        
        Modifications: 
            - the vertical length of each line
            - changeFont
            - BUTTON_FG, BUTTON_BG
    """
    
    def __init__(self, BUTTON_FG=((0x00, 0x00, 0x00)), BUTTON_BG=((0xFF, 0xFF, 0xFF))):
        pygame.sprite.Sprite.__init__(self)
        self.textLines = ["This", "is", "sample", "text"]
        self.font = pygame.font.Font("freesansbold.ttf", 20)
        self.fgColor = BUTTON_FG
        self.bgColor = BUTTON_BG
        self.center = (100, 100)
        self.size = (400, 300)
        
    def changeFont(self, fontSize=20, fontName="freesansbold.ttf"):
        ''' changes the font to suit a different purpose '''
        self.fontSize = fontSize
        self.font = pygame.font.Font(fontName, fontSize)        
        
    def update(self):
        self.image = pygame.Surface(self.size)
        self.image.fill(self.bgColor)
        numLines = len(self.textLines)
        vSize = 35
        
        for lineNum in range(numLines):
            currentLine = self.textLines[lineNum]
            fontSurface = self.font.render(currentLine, True, self.fgColor, self.bgColor)
            # center the text
            xPos = (self.image.get_width() - fontSurface.get_width())/2
            yPos = (lineNum * vSize) + 5
            self.image.blit(fontSurface, (xPos, yPos))
        
        self.rect = self.image.get_rect()
        self.rect.center = self.center

if __name__ == "__main__":
    # change this code to test various features of the engine
    # This code will not run when gameEngine is run as a module
    # (as it usually will be)
        
    game = Scene()
    thing = SuperSprite(game)
    thing.setSpeed(5)
    thing.setBoundAction(thing.BOUNCE)
    thing.setAngle(230)
    game.sprites = [thing]
    
    game.start()
