import pygame as pyg
import random
from behaviour_nodes import *
# from pynput.keyboard import Key, Controller

# initialise pygames
pyg.init()

clock = pyg.time.Clock()

# FONT -
fontScore = pyg.font.SysFont('comicsans', 30, True, True)
fontEnd = pyg.font.SysFont('comicsans', 70, True)

winSize = (960, 810)
sptSize = (128, 128)

# SOUND EFFECTS -
hitSound = pyg.mixer.Sound('resources/destroy.wav')
fireSound = pyg.mixer.Sound('resources/shoot.wav')
music = pyg.mixer.music.load('resources/music.mp3')
pyg.mixer.music.play(-1)
pyg.mixer.music.set_volume(0.5)

# Window setup
win = pyg.display.set_mode(winSize)
bg = pyg.image.load('resources/Background/background1.jpg')
pyg.display.set_caption('TheGame')


# defining class of our ship
class ship:
    static = [pyg.transform.scale(pyg.image.load('resources/Blue/Small_ship_blue/L1.png'), sptSize),
              pyg.transform.scale(pyg.image.load('resources/Blue/Small_ship_blue/R1.png'), sptSize)]
    flyRight = [pyg.transform.scale(pyg.image.load('resources/Blue/Small_ship_blue/R2.png'), sptSize),
                pyg.transform.scale(pyg.image.load('resources/Blue/Small_ship_blue/R3.png'), sptSize)]
    flyLeft = [pyg.transform.scale(pyg.image.load('resources/Blue/Small_ship_blue/L2.png'), sptSize),
               pyg.transform.scale(pyg.image.load('resources/Blue/Small_ship_blue/L3.png'), sptSize)]
    bulletInterval = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dir = 0
        self.vel = 15
        self.width = 95     # not image width but the width of the rectangle around it
        self.moveCount = 0  # to switch between sprites
        self.health = 950

    def draw(self, win):
        if self.moveCount == 30:
            self.moveCount = 0
        else:
            self.moveCount += 1

        if self.dir == 0:
            win.blit(self.static[self.moveCount % 2], (self.x, self.y))
        elif self.dir == 1:
            win.blit(self.flyRight[self.moveCount % 2], (self.x, self.y))
        elif self.dir == -1:
            win.blit(self.flyLeft[self.moveCount % 2], (self.x, self.y))
        # pyg.draw.rect(win, (0, 255, 0), (self.x + 15, self.y, self.width, self.width), 1)
        pyg.draw.rect(win, (0, 255, 0), (self.x + 15, self.y + self.width + 20, self.health/10, 10), 0)
        pyg.draw.rect(win, (10, 255, 0), (self.x + 15, self.y + self.width + 20, self.width, 10), 1)

    def fire(self):
        if not start and not end:
            if self.bulletInterval > 4:
                fireSound.play()
                self.bulletInterval = 0
                bullets.append(shots(player.x + (player.width // 2), player.y))
                return True
            else:
                self.bulletInterval += 1
                return False

    def moveRight(self):
        if self.x + self.width < 960 - self.vel:
            self.dir = 1
            self.x += self.vel

    def moveLeft(self):
        if self.x > self.vel:
            self.dir = -1
            self.x -= self.vel


class Asteroids:

    def __init__(self, x, s):   # s lies in [100, 200]
        self.x = x
        self.y = -s
        self.vel = 6 - (s-100)//50
        self.width = s - 20
        self.height = s - 25
        self.pop = False
        self.size = (s, s)
        self.health = s*2
        self.healthPredictor = s * 2
        self.img = pyg.transform.scale(pyg.image.load('resources/Aestroids/aestroid_brown.png'), self.size)

    def motion(self):
        if self.y < 810:
            self.y += self.vel
        else:
            self.pop = True

    def draw(self, win):
        self.motion()
        win.blit(self.img, (self.x, self.y))
        # if self == findTarget.target:
        #     pyg.draw.rect(win, (255, 0, 0), (self.x+10, self.y + 9, self.width, self.height), 2)


class shots():
    size = (48, 48)
    image = pyg.transform.scale(pyg.image.load('resources/Blue/bullet.png'), size)

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = 16
        self.pop = False
        self.width = 20

    def motion(self):
        if self.y + 10 > 0:
            self.y -= self.vel
        else:
            self.pop = True

    def draw(self, win):
        self.motion()
        win.blit(self.image, (self.x, self.y))
        # pyg.draw.rect(win, (255, 0, 0), (self.x + 14, self.y, self.width, self.width), 2)


startLocn = (winSize[0]//2 - sptSize[0], winSize[1] - sptSize[1] - 10)
player = ship(startLocn[0], startLocn[1])
bullets = []
asteroids = []


def endWin():
    win.blit(pyg.transform.scale(bg, winSize), (0, 0))
    text1 = fontScore.render('GAME OVER', 2, (255, 0, 0))
    text2 = fontScore.render('RESTART SOON', 2, (255, 0, 0))
    win.blit(text1, (winSize[0]/2-100, winSize[1]/2-50))
    win.blit(text2, (winSize[0]/2-110, winSize[1]/2))
    pyg.display.update()


def redrawWin(start, end):
    win.blit(pyg.transform.scale(bg, winSize), (0, 0))
    if start:
        textStart = fontEnd.render('PRESS SPACE TO START', 2, (255, 0, 0))
        win.blit(textStart, (winSize[0] / 2 - 320, winSize[1] / 2 - 50))
    elif end:
        text1 = fontEnd.render('GAME OVER', 2, (255, 0, 0))
        text2 = fontEnd.render('RESTARTING SOON', 2, (255, 0, 0))
        win.blit(text1, (winSize[0] / 2 - 200, winSize[1] / 2 - 50))
        win.blit(text2, (winSize[0] / 2 - 250, winSize[1] / 2))
    else:
        text = fontScore.render('Score - ' + str(score), 2, (27, 229, 54))
        win.blit(text, (winSize[0] - 150, winSize[1] - 50))
    if not end:
        if start:
            player.dir = 0
        player.draw(win)
    for bullet in bullets:
        if bullet.pop:
            bullets.pop(bullets.index(bullet))
        else:
            bullet.draw(win)

    for asteroid in asteroids:
        if asteroid.pop:
            if asteroid == findTarget.target:
                findTarget.target = None
            asteroids.pop(asteroids.index(asteroid))
        else:
            asteroid.draw(win)

    pyg.display.update()


# Decision Tree implementation try 1...
# I will try to automaticaly fire bullets when the ship is below an asteroid


moveleft = Move("moveleft", -1, player)
moveright = Move("moveright", 1, player)
# approach_defenseSelector = Selector("approach/defense",)

# Fire subtree
firenode = FireNode("firenode", player)
istarget = RandomTargetInRange("istarget", player, asteroids)
shoot = AttackSequence("ShootNode", children=[istarget, firenode])
# Target Approach Subtree
findTarget = findBestTarget("TargetLocatorNode", player, asteroids)

isinrange = TargetInRange("IsTheTargetInRange", player, findTarget)
approachTarget = ApproachTarget("AprroachTargetNode", player, findTarget)
ontarget = Selector("IsOnTarget", children=[isinrange, approachTarget])

approachSeq = Sequence("ApproachSequenceNode", children=[findTarget, ontarget])



# defence subtree

#both side obstacle
leftCheck = CheckLeft("leftCheck", player, asteroids)
rightCheck = CheckRight("rightCheck", player, asteroids)
bestMove = MoveBest("bestMove", player, leftCheck, rightCheck)

bothSide = Sequence("bothSideSequence", children=[leftCheck, rightCheck, bestMove])

#left side  obstacle
leftSeq = Sequence("leftSideSequence", children=[leftCheck, moveright])

#right side obstacle
rightSeq = Sequence("rightSideSequence", children=[rightCheck, moveleft])

defenceSelector = Selector("defenceSelector", children=[bothSide, leftSeq, rightSeq])
rootSelector = rootLoop("rootSelector", findTarget, children=[defenceSelector, approachSeq, shoot])

score = 0
restartCounter = 100
delayCounter = 25
end = False
start = True
delay = False
lastPosition = 100
bulletInterval = 5
asteroidInterval = 5
asteroidIntervalCounter = asteroidInterval + 1
play = True
while play:
    clock.tick(30)
    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            play = False

    for asteroid in asteroids:
        if max(abs(asteroid.x + 10 + asteroid.width // 2 - player.x - 15 - player.width // 2),
               abs(asteroid.y + 9 + asteroid.height // 2 -
                   player.y - 5 - player.width // 2)) < ((asteroid.width + player.width) // 2 - 10):
            # print('You hit an asteroid')
            if not start and not end:
                if player.health - 100 > 0:
                    player.health -= 100
                    asteroid.pop = True
                else:
                    player.health = 0

        for bullet in bullets:
            if bullet.y <= asteroid.y + asteroid.width - 5 and bullet.y > asteroid.y:
                if bullet.x > asteroid.x - 5 and bullet.x < asteroid.x + asteroid.width - 5:
                    bullet.pop = True
                    asteroid.health -= 150
                    score += 10
        if asteroid.health <= 0:
            hitSound.play()
            asteroid.pop = True

    if asteroidIntervalCounter > asteroidInterval:
        asteroidIntervalCounter = 1
        size = random.randint(100, 200)
        pos_x = random.randint(0, 800)
        if abs(lastPosition - pos_x) > 300 and (pos_x + size // 2) < winSize[0]:
            lastPosition = pos_x
            asteroids.append(Asteroids(pos_x, size))
    else:
        asteroidIntervalCounter += 1

    if start:
        keys = pyg.key.get_pressed()
        if keys[pyg.K_SPACE]:
            delay = True
        if delay:
            if delayCounter > 0:
                pyg.time.delay(10)
                delayCounter -= 1
                for event in pyg.event.get():
                    if event.type == pyg.QUIT:
                        pyg.quit()
            else:
                delayCounter = 25
                start = False
                delay = False

    elif not end:

        if player.health == 0:
            end = True

        # rootSelector.run()
        keys = pyg.key.get_pressed()
        if keys[pyg.K_RIGHT] and player.x + player.width < winSize[0]:
            player.moveRight()
        elif keys[pyg.K_LEFT] and player.x > 0:
            player.moveLeft()
        else:
            player.dir = 0

        if keys[pyg.K_SPACE]:
            if bulletInterval > 4:
                fireSound.play()
                bulletInterval = 0
                bullets.append(shots(player.x + (player.width//2), player.y))
            else:
                bulletInterval += 1

    else:
        score = 0
        pyg.time.delay(10)
        restartCounter -= 1
        if restartCounter == 0:
            restartCounter = 100
            player.health = 1000
            end = False
            start = True

    redrawWin(start, end)



