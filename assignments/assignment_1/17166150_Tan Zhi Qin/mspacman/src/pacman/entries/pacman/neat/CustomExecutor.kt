package pacman.entries.pacman.neat

import kotlinx.coroutines.ExecutorCoroutineDispatcher
import kotlinx.coroutines.async
import kotlinx.coroutines.newFixedThreadPoolContext
import kotlinx.coroutines.runBlocking
import pacman.controllers.Controller
import pacman.game.Constants.*
import pacman.game.Game
import pacman.game.GameView
import java.util.*
import kotlin.random.Random

/**
 * Check [pacman.Executor], this is addition to it with some kotlin coroutine stuff to make experimenting faster
 */
class CustomExecutor constructor
(private val dispatcher: ExecutorCoroutineDispatcher = newFixedThreadPoolContext(4, "CustomExecutorDispatcher")) {
    fun runExperiment(pacManController: Controller<MOVE>, ghostController: Controller<EnumMap<GHOST, MOVE>>, trials: Int): Double {
        var sumScores = 0.0
        var game: Game
        var iterationsWithoutChange: Int
        var lastIndex = 0
        var addition: Double

        for (i in 0 until trials) {
            game = Game(Random.nextLong())
            iterationsWithoutChange = 0
            addition = 0.0
            while (!game.gameOver()) {
                game.advanceGame(pacManController.getMove(game.copy(), -1),
                        ghostController.getMove(game.copy(), -1))

//                if (game.pacmanCurrentNodeIndex == lastIndex)
//                    iterationsWithoutChange++
//                else
//                    lastIndex = game.pacmanCurrentNodeIndex
//
//                if (iterationsWithoutChange > 500) {
//                    // addition = -(LEVEL_LIMIT.toDouble() - game.currentLevelTime.toDouble()) / 2.0
//                    // addition = game.score.toDouble() * -1
//                    break
//                }
            }

            sumScores += game.score.toDouble() + addition
        }

        return sumScores / trials
    }

    fun runExperimentForAll(pacManController: Array<Controller<MOVE>>, ghostController: Controller<EnumMap<GHOST, MOVE>>, trails: Int): Array<Double> =
            runBlocking(dispatcher) {
                val jobs = pacManController.mapIndexed { _, controller ->
                    async {
                        runExperiment(controller, ghostController, trails)
                    }
                }
                jobs.map { it.await() }.toTypedArray()
            }

    fun runGame(pacManController: Controller<MOVE>, ghostController: Controller<EnumMap<GHOST, MOVE>>, visual: Boolean, delay: Int) {
        val game = Game(Random.nextLong())
        var gv: GameView? = null
        if (visual) gv = GameView(game).showGame()
        while (!game.gameOver()) {
            game.advanceGame(pacManController.getMove(game.copy(), -1), ghostController.getMove(game.copy(), -1))
            try {
                Thread.sleep(delay.toLong())
            } catch (e: Exception) {
            }
            if (visual) gv!!.repaint()
        }
    }
}