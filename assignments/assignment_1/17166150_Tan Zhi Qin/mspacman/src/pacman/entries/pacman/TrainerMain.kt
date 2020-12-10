package pacman.entries.pacman

import pacman.controllers.examples.Legacy2TheReckoning
import pacman.entries.pacman.neat.CustomExecutor
import pacman.entries.pacman.neat.GeneticEvolutionator
import kotlin.random.Random

var printing = false

fun main() {
    val geneticEvolutionator = GeneticEvolutionator(100)
    while (geneticEvolutionator.generation < 200) {
        geneticEvolutionator.fit()
        println("generation: ${geneticEvolutionator.generation}, best ${geneticEvolutionator.bestFitness}")
        geneticEvolutionator.generateNextGeneration()
    }
    println(geneticEvolutionator.bestGene)

    printing = true

    // show the best
    val executor = CustomExecutor()
    executor.runGame(NeuroPacman(geneticEvolutionator.bestGene), Legacy2TheReckoning(), true, 10)
}

