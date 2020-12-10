package pacman.entries.pacman

import pacman.controllers.Controller
import pacman.entries.pacman.neat.NeuralNetwork
import pacman.entries.pacman.neat.maxIndex
import pacman.game.Constants.*
import pacman.game.Game

class NeuroPacman(private val brain: NeuralNetwork) : Controller<MOVE>() {

    init {
        if (brain.inputLen != INPUT_LEN || brain.hidden1Len != HIDDEN1_LEN || brain.hidden2Len != HIDDEN2_LEN || brain.outputLen != OUTPUT_LEN)
            throw IllegalArgumentException("The brain layers nodes numbers should be" +
                    " $INPUT_LEN, $HIDDEN1_LEN, $OUTPUT_LEN, got ${brain.inputLen}, ${brain.hidden1Len}, ${brain.outputLen}")
    }

    constructor() : this(NeuralNetwork(INPUT_LEN, HIDDEN1_LEN, HIDDEN2_LEN, OUTPUT_LEN))

    override fun getMove(game: Game?, timeDue: Long): MOVE {
        if (game == null)
            return MOVE.NEUTRAL
        // get inputs
        val inputs = Array(INPUT_LEN) { 0.0 }
        val maxIndex = game.numberOfNodes.toDouble()
        // pacman current position
        inputs[0] = game.pacmanCurrentNodeIndex.toDouble() / maxIndex
        val ghosts = GHOST.values()
        for (i in ghosts.indices) {
            // ghosts positions
//            inputs[i + 1] = game.getShortestPathDistance(game.pacmanCurrentNodeIndex, game.getGhostCurrentNodeIndex(ghosts[i])).toDouble() / maxIndex
            inputs[i + 1] = game.getGhostCurrentNodeIndex(ghosts[i]).toDouble() / maxIndex
            // ghosts edible time
            inputs[i + 5] = if (game.getGhostEdibleTime(ghosts[i]) > 0) 1.0 else 0.0
            // ghosts lair time
            // inputs[i + 9] = game.getGhostLairTime(ghosts[i]).toDouble() / 100.0 // max lair time
        }
        // closest pill position
        val closestPill =
                game.getClosestNodeIndexFromNodeIndex(game.pacmanCurrentNodeIndex, game.activePillsIndices, DM.PATH)
//        inputs[13] = if (closestPill != -1) game.getShortestPathDistance(game.pacmanCurrentNodeIndex, closestPill, game.pacmanLastMoveMade).toDouble() / maxIndex else 0.0
        inputs[13] = closestPill.toDouble() / maxIndex

        // closest power pill position
        val closestPowerPill =
                game.getClosestNodeIndexFromNodeIndex(game.pacmanCurrentNodeIndex, game.activePowerPillsIndices, DM.PATH)
//        inputs[14] = if (closestPowerPill != -1) game.getShortestPathDistance(game.pacmanCurrentNodeIndex, closestPowerPill, game.pacmanLastMoveMade).toDouble() / maxIndex else 0.0
        inputs[14] = closestPowerPill.toDouble() / maxIndex

        // are we in junction
        inputs[15] = if (game.isJunction(game.pacmanCurrentNodeIndex)) 1.0 else 0.0

        inputs[16] = game.pacmanLastMoveMade.ordinal.toDouble() / 5.0

        val outputs = brain.predict(inputs)
        if (printing) {
            println(outputs.contentToString())
            println(validMoves[outputs.maxIndex()])
        }

        return validMoves[outputs.maxIndex()]
    }

    companion object {
        const val INPUT_LEN: Int = 1 + 3 * 4 + 4
        const val HIDDEN1_LEN: Int = 16
        const val HIDDEN2_LEN: Int = 16
        const val OUTPUT_LEN: Int = 4 // number of moves

        private val validMoves = arrayOf(MOVE.LEFT, MOVE.RIGHT, MOVE.UP, MOVE.DOWN)
    }
}