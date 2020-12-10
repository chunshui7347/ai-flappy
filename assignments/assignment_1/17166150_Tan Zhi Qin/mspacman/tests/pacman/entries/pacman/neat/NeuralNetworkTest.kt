package pacman.entries.pacman.neat

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class NeuralNetworkTest {

    private lateinit var nn: NeuralNetwork
    private lateinit var input: Array<Double>

    @BeforeEach
    fun setup() {
        nn = NeuralNetwork(12, 8, 10, 4)
        input = arrayOf(1.0, 2.0, 5.0, 7.8, 9.88, 23.9, 2.0, 1.0, 23.0, 4.0, 3.0, 8.99)
    }

    /*
     * Tests that the matrix multiplication inside predict and matrix generation
     */
    @Test
    fun inputAndOutputSizes() {
        assertEquals(nn.predict(input).size, 4)
    }

    @Test
    fun copy() {
        val nnCopy = NeuralNetwork(nn)
        assertArrayEquals(nn.predict(input), nnCopy.predict(input))
    }

    /*
     * this test actually might fail if the random is so bad, but very low chance
     */
    @Test
    fun random() {
        val newNN = NeuralNetwork(12, 8, 10, 4)
        assertFalse(nn.predict(input).contentEquals(newNN.predict(input)))
    }

    @Test
    fun mutateHighRate() {
        val newNN = NeuralNetwork(nn)
        newNN.mutate(0.9)
        assertFalse(nn.predict(input).contentEquals(newNN.predict(input)))
    }

    @Test
    fun mutateZero() {
        val newNN = NeuralNetwork(nn)
        newNN.mutate(0.0)
        assertArrayEquals(nn.predict(input), newNN.predict(input))
    }

    @Test
    fun mutateArgumentOutOfRange() {
        val newNN = NeuralNetwork(nn)
        org.junit.jupiter.api.assertThrows<IllegalArgumentException> { newNN.mutate(-0.1) }
        org.junit.jupiter.api.assertThrows<IllegalArgumentException> { newNN.mutate(1.1) }
    }
}