import cv2
import pygame as pyg
import random
import numpy as np
import time

# initialise pygames
pyg.init()
clock = pyg.time.Clock()

# FONT -
fontScore = pyg.font.SysFont('comicsans', 30, True, True)
fontEnd = pyg.font.SysFont('comicsans', 70, True)

winSize = (960, 810)
sptSize = (128, 128)

# Window setup
win = pyg.display.set_mode(winSize)
bg = pyg.image.load('resources/Background/background1.jpg')
pyg.display.set_caption('TheGame')

# initialise webcam
cap = cv2.VideoCapture(0)

# SOUND EFFECTS -
hitSound = pyg.mixer.Sound('resources/destroy.wav')
fireSound = pyg.mixer.Sound('resources/shoot.wav')
music = pyg.mixer.music.load('resources/music.mp3')
pyg.mixer.music.play(-1)
pyg.mixer.music.set_volume(0.5)

# delay for camera to let it setup
time.sleep(5)

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
        self.health = 900

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
        color = (0, 255, 0)
        if self.health <= 300:
            color = (255, 0, 0)
        pyg.draw.rect(win, color, (self.x + 15, self.y + self.width + 20, self.health/10, 10), 0)
        pyg.draw.rect(win, (10, 255, 0), (self.x + 15, self.y + self.width + 20, self.width, 10), 1)

    def fire(self):
        if not start and not end:
            if self.bulletInterval > 4:
                fireSound.play()
                self.bulletInterval = 0
                bullets.append(shots(player.x + (player.width // 2), player.y))
            else:
                self.bulletInterval += 1

class Asteroids:

    def __init__(self, x, s):
        self.x = x
        self.y = -s
        self.vel = 6 - (s-100)//50
        self.width = s - 20
        self.height = s - 25         # height and width of box to fit around asteroid
        self.pop = False
        self.size = (s, s)
        self.health = s*2
        self.img = pyg.transform.scale(pyg.image.load('resources/Aestroids/aestroid_brown.png'), self.size)

    def motion(self):
        if self.y < 810:
            self.y += self.vel
        else:
            self.pop = True

    def draw(self, win):
        self.motion()
        win.blit(self.img, (self.x, self.y))
        # pyg.draw.rect(win, (255, 0, 0), (self.x+10, self.y, self.width, self.width), 2)

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


def imageProcessing(image):
    # blur the image 2 times
    blur = cv2.blur(image, (9, 9))
    blur = cv2.blur(blur, (5, 5))

    # Convert into HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # Thresholding ;-)
    lower = np.array([55, 10, 5])
    upper = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)

    # Kernels for erode and dilate respectively
    kernel_square = np.ones((11, 11), np.uint8)
    kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    # Erode and dilate
    dilation = cv2.dilate(mask, kernel_ellipse, iterations=1)
    erosion = cv2.erode(dilation, kernel_square, iterations=1)
    dilation2 = cv2.dilate(erosion, kernel_ellipse, iterations=1)
    erosion2 = cv2.erode(dilation2, kernel_square, iterations=1)
    dilation_final = cv2.dilate(erosion2, kernel_ellipse, iterations=1)
    filtered = cv2.medianBlur(dilation_final, 5)
    kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))
    dilation2 = cv2.dilate(filtered, kernel_ellipse, iterations=1)
    kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dilation3 = cv2.dilate(dilation2, kernel_ellipse, iterations=1)
    thresh = cv2.medianBlur(dilation3, 5)
    return thresh


def largestContour(contours):
    new = contours
    max_area = 100
    ci = 0
    for i in range(len(contours)):
        cnt = contours[i]
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            ci = i
    # print(max_area)
    if max_area < 5000:
        player.fire()       # Fire when area of contour becomes less than 5000 units
    # Largest area contour
    cnts = new[ci]
    moments = cv2.moments(cnts)

    # Central mass of first order moments
    if moments['m00'] != 0:
        cx = int(moments['m10'] / moments['m00'])  # cx = M10/M00
        cy = int(moments['m01'] / moments['m00'])  # cy = M01/M00
        centerMass = (cx, cy)
        # print(cx, cy)
        cv2.circle(img, centerMass, 3, [100, 0, 255], 0)
        return centerMass
    else:
        return (0, 0)

# integrated into redrawWin() function
# def endWin():
#     win.blit(pyg.transform.scale(bg, winSize), (0, 0))
#     text1 = fontScore.render('GAME OVER', 2, (255, 0, 0))
#     text2 = fontScore.render('RESTART SOON', 2, (255, 0, 0))
#     win.blit(text1, (winSize[0]/2-100, winSize[1]/2-50))
#     win.blit(text2, (winSize[0]/2-110, winSize[1]/2))
#     pyg.display.update()


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
            asteroids.pop(asteroids.index(asteroid))
        else:
            asteroid.draw(win)

    pyg.display.update()


# For Key Presses
# left = False
# right = False
# center = True
# keyboard = Controller()
score = 0
restartCounter = 100
delayCounter = 25
end = False
start = True
delay = False
lastPosition = 100
asteroidInterval = 18
play = True
centerMotion = 0
cx_old = 320

while play:
    clock.tick(30)

    ret, img = cap.read()
    height, width, _ = img.shape
    thresh = imageProcessing(img)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img, contours, -1, (122, 122, 0), 2)

    if len(contours) > 0:
        center = largestContour(contours)
        cx = center[0]
        cy = center[1]
        if cx != 0 and cy != 0:
            centerMotion = (cx - cx_old)*2
            cx_old = cx
    disp_img = cv2.flip(img, 1)
    cv2.imshow('Object detection', disp_img)

    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            play = False

    for asteroid in asteroids:
        if max(abs(asteroid.x + 10 + asteroid.width // 2 - player.x - 15 - player.width // 2),
               abs(asteroid.y + asteroid.width // 2 -
                   player.y - 10 - player.width // 2)) < ((asteroid.width + player.width) // 2 - 10):
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
        if asteroid.health < 0:
            hitSound.play()
            asteroid.pop = True

    if asteroidInterval > 19:
        asteroidInterval = 1
        size = random.randint(100, 200)
        pos_x = random.randint(0, 800)
        if abs(lastPosition - pos_x) > 300 and (pos_x + size // 2) < winSize[0]:
            lastPosition = pos_x
            asteroids.append(Asteroids(pos_x, size))
    else:
        asteroidInterval += 1

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

        keys = pyg.key.get_pressed()

        if centerMotion < 0 and player.x + player.width < winSize[0]:
            player.dir = 1
            player.x -= centerMotion
        elif centerMotion > 0 and player.x > 0:
            player.dir = -1
            player.x -= centerMotion
        else:
            player.dir = 0

        # if keys[pyg.K_SPACE]:
            # player.fire()

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

# while 1:
#     ret, img = cap.read()
#     height, width, _ = img.shape
#     thresh = imageProcessing(img)
#     contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#     cv2.drawContours(img, contours, -1, (122, 122, 0), 2)
#
#     if len(contours) > 0:
#         center = largestContour(contours)
#
#     # cv2.line(img, (int(width / 2) - 70, 0), (int(width / 2) - 70, height), (255, 255, 255), 5)
#     # cv2.line(img, (int(width / 2) + 70, 0), (int(width / 2) + 70, height), (255, 255, 255), 5)
#
#     disp_img = cv2.flip(img, 1)
#     cv2.imshow('Object detection', disp_img)

# k = cv2.waitKey(0) & 0xFF
# if k == 27:
cap.release()
cv2.destroyAllWindows()
