# PCG Maze Generation
The maze generation is implemented in Unity following [tutorial](https://catlikecoding.com/unity/tutorials/maze/) by Catlike Coding. The algorithm used to generate the maze is Growing Tree Algorithm. It is a very flexible algorithm as we can implement different types of algorithm by changing its cell selection method. 

## Maze Generation Algorithm
The maze is directly represented as cells or tiles. Each cell will have 4 walls or passages on each direction (North, West, South, East)
### Parameters:
1. Maze Size
    * Default size is 20 x 20 cells
    * We can specify custom maze size in `Size` `Maze` Prefab in Unity.
2. Cell Selection Method
    * We can visualize different type of cell selection method by specifying `Select Method` in the `Game Manager` GameObject in Unity. The maze generation recording for all cell selection method is [here](./pcg_maze_generation.mp4).


## Cell Selection Method
Following are the cell selection method implemented:
1. Newest (Recursive Backtracking)
2. Random (Prim's)
3. Middle
4. Oldest

We can observe that the ***newest*** method yield long winding paths with more dead ends while using ***random*** method, we get more junctions leading to different path.
For ***middle*** and ***oldest*** method, the maze generated will have long straight path which is not a very good maze as it is very easy to follow.

## Evaluation Methods
There are three methods to evaluate the maze generation algorithm
1. Total Dead Ends
    * More dead ends in the maze is generally better as the maze will be harder to complete
2. Shortest Distance to Exit
    * The player starting point is randomized each maze, while the exit is always at the edge
    * Shortest distance to from starting point to exit is determined with Dijkstra's algorithm
    * Longer distance to exit represents harder maze
3. Time Taken to Complete
    * Each maze is play tested by a tester, and the time taken to complete it is recorded
    * Longer time taken to complete means the maze generated is harder

## Evaluation Results
The PCG maze generation is evaluated with actual player. The results at the end of each game is saved as csv in [this](./Evaluation%20Results) folder.
Table below summarize the average of each selection method over a few runs:

| Cell Selection Method           | Total Dead Ends | Shortest Distance to Exit | Time Taken to Complete (s) |
|---------------------------------|----------------:|--------------------------:|---------------------------:|
| Newest (Recursive Backtracking) |       42 ± 2.77 |            **95 ± 61.77** |          **66.17 ± 37.35** |
| Random (Prim's)                 |  **125 ± 8.79** |             27.75 ±  7.79 |              24.75 ± 10.05 |
| Middle                          |    38.17 ± 5.64 |             24.83 ±  8.75 |              15.33 ±  4.42 |
| Oldest                          |    46.86 ± 9.08 |             26.14 ±  8.51 |              12.86 ±  4.26 |

## Unity Assets Used
For this project, I had used a few free assets from Unity Asset Store:
1. [Free HDR Sky](https://assetstore.unity.com/packages/2d/textures-materials/sky/free-hdr-sky-61217)
2. [Standard Assets (for Unity 2018.4)](https://assetstore.unity.com/packages/essentials/asset-packs/standard-assets-for-unity-2018-4-32351)

## References
1. https://catlikecoding.com/unity/tutorials/constructing-a-fractal/
2. http://weblog.jamisbuck.org/2011/1/27/maze-generation-growing-tree-algorithm
