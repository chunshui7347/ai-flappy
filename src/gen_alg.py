import copy
import os
import pickle
import random
import subprocess
import sys
from itertools import cycle

import matplotlib.pyplot as plt
import numpy as np
import pygame
import tensorflow as tf
from PIL import Image
from pygame.locals import *

from src.basegame_flappy import SCREENWIDTH, SCREENHEIGHT, PIPEGAPSIZE, BASEY, pixelCollision, getHitmask
from src.util import make_model

FPS = 30
MAX_SCORE = 1000
# image, sound and hitmask
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

resume_previous = False
save_current_pool = True
pool_dir = '../data/current_pool'
os.makedirs(pool_dir, exist_ok=True)
total_models = 20
max_generation = 100

# change if resume from previous
generation = 1
previous_best = -1
best_idx_so_far = -1


def save_pool():
    for i in range(total_models):
        with open(os.path.join(pool_dir, 'model_{}.pickle'.format(i)), 'wb') as f:
            pickle.dump(current_pool[i], f)


def crossover(weights1, weights2):
    # cross over weights of first layer by randomly swapping weights
    ori_shape = weights1[0].shape
    weights1[0] = weights1[0].flatten()
    weights2[0] = weights2[0].flatten()
    weightsnew1 = copy.deepcopy(weights1)
    weightsnew2 = copy.deepcopy(weights2)
    indexes = random.sample(range(len(weights1[0])), len(weights1[0]) // 2)
    weightsnew1[0][indexes] = weights2[0][indexes]
    weightsnew2[0][indexes] = weights1[0][indexes]
    weightsnew1[0] = weightsnew1[0].reshape(ori_shape)
    weightsnew2[0] = weightsnew2[0].reshape(ori_shape)
    weights1[0] = weights1[0].reshape(ori_shape)
    weights2[0] = weights2[0].reshape(ori_shape)
    return np.asarray([weightsnew1, weightsnew2])


def mutate(weights, mutation_rate=0.15):
    # randomly mutate each synapse weight and biases based on mutation rate
    for i in range(len(weights)):
        for j in range(len(weights[i])):
            if random.uniform(0, 1) < mutation_rate:
                change = random.uniform(-0.5, 0.5)
                weights[i][j] += change
    return weights


def predict_jump(height, dist, pipe_height, model_num):
    # the height, dist and pipe_height scaled to 0 to 1
    height = min(SCREENHEIGHT, height) / SCREENHEIGHT
    dist = dist / 450  # max pipe distance from player will be 450 (first pipe that is out of screen)
    pipe_height = min(SCREENHEIGHT, pipe_height) / SCREENHEIGHT
    inputs = [height, dist, pipe_height]
    model.set_weights(current_pool[model_num])
    output_prob = model.predict([inputs])[0]
    if output_prob[0] >= 0.5:
        # Perform jump action
        return True
    return False


# Initialize all models
model = make_model()
current_pool = [make_model().get_weights() for _ in range(total_models)]
fitness = [-1] * total_models

if resume_previous:
    for i in range(total_models):
        with open(os.path.join(pool_dir, 'model_{}.h5'.format(i)), 'rb') as f:
            current_pool[i] = pickle.load(f)

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
        # amount by which base can maximum shift to left
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


def main(save_video=False, log=True):
    if log:
        with open(os.path.join('..', 'data', 'log.txt'), 'w') as f:
            f.write('history fitness\n')
    global SCREEN, FPSCLOCK
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((int(SCREENWIDTH), int(SCREENHEIGHT)))
    pygame.display.set_caption('Flappy Bird')

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('../assets/sprites/0.png').convert_alpha(),
        pygame.image.load('../assets/sprites/1.png').convert_alpha(),
        pygame.image.load('../assets/sprites/2.png').convert_alpha(),
        pygame.image.load('../assets/sprites/3.png').convert_alpha(),
        pygame.image.load('../assets/sprites/4.png').convert_alpha(),
        pygame.image.load('../assets/sprites/5.png').convert_alpha(),
        pygame.image.load('../assets/sprites/6.png').convert_alpha(),
        pygame.image.load('../assets/sprites/7.png').convert_alpha(),
        pygame.image.load('../assets/sprites/8.png').convert_alpha(),
        pygame.image.load('../assets/sprites/9.png').convert_alpha()
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('../assets/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('../assets/sprites/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('../assets/sprites/base.png').convert_alpha()

    # sounds
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SOUNDS['die'] = pygame.mixer.Sound('../assets/audio/die' + soundExt)
    SOUNDS['hit'] = pygame.mixer.Sound('../assets/audio/hit' + soundExt)
    SOUNDS['point'] = pygame.mixer.Sound('../assets/audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('../assets/audio/swoosh' + soundExt)
    SOUNDS['wing'] = pygame.mixer.Sound('../assets/audio/wing' + soundExt)

    if save_video:
        dimen = str(SCREENWIDTH) + 'x' + str(SCREENHEIGHT)
        global proc
        proc = subprocess.Popen(['ffmpeg',
                                 '-y',
                                 '-f', 'jpegls_pipe',
                                 '-vcodec', 'jpegls',
                                 '-s', dimen,
                                 '-i', '-',
                                 '-an',
                                 '-r', str(FPS),
                                 '-b:v', '500k',
                                 '../data/learning.mp4'], stdin=subprocess.PIPE)

    while generation <= max_generation:
        # select random background sprites
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

        # select random player sprites
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        # select random pipe sprites
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (
            pygame.transform.rotate(
                pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), 180),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
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

        global fitness
        for idx in range(total_models):
            fitness[idx] = 0
        best_idx = mainGame({
            'playery': int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2),
            'basex': 0,
            'playerIndexGen': cycle([0, 1, 2, 1]),
        }, save_video)
        if best_idx is not None:
            print('stop condition met, best model index:', best_idx)
            with open(os.path.join('..', 'data', 'best_weight.pickle'), 'wb') as f:
                pickle.dump(current_pool[best_idx], f)
            if save_video:
                proc.stdin.close()
                proc.wait()
            break
        else:
            showGameOverScreen(log)


def mainGame(movementInfo, save_video):
    global fitness
    if save_video:
        global proc
    playerIndex = loopIter = 0
    scores = [0] * total_models
    playerIndexGen = movementInfo['playerIndexGen']
    playersXList = [int(SCREENWIDTH * 0.2)] * total_models
    playersYList = [movementInfo['playery']] * total_models

    basex = movementInfo['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 new pipes to add to upperPipes lowerPipes list
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

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

    next_pipe_x = lowerPipes[0]['x'] + IMAGES['pipe'][0].get_width()
    next_pipe_hole_y = (lowerPipes[0]['y'] + (upperPipes[0]['y'] + IMAGES['pipe'][0].get_height())) / 2

    pipeVelX = -4

    # player velocity, max velocity, downward accleration, accleration on flap
    playersVelY = [-9] * total_models  # player's velocity along Y, default same as playerFlapped
    playerMaxVelY = 10  # max vel along Y, max descend speed
    playersAccY = [1] * total_models  # players downward accleration
    playerFlapAcc = -9  # players speed on flapping
    playersFlapped = [False] * total_models  # True when player flaps
    playerIsAlive = [True] * total_models  # True if player is still alive

    alive_players = total_models

    while True:
        # check if player is off screen
        for idxPlayer in range(total_models):
            if playersYList[idxPlayer] < 0 and playerIsAlive[idxPlayer]:
                alive_players -= 1
                playerIsAlive[idxPlayer] = False
                fitness[idxPlayer] = fitness[idxPlayer] // 2  # penalize for going off screen
        if alive_players == 0:
            return
        for idxPlayer in range(total_models):
            if playerIsAlive[idxPlayer]:
                fitness[idxPlayer] += 1  # reward for staying alive
        next_pipe_x += pipeVelX
        for idxPlayer in range(total_models):
            if playerIsAlive[idxPlayer]:
                if predict_jump(playersYList[idxPlayer], next_pipe_x, next_pipe_hole_y, idxPlayer):
                    if playersYList[idxPlayer] > -2 * IMAGES['player'][0].get_height():
                        playersVelY[idxPlayer] = playerFlapAcc
                        playersFlapped[idxPlayer] = True
                        # SOUNDS['wing'].play()
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                if save_video:
                    proc.stdin.close()
                    proc.wait()
                pygame.quit()
                sys.exit()

        # check for crash here, returns status list
        crashTest = checkCrash({'x': playersXList, 'y': playersYList, 'index': playerIndex}, playerIsAlive,
                               upperPipes, lowerPipes)

        for idx in range(total_models):
            if playerIsAlive[idx] and crashTest[idx] == 1:  # hit pipe
                if alive_players >= total_models // 2:
                    fitness[idx] = fitness[idx] // 2  # penalize for dying first
                alive_players -= 1
                playerIsAlive[idx] = False
            elif playerIsAlive[idx] and crashTest[idx] == 0:  # hit ground
                alive_players -= 1
                playerIsAlive[idx] = False
                fitness[idx] = fitness[idx] // 2  # penalize for hitting ground

        if alive_players == 0:
            return

        # check for score
        for idx in range(total_models):
            if playerIsAlive[idx]:
                playerMidPos = playersXList[idx]
                for pipe_idx in range(len(upperPipes)):
                    pipeMidPos = upperPipes[pipe_idx]['x'] + IMAGES['pipe'][0].get_width()
                    if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                        next_pipe_x = lowerPipes[pipe_idx + 1]['x'] + IMAGES['pipe'][0].get_width()
                        next_pipe_hole_y = (lowerPipes[pipe_idx + 1]['y'] + (
                                upperPipes[pipe_idx + 1]['y'] + IMAGES['pipe'][pipe_idx + 1].get_height())) / 2
                        scores[idx] += 1
                        if scores[idx] >= MAX_SCORE:
                            return idx
                        fitness[idx] += 50  # reward for passing pipes
                        # SOUNDS['point'].play()

        # playerIndex basex change
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # player's movement
        for idx in range(total_models):
            if playerIsAlive[idx]:
                if playersVelY[idx] < playerMaxVelY and not playersFlapped[idx]:
                    playersVelY[idx] += playersAccY[idx]
                if playersFlapped[idx]:
                    playersFlapped[idx] = False
                playerHeight = IMAGES['player'][playerIndex].get_height()
                playersYList[idx] += min(playersVelY[idx], BASEY - playersYList[idx] - playerHeight)

        # move pipes to left
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        # print score so player overlaps the score
        showScore(max(scores))
        for idx in range(total_models):
            if playerIsAlive[idx]:
                SCREEN.blit(IMAGES['player'][playerIndex], (playersXList[idx], playersYList[idx]))

        showInfo(sum(playerIsAlive))
        pygame.display.update()
        if save_video:
            img = Image.frombytes('RGB', SCREEN.get_size(), pygame.image.tostring(SCREEN, 'RGB', False))
            img.save(proc.stdin, 'JPEG')

        FPSCLOCK.tick(FPS)


def showGameOverScreen(log):
    """crossover and mutate here"""
    global current_pool
    global fitness
    global generation
    global previous_best
    global previous_best, best_idx_so_far

    new_weights = []
    total_fitness = 0
    best_fit = max(fitness)
    if log:
        with open(os.path.join('..', 'data', 'log.txt'), 'a') as f:
            f.write('{}\n'.format(best_fit))
    if best_fit > previous_best:
        previous_best = best_fit
        best_idx_so_far = fitness.index(best_fit)
        if save_current_pool:
            with open(os.path.join('..', 'data', 'best_weights_so_far.pickle'), 'wb') as f:
                pickle.dump(current_pool[best_idx_so_far], f)

    # roulette selection
    for select in range(total_models):
        total_fitness += fitness[select]
    for select in range(total_models):
        fitness[select] /= total_fitness
        if select > 0:
            fitness[select] += fitness[select - 1]
    for select in range(int(total_models / 2)):
        parent1 = random.uniform(0, 1)
        parent2 = random.uniform(0, 1)
        idx1 = -1
        idx2 = -1
        for idxx in range(total_models):
            if fitness[idxx] >= parent1:
                idx1 = idxx
                break
        for idxx in range(total_models):
            if fitness[idxx] >= parent2:
                idx2 = idxx
                break
        new_weights1 = crossover(current_pool[idx1], current_pool[idx2])
        updated_weights1 = mutate(new_weights1[0])
        updated_weights2 = mutate(new_weights1[1])
        new_weights.append(updated_weights1)
        new_weights.append(updated_weights2)
    for select in range(len(new_weights)):
        fitness[select] = -1
        current_pool[select] = new_weights[select]
    if save_current_pool:
        save_pool()
    generation = generation + 1
    return


def getRandomPipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE},  # lower pipe
    ]


def showInfo(alive_count):
    """show genetic algo info"""
    fsize = 10
    default_font = pygame.font.get_default_font()
    font_renderer = pygame.font.Font(default_font, fsize)

    # To create a surface containing `Some Text`
    lines = ["Generation: {}".format(generation), "Previous Best: {}".format(previous_best),
             "Current Best: {}".format(max(fitness)), "Current Alive: {}".format(alive_count)]
    for i, l in enumerate(lines):
        label = font_renderer.render(l, True, (255, 255, 255))
        SCREEN.blit(label, (5, SCREENHEIGHT - 5 - fsize * (i + 1)))


def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0  # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def checkCrash(players, playerIsAlive, upperPipes, lowerPipes):
    """returns 1 if player colldes pipes else 0 if collides with base"""
    statuses = [-1] * total_models

    for idx in range(total_models):
        if not playerIsAlive[idx]:
            statuses[idx] = -1
            continue
        statuses[idx] = -1
        pi = players['index']
        players['w'] = IMAGES['player'][0].get_width()
        players['h'] = IMAGES['player'][0].get_height()
        # if player crashes into ground
        if players['y'][idx] + players['h'] >= BASEY - 1:
            statuses[idx] = 0
        playerRect = pygame.Rect(players['x'][idx], players['y'][idx],
                                 players['w'], players['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

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
                statuses[idx] = 1
    return statuses


if __name__ == '__main__':
    with tf.device('/cpu:0'):
        main(save_video=True)

    with open(os.path.join('..', 'data', 'log.txt'), 'r') as f:
        lines = f.read()
    data = list(map(int, lines.strip().split('\n')[1:]))
    plt.figure(figsize=(8, 8))
    plt.plot(data)
    plt.xlabel('Fitness')
    plt.ylabel('Generation')
    plt.savefig(os.path.join('..', 'data', 'fitness.png'))
    plt.show()
