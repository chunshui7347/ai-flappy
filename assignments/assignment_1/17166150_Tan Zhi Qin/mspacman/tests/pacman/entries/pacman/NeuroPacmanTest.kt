package pacman.entries.pacman

import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import pacman.entries.pacman.neat.NeuralNetwork

internal class NeuroPacmanTest {
    @Test
    fun badBrainArgument() {
        assertThrows<IllegalArgumentException> {
            NeuroPacman(NeuralNetwork(1, 1, 1, 1))
        }
    }
}