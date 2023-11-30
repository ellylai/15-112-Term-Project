from cmu_graphics import *
import math
import random
from PIL import Image

class Game:
    def __init__(self):
        self.states = {'start', 'instructions', 'hangar', 'game', 'game over', 'win'}
        self.currState = 'start'
    
    def switchState(self, other):
        if other in self.states:
            self.currState = other

class Fleet:
    def __init__(self):
        imageList = [['X-Wing.png', 50, 50], 
             ['Falcon.png', 40, 50], 
             ['Red.png', 35, 50], 
             ['Yellow.png', 35, 60], 
             ['TIE.png', 50, 40]]
        self.fleet = [Ship(ship) for ship in imageList]

class Ship:
    def __init__(self, ship):
        self.image = Image.open(ship[0])
        self.w = ship[1]
        self.h = ship[2]

class Buttons:
    def __init__(self, app):
        self.buttonLabels = {0: 'Start! (Random Mode)', 1: 'Mode 1', 2: 'Mode 2', 
                             3: 'Mode 3', 4: 'Instructions'}
        self.buttonCoords = []
    
        for i in range(5):
            topX, topY = 100, (i+1)*(app.height/8)
            self.buttonCoords.append((topX, topY))
    
    def drawButtons(self):
        for i in range(5):
            drawRect(self.buttonCoords[i][0], self.buttonCoords[i][1], 400, 100, 
                     fill=None, border='black')
            drawLabel(self.buttonLabels[i], self.buttonCoords[i][0]+200, 
                      self.buttonCoords[i][1]+50, bold=True, align='center')
    
    def returnMode(self, app, mouseX, mouseY):
        for button in self.buttonCoords:
            index = self.buttonCoords.index(button) 
            if ((button[0] <= mouseX <= button[0]+400) and 
            (button[1] <= mouseY <= button[1]+100)):
                if index == 0: #get random mode
                    app.gamemode = random.randint(1, 3)
                    app.gameState = 'hangar'
                elif index in range(1, 4):
                    app.gamemode = index
                    app.gameState = 'hangar'
                elif index == 4: #draw instructions
                    app.gameState = 'instructions'

class Buttons2:
    def __init__(self, app):
        self.buttonLabels = ['X-Wing', 'Falcon', 'Red Ship', 'Yellow Ship']
        self.buttonCoords = []
        for i in range(4):
            topX, topY = 100, (i+1)*(app.height/7)
            self.buttonCoords.append((topX, topY))
    
    def drawButtons(self, app):
        for i in range(4):
            drawRect(self.buttonCoords[i][0], self.buttonCoords[i][1], 400, 100, 
                    fill=None, border='black')
            drawLabel(self.buttonLabels[i], self.buttonCoords[i][0]+200, 
                    self.buttonCoords[i][1]+50, bold=True, align='center')
            drawImage(CMUImage(app.shipImages.fleet[i].image), 400, self.buttonCoords[i][1]+50, 
                    width=app.shipImages.fleet[i].w, height=app.shipImages.fleet[i].h, 
                    align='center')
    
    def getShip(self, app, mouseX, mouseY):
        for button in self.buttonCoords:
            index = self.buttonCoords.index(button) 
            if ((button[0] <= mouseX <= button[0]+400) and 
            (button[1] <= mouseY <= button[1]+100)):
                app.playerShip.image = index
                app.gameState = 'game'

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = None
        self.rotate = 0
        self.moveSpeed = 5
        self.bullets = []
        self.bulletSpeed = 5
        self.hits = 0
        self.kills = 0
        self.dead = False
    
    def onKeyHold(self, app, keys):
        if 'w' in keys and self.y > 0:
            self.y -= self.moveSpeed
        if 'a' in keys and self.x > 0:
            self.x -= self.moveSpeed
        if 's' in keys and self.y < app.height:
            self.y += self.moveSpeed
        if 'd' in keys and self.x < app.width:
            self.x += self.moveSpeed

    def onMouseMove(self, app, mouseX, mouseY):
        self.rotationAngle(mouseX, mouseY)

    def addBullets(self, app):
        if app.onStepCounter%5==0 and not self.dead:
            self.bullets.append([self.x-7, self.y])
            self.bullets.append([self.x+7, self.y])
    
    def moveBullets(self): #need to adjust bullet direction
        #self.bullet speed update
        if not self.dead:
            for bullet in self.bullets:
                #bullet[0] += math.sin(self.rotate)*5
                bullet[1] -= self.bulletSpeed
    
    def drawPlayer(self, app):
        if not self.dead and self.image != None:
            imageW = app.shipImages.fleet[self.image].w
            imageH = app.shipImages.fleet[self.image].h
            shipImage = app.shipImages.fleet[self.image].image
            drawImage(CMUImage(shipImage), self.x, self.y, width=imageW, height=imageH, align='center', rotateAngle=self.rotate)
    
    def drawBullets(self, app):
        if not self.dead:
            for bullet in self.bullets:
                if onScreen(app, bullet[0], bullet[1]):
                    drawOval(bullet[0], bullet[1], 3, 6, fill='blue')
    
    def collision(self, app): # treating ship with a circular 'hitpoint' with r=8
        for enemy in app.enemyShips.enemies:
            for bullet in enemy.bullets:
                if distance(bullet.x, bullet.y, self.x, self.y) <= 8:
                    self.hits += 1
                    enemy.bullets.remove(bullet)
                    return True
        if self.hits >= 10:
            self.dead = True
    
    def rotationAngle(self, mouseX, mouseY):
        y = mouseY-self.y
        x = mouseX-self.x
        if x==0:
            self.rotate = 0
        elif x!=0:
            self.rotate = math.degrees(math.atan2(y, x)+math.pi/2)
        
class Enemy:
    def __init__(self, app, x, y):
        self.x, self.y = x, y
        self.moveRight = True
        self.bullets = []
        self.rotate = 0
        self.health = 5
        self.hits = 0
        self.dead = False

    def move(self, app):
        if self.moveRight == True:
            self.x += 1
            if self.x >= 600: self.moveRight = False
        if self.moveRight == False:
            self.x -= 1
            if self.x <= 0: self.moveRight = True
        if self.y < app.height/5:
            self.y += 2
    
    def addBullets(self):
        self.bullets.append(Bullet(self.x-7, self.y))
        self.bullets.append(Bullet(self.x+7, self.y))
    
    def drawBullets(self, app):
        for bullet in self.bullets:
            if onScreen(app, bullet.x, bullet.y):
                drawOval(bullet.x, bullet.y, 3, 6, fill='orange', rotateAngle=bullet.rotate)
    
    def onStep(self, app): 
        if app.gamemode == 1:
            for bullet in self.bullets:
                bullet.update1()
        if app.gamemode == 2:
            for bullet in self.bullets:
                bullet.update2(app)
        if app.gamemode == 3:
            for bullet in self.bullets:
                bullet.update3(app)

        if app.onStepCounter%15 == 0 and not self.dead:
            self.addBullets()  
        self.move(app)
        self.rotationAngle(app)

    def collision(self, app):
        for bullet in app.playerShip.bullets:
            if distance(bullet[0], bullet[1], self.x, self.y) <= 8:
                self.hits += 1
                app.playerShip.bullets.remove(bullet)
                return True
        if self.hits >= self.health:
            self.dead = True
    
    def rotationAngle(self, app):
        y = app.playerShip.y-self.y
        x = app.playerShip.x-self.x
        if x==0:
            self.rotate = 0
        elif x!=0:
            self.rotate = math.degrees(math.atan2(y, x)-math.pi/2)

class Enemies:
    def __init__(self, app):
        self.enemies = []
    
    def addEnemy(self, app, enemyX, enemyY):
        if app.gamemode==1:
            enemyAddStep = 150
        if app.gamemode==2:
            enemyAddStep = 120
        if app.gamemode==3:
            enemyAddStep = 200
        if app.onStepCounter%enemyAddStep==0:
            self.enemies.append(Enemy(app, enemyX, enemyY))
    
    def drawEnemy(self, app):
        for enemy in self.enemies:
            # x1, y1 = enemy.x, enemy.y+12
            # x2, y2 = enemy.x+8, enemy.y-12
            # x3, y3 = enemy.x-8, enemy.y-12
            if not enemy.dead:
                imageW = app.shipImages.fleet[-1].w
                imageH = app.shipImages.fleet[-1].h
                shipImage = app.shipImages.fleet[-1].image
                drawImage(CMUImage(shipImage), enemy.x, enemy.y, width=imageW, height=imageH, align='center', rotateAngle=enemy.rotate)
                #drawPolygon(x1, y1, x2, y2, x3, y3, fill='red', rotateAngle=enemy.rotate)
    
class Bullet: # for enemy bullets!
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 4
        self.direction = 1
        self.angle = math.pi/4
        self.rotate = 0
    
    def update1(self):
        self.y += 3
    
    def update2(self, app):
        self.rotate = self.direction*-45
        if self.x >= app.width:
            self.direction = -1
        if self.x <= 0:
            self.direction = 1
        self.x += self.speed*self.direction
        self.y += self.speed
    
    def update3(self, app): # homing
        Xp, Yp = app.playerShip.x, app.playerShip.y
        Xe, Ye = self.x, self.y
        d = ((Xp-Xe)**2 + (Yp-Ye)**2)**0.5
        Xmovement = self.speed*(Xp-Xe)/d
        Ymovement = self.speed*(Yp-Ye)/d
        self.x += Xmovement
        self.y += Ymovement

class Instructions:
    def __init__(self):
        self.instructions = '''INSTRUCTIONS: \n
            To move your ship: the ship follows your mouse movement, \n 
            so use your mouse to control the ship and \n
            dodge enemy bullets. \n
            Objective: in each level, the objective is to kill \n
            all enemies in the level without dying yourself. \n
            Your ship can take 10 hits. In each level, \n
            the enemies will have different health. \n
            To use special skill: every five kills, you will reload \n
            your skill use quota. Press ‘space’ to use the skill and \n
            clear the screen of enemies and bullets. \n
            Press 'escape' to go back to main page.'''
    
    def drawInstructions(self, app):
        numLines = len(self.instructions.splitlines())
        for i in range(numLines):
            drawLabel(self.instructions.splitlines()[i], app.width/2, 
                      (app.height/(numLines+1))*(i+1), size=20, align='center')

def onAppStart(app):
    #app
    app.onStepCounter = 0
    app.paused = False
    app.instructions = Instructions()
    app.gamemode = None
    app.game = Game()
    app.gameState = app.game.currState
    app.buttons = Buttons(app)
    #ships
    app.playerShip = Player(app.width/2, app.height*(3/4))
    app.enemyShips = Enemies(app)
    app.shipImages = Fleet()
    app.buttons2 = Buttons2(app)

def redrawAll(app):
    if app.gameState == 'start':
        drawStartScreen(app)

    if app.gameState == 'instructions':
        drawInstructions(app)

    if app.gameState == 'hangar':
        app.buttons2.drawButtons(app)

    if app.gameState == 'game':
        drawPlayer(app)
        drawEnemies(app)
        drawBullets(app)
    
    if app.gameState == 'game over':
        drawGameOver(app)

def drawPlayer(app):
    app.playerShip.drawPlayer(app)
    #app.shipImages.drawXWing(app, app.playerShip.x, app.playerShip.y)

def drawEnemies(app):
    app.enemyShips.drawEnemy(app)

def drawBullets(app):
    app.playerShip.drawBullets(app)
    for enemy in app.enemyShips.enemies:
        enemy.drawBullets(app)

def drawStartScreen(app):
    app.buttons.drawButtons()
    
def drawInstructions(app):
    app.instructions.drawInstructions(app)

def drawGameOver(app): # game over screen ?
    drawLabel('Game Over!', app.width/2, app.height/2, size=40, bold=True)

def onMouseMove(app, mouseX, mouseY):
    app.playerShip.onMouseMove(app, mouseX, mouseY)

def onStep(app):
    if app.gameState=='game' and not app.paused:
        app.onStepCounter += 1

        for enemy in app.enemyShips.enemies:
            enemy.onStep(app)

        #spawn new enemies
        app.enemyShips.addEnemy(app, app.width/2, -20)
        
        #player bullet movement
        app.playerShip.addBullets(app)
        app.playerShip.moveBullets()

        #player collision
        app.playerShip.collision(app)

        #enemy collision
        for enemy in app.enemyShips.enemies:
            enemy.collision(app)
    
    #handling player death
    if app.playerShip.dead == True:
        app.gamemode = None
        app.gameState = 'game over'
        app.paused = True

def onKeyPress(app, key):
    if key == '1': 
        app.gamemode = 1
    if key == '2': 
        app.gamemode = 2
    if key == '3': 
        app.gamemode = 3
    if key == 'r':
        app.gamemode = None
    if key == 'escape':
        onAppStart(app)
    if key == 'p':
        app.paused = True

def onKeyHold(app, keys):
    app.playerShip.onKeyHold(app, keys)

def onMousePress(app, mouseX, mouseY):
    if app.gameState == 'start':
        app.buttons.returnMode(app, mouseX, mouseY)

    elif app.gameState == 'hangar':
        app.buttons2.getShip(app, mouseX, mouseY)

def distance(x0, y0, x1, y1):
    return ((x0-x1)**2 + (y0-y1)**2)**0.5

def onScreen(app, x, y):
    return (x < app.width+10 and y < app.height+10)

def main():
    runApp(width=600, height=1000)
    print('running app')

main()