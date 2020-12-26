import os
import random
from itertools import cycle

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from PIL import Image

SCREENWIDTH = 288
SCREENHEIGHT = 512
PIPEGAPSIZE = 100  # gap between upper and lower part of pipe
BASEY = SCREENHEIGHT * 0.79

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = (
    # red bird
    (
        '../assets/sprites/redbird-upflap.png',
        '../assets/sprites/redbird-midflap.png',
        '../assets/sprites/redbird-downflap.png',
    ),
    # blue bird
    (
        '../assets/sprites/bluebird-upflap.png',
        '../assets/sprites/bluebird-midflap.png',
        '../assets/sprites/bluebird-downflap.png',
    ),
    # yellow bird
    (
        '../assets/sprites/yellowbird-upflap.png',
        '../assets/sprites/yellowbird-midflap.png',
        '../assets/sprites/yellowbird-downflap.png',
    ),
)

# list of backgrounds
BACKGROUNDS_LIST = (
    '../assets/sprites/background-day.png',
    '../assets/sprites/background-night.png',
)

# list of pipes
PIPES_LIST = (
    '../assets/sprites/pipe-green.png',
    '../assets/sprites/pipe-red.png',
)

try:
    xrange
except NameError:
    xrange = range


def forward(model):
    IMAGES = {}
    HITMASKS = {}
    IMAGES['base'] = Image.open('../assets/sprites/base.png').convert('RGBA')
    # select random background sprites
    randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
    IMAGES['background'] = Image.open(BACKGROUNDS_LIST[randBg])
    # sekect random player sprites
    randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
    IMAGES['player'] = (
        Image.open(PLAYERS_LIST[randPlayer][0]).convert('RGBA'),
        Image.open(PLAYERS_LIST[randPlayer][1]).convert('RGBA'),
        Image.open(PLAYERS_LIST[randPlayer][2]).convert('RGBA'),
    )
    # select random pipe sprites
    pipeindex = random.randint(0, len(PIPES_LIST) - 1)
    IMAGES['pipe'] = (
        Image.open(PIPES_LIST[pipeindex]).convert('RGBA').transpose(Image.FLIP_TOP_BOTTOM),
        Image.open(PIPES_LIST[pipeindex]).convert('RGBA'),
    )

    # hismask for pipes
    HITMASKS['pipe'] = (
        getHitmask(IMAGES['pipe'][0]),
        getHitmask(IMAGES['pipe'][1]),
    )

    # hitmask for player
    HITMASKS['player'] = (
        getHitmask(IMAGES['player'][0]),
        getHitmask(IMAGES['player'][1]),
        getHitmask(IMAGES['player'][2]),
    )

    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].height) / 2)
    basex = 0
    playerIndexGen = cycle([0, 1, 2, 1])

    score = playerIndex = loopIter = 0

    baseShift = IMAGES['base'].width - IMAGES['background'].width

    # get 2 new pipes to add to upperPipes lowerPipes list
    newPipe1 = getRandomPipe(IMAGES)
    newPipe2 = getRandomPipe(IMAGES)

    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]

    # list of lowerpipe
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4

    # player velocity, max velocity, downward accleration, accleration on flap
    playerVelY = -9  # player's velocity along Y, default same as playerFlapped
    playerMaxVelY = 10  # max vel along Y, max descend speed
    playerAccY = 1  # players downward accleration
    playerFlapAcc = -9  # players speed on flapping
    playerFlapped = False  # True when player flaps

    while True:
        # TODO get model input and output here
        jump = True
        if jump:
            if playery > -2 * IMAGES['player'][0].height:
                playerVelY = playerFlapAcc
                playerFlapped = True

        # check for crash here
        crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
                               upperPipes, lowerPipes, IMAGES, HITMASKS)
        if crashTest[0]:
            return score, crashTest[1], playery, upperPipes, lowerPipes, playerVelY

        # check for score
        playerMidPos = playerx + IMAGES['player'][0].width / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].width / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1

        # playerIndex basex change
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # player's movement
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False

        playerHeight = IMAGES['player'][playerIndex].height
        playery += min(playerVelY, BASEY - playery - playerHeight)

        # move pipes to left
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if len(upperPipes) > 0 and 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe(IMAGES)
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if len(upperPipes) > 0 and upperPipes[0]['x'] < -IMAGES['pipe'][0].width:
            upperPipes.pop(0)
            lowerPipes.pop(0)


def getRandomPipe(IMAGES):
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].height
    pipeX = SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE},  # lower pipe
    ]


def checkCrash(player, upperPipes, lowerPipes, IMAGES, HITMASKS):
    """returns True if player collders with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].width
    player['h'] = IMAGES['player'][0].height

    # if player crashes into ground
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                                 player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].width
        pipeH = IMAGES['pipe'][0].height

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]


def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1 + x][y1 + y] and hitmask2[x2 + x][y2 + y]:
                return True
    return False


def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.width):
        mask.append([])
        for y in xrange(image.height):
            mask[x].append(bool(image.getpixel((x, y))[3]))
    return mask


if __name__ == '__main__':
    print(forward(None))
