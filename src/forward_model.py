import random
from itertools import cycle

import pygame
from PIL import Image

from src.basegame_flappy import SCREENWIDTH, SCREENHEIGHT, PIPEGAPSIZE, BASEY, PLAYERS_LIST, BACKGROUNDS_LIST, \
    PIPES_LIST, getHitmask, getRandomPipe, checkCrash, pixelCollision

MAX_SCORE = 100000

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

    score = playerIndex = loopIter = travelled = 0

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
        if score >= MAX_SCORE:
            return score, travelled
        # input are player y, velocity, dist to next pipe, upper pipe height, lower pipe height
        nextPipeIndex = getNextPipe(playerx, upperPipes, IMAGES['pipe'][0].width)
        inputs = [playery / SCREENHEIGHT, playerVelY / playerMaxVelY,
                  (upperPipes[nextPipeIndex]['x'] - playerx) / SCREENWIDTH,
                  (lowerPipes[nextPipeIndex]['y'] - PIPEGAPSIZE) / SCREENHEIGHT,
                  (SCREENHEIGHT - lowerPipes[nextPipeIndex]['y']) / SCREENHEIGHT]
        pred = model.predict([inputs])[0]
        # flap if pred >= 0.5
        if pred >= 0.5:
            if playery > -2 * IMAGES['player'][0].height:
                playerVelY = playerFlapAcc
                playerFlapped = True

        # check for crash here
        crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
                               upperPipes, lowerPipes, IMAGES, HITMASKS)
        if crashTest[0]:
            return score, travelled

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

        travelled += 1

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


def getNextPipe(playerx, pipes, pipeWidth):
    """returns the index of the next pipe"""
    for i, pipe in enumerate(pipes):
        if pipe['x'] + pipeWidth > playerx:
            return i


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


def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.width):
        mask.append([])
        for y in xrange(image.height):
            mask[x].append(bool(image.getpixel((x, y))[3]))
    return mask