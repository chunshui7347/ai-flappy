# Heuristic Analysis (Game Playing Agent for Isolation)

### An Adversarial Game Playing Agent for Isolation

Students will form into groups and write a custom heuristic that will be used by the minimax/alpha-beta tree search algorithm.

1) You can write your heuristic function in game_agent.py,

2) Include the function in a custom player agent and add it to the list of test agents in tournament.py

    ``test_agents = [Agent(CustomPlayer(score_fn=improved_score, **CUSTOM_ARGS), "ID_Improved"),
                Agent(CustomPlayer(score_fn=aggressive_heuristic, **CUSTOM_ARGS), "Student1"),
                Agent(CustomPlayer(score_fn=defensive_heuristic, **CUSTOM_ARGS), "Student2"),
                Agent(CustomPlayer(score_fn=maximizing_win_chances_heuristic, **CUSTOM_ARGS), "Student3"),
                Agent(CustomPlayer(score_fn=minimizing_losing_chances_heuristic, **CUSTOM_ARGS), "Student4"),
                Agent(CustomPlayer(score_fn=chances_heuristic, **CUSTOM_ARGS), "Student5"),
                Agent(CustomPlayer(score_fn=weighted_chances_heuristic, **CUSTOM_ARGS), "Student6"),
                Agent(CustomPlayer(score_fn=weighted_chances_heuristic_2, **CUSTOM_ARGS), "Student7"),
	            Agent(CustomPlayer(score_fn=my_heuristic_function, **CUSTOM_ARGS), "GROUP_1")]``

    Optionally, you may create your own custom arguments to be used together with your heuristic function by defining your arguments such as 

    `CUSTOM_ARGS = {"method": 'alphabeta', 'iterative': True}`
   
3) Evaluate your agent score against the standard opponents by running the tournament.py

4) You can also compare your agent performance against the default baseline ID_Improved

5) Submit your code through spectrum and your agent will compete with the other group agent

** Download the Isolation game [here](https://github.com/sumitbinnani/AIND-Isolation) 