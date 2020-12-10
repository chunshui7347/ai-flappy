package pacman.entries.pacman

import pacman.controllers.Controller
import pacman.game.Constants.GHOST
import pacman.game.Constants.MOVE
import pacman.game.Game
import java.util.*

class MinimaxPacman(private val ghostController: Controller<EnumMap<GHOST, MOVE>>, private val maxDepth: Int = 1) : Controller<MOVE>() {

    private fun evaluateScore(game: Game): Int {
        val score = game.score

        var distanceToNearestGhost = Int.MAX_VALUE
        var nearestGhostEdibleTime = 0
        for (ghost in GHOST.values()) {
            val ghostIndex = game.getGhostCurrentNodeIndex(ghost);
            val ghostDistance = game.getShortestPathDistance(game.pacmanCurrentNodeIndex, ghostIndex)
            val ghostEdibleTime = game.getGhostEdibleTime(ghost)

            if (ghostDistance < distanceToNearestGhost) {
                distanceToNearestGhost = ghostDistance
                nearestGhostEdibleTime = ghostEdibleTime
            }
        }

        return if (distanceToNearestGhost < 30 && nearestGhostEdibleTime == 0) {
            score - distanceToNearestGhost
        } else {
            score + distanceToNearestGhost
        }
    }

    private fun minimax(move: MOVE?, depth: Int, game: Game): Int {
        if (game.gameOver() || depth == maxDepth)
            return evaluateScore(game)

        return if (move == null) {
            var maxScore: Int = Int.MIN_VALUE
            for (i in moves.indices) {
                val currentScore = minimax(moves[i], depth + 1, game)
                maxScore = arrayOf(currentScore, maxScore).maxOrNull()!!
            }
            maxScore
        } else {
            val copy = game.copy()
            for (mm in 0 until 10)
                copy.advanceGame(move, ghostController.getMove(copy, -1))

            minimax(null, depth, copy)
        }
    }


    override fun getMove(game: Game, timeDue: Long): MOVE {
        val scores = Array(moves.size) { Int.MIN_VALUE }
        for (i in moves.indices) {
            val copy = game.copy()

            for (mm in 0 until 10)
                copy.advanceGame(moves[i], ghostController.getMove(copy, -1))

            // only if we can move
            if (copy.pacmanCurrentNodeIndex != game.pacmanCurrentNodeIndex)
                scores[i] = minimax(null, 0, copy)
        }

        val maxScore = scores.maxOrNull()!!;

        // return max score
        return moves[scores.indexOf(maxScore)]
    }

    companion object {
        private val moves = arrayOf(MOVE.UP, MOVE.RIGHT, MOVE.DOWN, MOVE.LEFT)
    }
}