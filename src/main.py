import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygad.kerasga
from src.util import make_model, visualize
from src.forward_model import forward


def fitness_func(solution, sol_idx):
    global keras_ga, model

    model_weights_matrix = pygad.kerasga.model_weights_as_matrix(model=model,
                                                                 weights_vector=solution)

    model.set_weights(weights=model_weights_matrix)
    score, travelled = forward(model)

    return score + 0.5 * travelled


def callback_generation(ga_instance):
    global last_fitness, keras_ga

    keras_ga.population_weights = ga_instance.population

    print("Generation = {generation}".format(generation=ga_instance.generations_completed), end='\t')
    print("Fitness    = {fitness}".format(fitness=ga_instance.best_solution()[1]))


if __name__ == '__main__':
    print('creating keras model')
    model = make_model()
    model.summary()
    weights_vector = pygad.kerasga.model_weights_as_vector(model=model)

    # Create an instance of the pygad.kerasga.KerasGA class to build the initial population.
    keras_ga = pygad.kerasga.KerasGA(model=model,
                                     num_solutions=10)

    # Prepare the PyGAD parameters. Check the documentation for more information:
    # https://pygad.readthedocs.io/en/latest/README_pygad_ReadTheDocs.html#pygad-ga-class
    num_generations = 250  # Number of generations.
    num_parents_mating = 5  # Number of solutions to be selected as parents in the mating pool.
    initial_population = keras_ga.population_weights  # Initial population of network weights.
    parent_selection_type = "sss"  # Type of parent selection.
    crossover_type = "single_point"  # Type of the crossover operator.
    mutation_type = "random"  # Type of the mutation operator.
    mutation_percent_genes = 15  # Percentage of genes to mutate.
    # This parameter has no action if the parameter mutation_num_genes exists.
    keep_parents = -1  # Number of parents to keep in the next population.
    # -1 means keep all parents and 0 means keep nothing.

    # Create an instance of the pygad.GA class
    ga_instance = pygad.GA(num_generations=num_generations,
                           num_parents_mating=num_parents_mating,
                           initial_population=initial_population,
                           fitness_func=fitness_func,
                           parent_selection_type=parent_selection_type,
                           crossover_type=crossover_type,
                           mutation_type=mutation_type,
                           mutation_percent_genes=mutation_percent_genes,
                           keep_parents=keep_parents,
                           on_generation=callback_generation)

    # Start the genetic algorithm evolution.
    print('running genetic algorithm for {} generations'.format(num_generations))
    ga_instance.run()

    # After the generations complete, some plots are showed that
    # summarize how the outputs/fitness values evolve over generations.
    ga_instance.plot_result(title="Iteration vs. Fitness", linewidth=4)

    # Returning the details of the best solution.
    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    print("Index of the best solution : {solution_idx}".format(solution_idx=solution_idx))

    # Fetch the parameters of the best solution.
    best_solution_weights = pygad.kerasga.model_weights_as_matrix(model=model,
                                                                  weights_vector=solution)
    model.set_weights(best_solution_weights)

    visualize(model)
    model.save('best_model.h5')
