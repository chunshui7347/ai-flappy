package pacman.entries.pacman.neat

import kotlin.math.exp
import kotlin.math.max
import kotlin.math.min
import kotlin.math.tanh
import kotlin.random.Random

class NeuralNetwork {
    val inputLen: Int
    val hidden1Len: Int
    val hidden2Len: Int
    val outputLen: Int

    private val inputHidden1Weights: Matrix
    private val hidden1Hidden2Weights: Matrix
    private val hidden2OutputWeights: Matrix
    private val hidden1Biases: Matrix
    private val hidden2Biases: Matrix
    private val outputBiases: Matrix

    constructor(_input_len: Int, _hidden1_len: Int, _hidden2_len: Int, _output_len: Int) {
        inputLen = _input_len
        hidden1Len = _hidden1_len
        hidden2Len = _hidden2_len
        outputLen = _output_len
        inputHidden1Weights = Matrix(inputLen, hidden1Len) { _, _ -> rand() }
        hidden1Hidden2Weights = Matrix(hidden1Len, hidden2Len) { _, _ -> rand() }
        hidden2OutputWeights = Matrix(hidden2Len, outputLen) { _, _ -> rand() }
        hidden1Biases = Matrix(1, hidden1Len) { _, _ -> rand() }
        hidden2Biases = Matrix(1, hidden2Len) { _, _ -> rand() }
        outputBiases = Matrix(1, outputLen) { _, _ -> rand() }
    }

    constructor(nn: NeuralNetwork) {
        inputLen = nn.inputLen
        hidden1Len = nn.hidden1Len
        hidden2Len = nn.hidden2Len
        outputLen = nn.outputLen
        inputHidden1Weights = Matrix(nn.inputHidden1Weights)
        hidden1Hidden2Weights = Matrix(nn.hidden1Hidden2Weights)
        hidden2OutputWeights = Matrix(nn.hidden2OutputWeights)
        hidden1Biases = Matrix(nn.hidden1Biases)
        hidden2Biases = Matrix(nn.hidden2Biases)
        outputBiases = Matrix(nn.outputBiases)
    }

    private fun sigmoid(x: Double): Double {
        return 1 / (1 + exp(-5 * x))
    }

    private fun relu(x: Double): Double {
        return max(0.0, x)
    }

    /**
     * run feed forward on this neural network, the activation function is [tanh]
     */
    fun predict(inputs: Array<Double>): Array<Double> {
        if (inputs.size != inputLen)
            throw IllegalArgumentException("inputs size must be $inputLen elements")

        val inputMatrix = Matrix(inputs)
        val hidden1 = (inputMatrix * inputHidden1Weights)
        hidden1 += hidden1Biases
        hidden1.map(::tanh)

        val hidden2 = (hidden1 * hidden1Hidden2Weights)
        hidden2 += hidden2Biases
        hidden2.map(::tanh)

        val outputs = (hidden2 * hidden2OutputWeights)
        outputs += outputBiases
        outputs.map(::tanh)

        if (outputs.rows > 1)
            throw IllegalArgumentException("output did not result in an array")

        return outputs[0]
    }

    fun mutate(rate: Double) {
        if (rate > 1.0 || rate < 0)
            throw IllegalArgumentException("rate must be between 0 and 1")

//        inputHiddenWeights.map { a -> a + if (Random.nextDouble() < rate) r.nextGaussian() else 0.0 }
//        hiddenOutputWeights.map { a -> a + if (Random.nextDouble() < rate) r.nextGaussian() else 0.0 }
//        hiddenBiases.map { a -> a + if (Random.nextDouble() < rate) r.nextGaussian() else 0.0 }
//        outputBiases.map { a -> a + if (Random.nextDouble() < rate) r.nextGaussian() else 0.0 }

        inputHidden1Weights.map { a -> if (Random.nextDouble() < rate) rand() else a }
        hidden1Hidden2Weights.map { a -> if (Random.nextDouble() < rate) rand() else a }
        hidden2OutputWeights.map { a -> if (Random.nextDouble() < rate) rand() else a }
        hidden1Biases.map { a -> if (Random.nextDouble() < rate) rand() else a }
        outputBiases.map { a -> if (Random.nextDouble() < rate) rand() else a }
    }

    // TODO: test
    fun cross(other: NeuralNetwork) {
        val midInputHidden1W = Random.nextInt(min(inputLen, other.inputLen))
        val minHidden1 = min(hidden1Len, other.hidden1Len)
        val minHidden2 = min(hidden2Len, other.hidden2Len)
        val midHidden1Hidden2W = Random.nextInt(minHidden1)
        val midHidden2OutputW = Random.nextInt(minHidden2)
        val midHidden1B = Random.nextInt(minHidden1)
        val midHidden2B = Random.nextInt(minHidden2)
        val midOutputB = Random.nextInt(min(outputLen, other.outputLen))

        // weights cross might not be the best? but I guess its ok
        // we are crossing with rows, so the whole row will be copied and not individual values
        for (i in 0 until inputHidden1Weights.rows)
            if (i > midInputHidden1W)
                inputHidden1Weights[i] = other.inputHidden1Weights[i].copyOf()

        for (i in 0 until hidden1Hidden2Weights.rows)
            if (i > midHidden1Hidden2W)
                hidden1Hidden2Weights[i] = other.hidden1Hidden2Weights[i].copyOf()

        for (i in 0 until hidden2OutputWeights.rows)
            if (i > midHidden2OutputW)
                hidden2OutputWeights[i] = other.hidden2OutputWeights[i].copyOf()

        for (i in 0 until hidden1Len)
            if (i > midHidden1B)
                hidden1Biases[0, i] = other.hidden1Biases[0, i]

        for (i in 0 until hidden2Len)
            if (i > midHidden2B)
                hidden2Biases[0, i] = other.hidden2Biases[0, i]

        for (i in 0 until outputLen)
            if (i > midOutputB)
                outputBiases[0, i] = other.outputBiases[0, i]
    }

    override fun toString(): String {
        return "NeuralNetwork(inputLen=$inputLen, hidden1Len=$hidden1Len, hidden2Len=$hidden2Len, outputLen=$outputLen,\ninputHidden1Weights=\n$inputHidden1Weights,\nhidden1Hidden2Weights=\n$hidden1Hidden2Weights,\nhidden2OutputWeights=\n$hidden2OutputWeights,\nhidden1Biases=\n$hidden1Biases,\n" +
                "hidden2Biases=\n" +
                "$hidden2Biases\noutputBiases=\n$outputBiases)"
    }


    companion object {
        private fun rand(): Double {
            return Random.nextDouble(-1.0, 1.0)
        }
    }
}