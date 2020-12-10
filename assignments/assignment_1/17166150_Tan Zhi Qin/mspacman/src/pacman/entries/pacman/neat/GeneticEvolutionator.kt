package pacman.entries.pacman.neat

import pacman.controllers.examples.Legacy2TheReckoning
import pacman.controllers.examples.StarterGhosts
import pacman.entries.pacman.NeuroPacman
import kotlin.random.Random

class GeneticEvolutionator(val populationSize: Int = 50) {
    val currentGenes: ArrayList<NeuralNetwork> = ArrayList(populationSize)
    var generation: Int = 0
        private set
    var fitted = false
        private set
    val fitnessValues = Array(populationSize) { 0.0 }
    private val executor = CustomExecutor()

    val bestFitness: Double
        get() {
            if (!fitted)
                fit()

            return fitnessValues.maxOrNull() ?: 0.0
        }

    val bestGene: NeuralNetwork
        get() {
            if (!fitted)
                fit()

            return currentGenes[fitnessValues.maxIndex()]
        }

    init {
        // create random population
        for (i in 0 until populationSize)
            currentGenes.add(NeuralNetwork(NeuroPacman.INPUT_LEN, NeuroPacman.HIDDEN1_LEN, NeuroPacman.HIDDEN2_LEN, NeuroPacman.OUTPUT_LEN))
    }

    fun fit(force: Boolean = false) {
        if (!force && fitted)
            throw AlreadyFittedException()

        System.arraycopy(computeFitness(), 0, fitnessValues, 0, populationSize)

        fitted = true
    }

    private fun computeFitness(): Array<Double> {
        return executor.runExperimentForAll(Array(populationSize) { i -> NeuroPacman(currentGenes[i]) }, StarterGhosts(), 10)
    }

    fun generateNextGeneration() {
        if (!fitted)
            fit()

        // normalize
        val sumFitness = fitnessValues.sum()
        for (i in fitnessValues.indices)
            fitnessValues[i] /= sumFitness

//        val sortedFitness = fitnessValues.mapIndexed {a, b -> Pair(a, b)}.sortedByDescending { it.second }
//        val p1 = currentGenes[sortedFitness[0].first]
//        val p2 = currentGenes[sortedFitness[1].first]

        val genesCopy = currentGenes.toList()
        for (i in 0 until currentGenes.size) {
            val i1 = roulettePicker(fitnessValues)
            val i2 = roulettePicker(fitnessValues)
            val p1 = genesCopy[i1]
            val p2 = genesCopy[i2]
            currentGenes[i] = NeuralNetwork(p1)
            currentGenes[i].cross(p2)
            currentGenes[i].mutate(MUTATION_RATE)
        }

        generation++
        fitted = false
    }

    companion object {
        const val MUTATION_RATE: Double = 0.15

        private fun roulettePicker(percentages: Array<Double>): Int {
            var index = 0
            var r = Random.nextDouble()
            while (r > 0) {
                r -= percentages[index]
                index++
            }
            if (index > 0)
                index--
            if (index >= percentages.size)
                throw ArithmeticException("Could not apply roulette wheel selection")

            return index
        }
    }
}

class AlreadyFittedException : Exception("The model is already fit")
