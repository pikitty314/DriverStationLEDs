import board
import neopixel
import time
import random

## NOTE: Ticks refer to board time, time refers to match time

# Constants
BRIGHTNESS = 0.5

CHASE_SPEED = 1
CHASE_LENGTH = 10

RAINBOW_SPEED = 200
RAINBOW_DENSITY = 10

# Pixel strip
pixels = neopixel.NeoPixel(board.GP0, 70, auto_write=False, brightness=BRIGHTNESS)

# Colors
BLUE = (0,0,100)
LIGHT_BLUE = (0,5,100)
RED = (100,0,0)
LIGHT_RED = (100,5,0)
PURPLE = (100, 0, 100)
WHITE = (255,255,255)
OFF = (0, 0, 0)

# Eventually these get read from the DS laptop
matchActive = True
currentTime = 160
autonWinner = 'B'
ourRobotColor = 'B'
lastUpdateTick = time.monotonic()

def getShiftTime():
    if currentTime > 140:
        return currentTime - 140
    # if in transition return how much time remains in transition
    elif currentTime > 130:
        return currentTime - 130
    # if in shift 1 return how long is in shift1 
    elif currentTime > 105:
        return currentTime - 105
    # if in shift 2 return how long is in shift2 
    elif currentTime > 80:
        return currentTime - 80
    # if in shift 3 return how long is in shift3 
    elif currentTime > 55:
        return currentTime - 55
    # if in shift 4 return how long is in shift4 
    elif currentTime > 30:
        return currentTime - 30
    # if in endgame return how long is in endgame 
    else:
        return currentTime

def getActiveHubColor():
    blueWonAuto = (autonWinner == 'B')
    ourRobotIsBlue = (ourRobotColor == 'B')
    
    if currentTime > 130:
        return BLUE if ourRobotIsBlue else RED
    elif currentTime > 105:
        return RED if blueWonAuto else BLUE
    elif currentTime > 80:
        return BLUE if blueWonAuto else RED
    elif currentTime > 55:
        return RED if blueWonAuto else BLUE
    elif currentTime > 30:
        return BLUE if blueWonAuto else RED
    else:
        return BLUE if ourRobotIsBlue else RED
    
def fade(firstColor, secondColor, progress):
    r = int((firstColor[0] * (1-progress)) + secondColor[0]*progress)
    g = int((firstColor[1] * (1-progress)) + secondColor[1]*progress)
    b = int((firstColor[2] * (1-progress)) + secondColor[2]*progress)
    return (r,g,b)

def rainbowColorWheel(seed):
    if seed < 0 or seed > 255:
        seed = int(random.randrange(range(0,256)))
    
    if seed < 85:
        return (255 - seed * 3, seed * 3, 0)
    elif seed < 170:
        seed -= 85
        return (0, 255 - seed * 3, seed * 3)
    else:
        seed -= 170
        return (seed * 3, 0, 255 - seed * 3)
    
def updateStripStandard(activeAllianceColor,shiftTime):
    for x in range(0,shiftTime):
        pixels[x] = activeAllianceColor
        pixels[len(pixels) - x - 1] = activeAllianceColor
    for x in range(shiftTime,29):
        pixels[x] = OFF
        pixels[len(pixels) - x - 1] = OFF
    for x in range(29,len(pixels)-29):
        pixels[x] = activeAllianceColor

    pixels.show()

def updateStripWithChaser(activeAllianceColor, shiftTime):
    for x in range(0,shiftTime):
        pixels[x] = activeAllianceColor
        pixels[len(pixels) - x - 1] = activeAllianceColor
    for x in range(shiftTime,29):
        pixels[x] = OFF
        pixels[len(pixels) - x - 1] = OFF
    for x in range(29,len(pixels)-29):
        pixels[x] = activeAllianceColor

    progress = time.monotonic() % (1/CHASE_SPEED)

    if shiftTime > 0:
        head = int(len(pixels) * CHASE_SPEED * progress)
        tail = int(head-CHASE_LENGTH)
        for x in range(CHASE_LENGTH):
            if 0 <= x < len(pixels):
                if 0 <= x + tail <= shiftTime or len(pixels)-shiftTime <= x + tail <= len(pixels) or 30<= x + tail <= len(pixels)-30:
                    pixels[x + tail] = fade(activeAllianceColor, WHITE, x/CHASE_LENGTH)
                else:
                    pixels[x + tail] = pixels[x + tail] = fade(OFF, WHITE, x/CHASE_LENGTH)

    pixels.show()

def updateStripRainbow(shiftTime):
    offset = int(time.monotonic() * RAINBOW_SPEED) % 256

    for x in range(len(pixels)):
        pixels[x] = rainbowColorWheel((x * RAINBOW_DENSITY + offset) % 256)
    for x in range(shiftTime,29):
        pixels[x] = OFF
        pixels[len(pixels) - x - 1] = OFF

    pixels.show()

def rainbowWipe():
    offset = int(time.monotonic() * RAINBOW_SPEED) % 256

    for x in range(len(pixels)):
        pixels[x] = rainbowColorWheel((x * RAINBOW_DENSITY + offset) % 256)

while True:
    if matchActive:
        currentTick = time.monotonic()

        if currentTick - lastUpdateTick >= 1:
            currentTime -= 1
            lastUpdateTick = currentTick

            if currentTime <= 0:
                matchActive = False        
        if currentTime > 140:
            updateStripRainbow(getShiftTime())
        elif currentTime > 130 and ourRobotColor == autonWinner:
            updateStripWithChaser(getActiveHubColor(), getShiftTime())
        else:
            updateStripStandard(getActiveHubColor(), getShiftTime())

    else:
        pixels.fill(PURPLE)
        pixels.show()