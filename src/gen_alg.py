import copy
import os
import pickle
import random
import time
import subprocess
import sys
from itertools import cycle

import matplotlib.pyplot as plt
import numpy as np
import pygame
from PIL import Image
from pygame.locals import *

from basegame_flappy import SCREENWIDTH, SCREENHEIGHT, PIPEGAPSIZE, BASEY, pixelCollision, getHitmask
from util import make_model

FPS = 60  # use higher value for faster simulation, default is 30
MAX_SCORE = 20000  # maximum score as stop condition, maximum pipe combination is 142*142 = 20164
# image, sound and hitmask
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

resume_previous = False  # resume from previous run
save_current_pool = True  # save current pool to resume later
pool_dir = '../data/current_pool'
os.makedirs(pool_dir, exist_ok=True)
total_models = 50
max_generation = 200

# change if resume from previous
generation = 1
previous_best = -1
best_idx_so_far = -1
local_minima_stuck_time = 0


def save_pool():
    """
    method to save pools
    """
    for i in range(total_models):
        with open(os.path.join(pool_dir, 'model_{}.pickle'.format(i)), 'wb') as f:
            pickle.dump(current_pool[i], f)


def crossover(weights1_idx, weights2_idx, uniform_rate=0.5):
    """
    cross over weights of layers by swapping nodes

    :param weights1_idx: index of parent 1 weights
    :type weights1_idx: int
    :param weights2_idx: index of parent 2 weights
    :type weights2_idx: idx
    :param uniform_rate: rate of swapping, default is 0.5
    :type uniform_rate: float
    :return: np.ndarray of cross overed weights
    :rtype: list[list[np.ndarray]]
    """
    weights1 = current_pool[weights1_idx]
    weights2 = current_pool[weights2_idx]
    weightsnew1 = copy.deepcopy(weights1)

    for i in range(len(weightsnew1)):
        ori_shape = weights1[i].shape
        weights2[i] = weights2[i].flatten()
        weightsnew1[i] = weightsnew1[i].flatten()
        for j in range(len(weightsnew1[i])):
            if random.random() < uniform_rate:
                weightsnew1[i] = weights2[i]
        weights2[i] = weights2[i].reshape(ori_shape)
        weightsnew1[i] = weightsnew1[i].reshape(ori_shape)

    return weightsnew1


def mutate(weights, mutation_rate=0.01):
    """
    randomly mutate each synapse weight and biases based on mutation rate
    :param weights: list of weights to mutate
    :type weights: list[np.ndarray]
    :param mutation_rate: mutation probability between 0 and 1
    :type mutation_rate: float
    :return: mutated weights
    :rtype: list[np.ndarray]
    """
    for i in range(len(weights)):
        for j in range(len(weights[i])):
            if random.random() < mutation_rate:
                weights[i][j] += weights[i][j] * (random.random() - 0.5) * 3 + (random.random() - 0.5)
                # weights[i][j] = np.random.uniform(-1, 1)
    return weights


def predict_jump(height, dist, pipe_height, vel, diff_in_pipe, model_num):
    """
    :param height: height of bird
    :type height: int
    :param vel: y velocity of bird
    :type vel: int
    :param dist: horizontal distance to next pipe
    :type dist: int
    :param pipe_height: height of next pipe
    :type pipe_height: int
    :param model_num: index of model to use from pool
    :type model_num: int
    :return: boolean to jump or not
    :rtype: bool
    """
    # the height, dist and pipe_height scaled to 0 to 1
    dist = min(dist / SCREENWIDTH, 1)
    vel = (vel + 9) / 19  # range -9 to 10
    pipe_height = (pipe_height - height) / BASEY
    diff_in_pipe = diff_in_pipe / BASEY
    inputs = [dist, pipe_height, vel, diff_in_pipe]
    model.set_weights(current_pool[model_num])
    output_prob = model.predict([inputs])[0]
    return output_prob[0] > 0.75


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
    """

    :param save_video: boolean to save the simulation as video (for review), save to '../data/learning.mp4'
    :type save_video: bool
    :param log: boolean to save fitness history to log file at '../data/log.txt'
    :type log: bool
    """
    if log and not resume_previous:
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
        # random.seed(1234)  # use seed to make each run same, comment out for more randomness
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
            if log:
                with open(os.path.join('..', 'data', 'log.txt'), 'a') as f:
                    f.write('{}\n'.format(int(fitness[best_idx] * 1.2)))
            break
        else:
            showGameOverScreen(log)


def mainGame(movementInfo, save_video):
    """main simulation code"""
    global fitness
    global FPS
    if save_video:
        global proc
    playerIndex = loopIter = 0
    scores = [0] * total_models
    playerIndexGen = movementInfo['playerIndexGen']
    playersX = int(SCREENWIDTH * 0.2)
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

    next_pipe_x = lowerPipes[0]['x'] - (playersX + IMAGES['player'][0].get_width())
    next_pipe_hole_y = lowerPipes[0]['y']
    diff_in_pipe = lowerPipes[1]['y'] - lowerPipes[0]['y']

    pipeVelX = -4

    # player velocity, max velocity, downward accleration, accleration on flap
    playersVelY = [-9] * total_models  # player's velocity along Y, default same as playerFlapped
    playerMaxVelY = 10  # max vel along Y, max descend speed
    playersAccY = [1] * total_models  # players downward accleration
    playerFlapAcc = -9  # players speed on flapping
    playersFlapped = [False] * total_models  # True when player flaps
    playerIsAlive = [True] * total_models  # True if player is still alive
    playerRot = [45] * total_models  # player's rotation
    playerVelRot = 3  # angular speed
    playerRotThr = 20  # rotation threshold

    alive_players = total_models

    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_UP:
                if FPS < 1000:
                    FPS *= 2
            if event.type == KEYDOWN and event.key == K_DOWN:
                if FPS > 1:
                    FPS = max(FPS / 2, 1)
        # check if player is off screen
        for idxPlayer in range(total_models):
            if playersYList[idxPlayer] < 0 and playerIsAlive[idxPlayer]:
                alive_players -= 1
                playerIsAlive[idxPlayer] = False
                fitness[idxPlayer] = 1  # penalize for going off screen
        if alive_players == 0:
            return
        for idxPlayer in range(total_models):
            if playerIsAlive[idxPlayer]:
                fitness[idxPlayer] += 1  # reward for staying alive
        for idxPlayer in range(total_models):
            if playerIsAlive[idxPlayer]:
                if predict_jump(playersYList[idxPlayer], next_pipe_x, next_pipe_hole_y, playersVelY[idxPlayer],
                                diff_in_pipe, idxPlayer):  # predict jump or not for each model
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
        crashTest = checkCrash({'x': playersX, 'y': playersYList, 'index': playerIndex}, playerIsAlive,
                               upperPipes, lowerPipes)

        for idx in range(total_models):
            if playerIsAlive[idx] and crashTest[idx] == 1:  # hit pipe
                if alive_players >= total_models // 2:
                    if scores[idx] > 0:
                        fitness[idx] = fitness[idx] // 2  # penalize for dying first
                    else:
                        fitness[idx] = 1
                # if alive_players == 1 and fitness[idx] > 150:
                #     fitness[idx] = int(fitness[idx] * 1.2)  # reward for being the last man standing
                alive_players -= 1
                playerIsAlive[idx] = False
            elif playerIsAlive[idx] and crashTest[idx] == 0:  # hit ground
                alive_players -= 1
                playerIsAlive[idx] = False
                fitness[idx] = 1  # penalize for hitting ground

        if alive_players == 0:
            return

        # check for score
        for idx in range(total_models):
            if playerIsAlive[idx]:
                playerMidPos = playersX
                for pipe_idx in range(len(upperPipes)):
                    pipeMidPos = upperPipes[pipe_idx]['x'] + IMAGES['pipe'][0].get_width()
                    if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                        next_pipe_x = lowerPipes[pipe_idx + 1]['x'] - (playersX + IMAGES['player'][0].get_width())
                        next_pipe_hole_y = lowerPipes[pipe_idx + 1]['y']
                        diff_in_pipe = lowerPipes[pipe_idx + 2]['y'] - lowerPipes[pipe_idx + 1]['y']
                        scores[idx] += 1  # reward for surviving
                        if scores[idx] >= MAX_SCORE:
                            return idx
                        fitness[idx] += 50  # reward for passing pipes
                        # SOUNDS['point'].play()

        # playerIndex basex change
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # rotate the player
        for idx in range(total_models):
            if playerIsAlive[idx]:
                if playerRot[idx] > -90:
                    playerRot[idx] -= playerVelRot

        # player's movement
        for idx in range(total_models):
            if playerIsAlive[idx]:
                if playersVelY[idx] < playerMaxVelY and not playersFlapped[idx]:
                    playersVelY[idx] += playersAccY[idx]
                if playersFlapped[idx]:
                    # more rotation to cover the threshold (calculated in visible rotation)
                    playerRot[idx] = 45
                    playersFlapped[idx] = False
                playerHeight = IMAGES['player'][playerIndex].get_height()
                playersYList[idx] += min(playersVelY[idx], BASEY - playersYList[idx] - playerHeight)

        # move pipes to left
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX
        next_pipe_x += pipeVelX

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

        # Player rotation has a threshold
        for idx in range(total_models):
            if playerIsAlive[idx]:
                visibleRot = playerRotThr
                if playerRot[idx] <= playerRotThr:
                    visibleRot = playerRot[idx]
                playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)
                SCREEN.blit(playerSurface, (playersX, playersYList[idx]))

        showInfo(sum(playerIsAlive))
        pygame.display.update()
        if save_video:
            img = Image.frombytes('RGB', SCREEN.get_size(), pygame.image.tostring(SCREEN, 'RGB', False))
            img.save(proc.stdin, 'JPEG')

        FPSCLOCK.tick(FPS)


def showGameOverScreen(log):
    """crossover and mutation logic"""
    global current_pool
    global fitness
    global generation
    global previous_best
    global previous_best, best_idx_so_far, local_minima_stuck_time

    # random.seed(time.time())
    new_weights = []
    best_fit = max(fitness)
    if log:
        with open(os.path.join('..', 'data', 'log.txt'), 'a') as f:
            f.write('{}\n'.format(best_fit))
    if best_fit > previous_best:
        previous_best = best_fit
        best_idx_so_far = fitness.index(best_fit)
        local_minima_stuck_time = 0
        with open(os.path.join('..', 'data', 'best_weight_so_far.pickle'), 'wb') as f:
            pickle.dump(current_pool[best_idx_so_far], f)
    else:
        local_minima_stuck_time += 1

    mrate = 0.1 if previous_best < 500 else 0.05  # increase mutation rate if stuck
    mrate = min(local_minima_stuck_time / 100, 0.25) if local_minima_stuck_time > 10 else mrate
    # roulette wheel selection
    max_fit = sum(fitness)
    sel_prob = [fit / max_fit for fit in fitness]
    sorted_idx = np.argsort(fitness)
    while len(new_weights) < int(total_models / 5 * 4):
        # idx1 = random.choice([sorted_idx[-1], sorted_idx[-2]])  # force one of parent to be elite
        idx1 = np.random.choice(total_models, p=sel_prob)
        idx2 = np.random.choice(total_models, p=sel_prob)
        if idx1 != idx2:
            new_weights1 = crossover(idx1, idx2, )
            new_weights.append(new_weights1)
    current_pool = np.array(current_pool)[sorted_idx].tolist()

    # eliminate bad genes
    for idx in range(len(new_weights)):
        current_pool[idx] = new_weights[idx]

    # mutate weights
    for idx in range(total_models):
        fitness[idx] = -1
        if idx < total_models - 1:  # elitism, keep and don't mutate top gene
            current_pool[idx] = mutate(current_pool[idx], mrate)
        else:
            with open(os.path.join('..', 'data', 'best_weight_so_far.pickle'), 'rb') as f:
                current_pool[idx] = pickle.load(f)

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
    """show genetic algo info on pygame screen"""
    fsize = 10
    default_font = pygame.font.get_default_font()
    font_renderer = pygame.font.Font(default_font, fsize)

    # To create a surface containing `Some Text`
    lines = ["Generation: {}".format(generation), "Previous Best: {}".format(previous_best),
             "Current Best: {}".format(max(fitness)), "Current Alive: {}".format(alive_count)]
    for i, l in enumerate(lines):
        label = font_renderer.render(l, True, (255, 255, 255))
        SCREEN.blit(label, (5, SCREENHEIGHT - 5 - fsize * (i + 1)))
    fps = FPSCLOCK.get_fps()
    SCREEN.blit(font_renderer.render(str(int(fps)), True, (255, 255, 255)),
                (SCREENWIDTH - 5 - 2 * fsize, SCREENHEIGHT - 5 - fsize))


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
        playerRect = pygame.Rect(players['x'], players['y'][idx],
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
    main(save_video=False)

    with open(os.path.join('..', 'data', 'log.txt'), 'r') as f:
        lines = f.read()
    data = list(map(int, lines.strip().split('\n')[1:]))
    plt.figure(figsize=(8, 8))
    plt.plot(data)
    p = np.polyfit(list(range(len(data))), data, 3)
    py = np.poly1d(p)(list(range(len(data))))
    plt.plot(py, 'r--')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.savefig(os.path.join('..', 'data', 'fitness.png'))
    plt.show()
