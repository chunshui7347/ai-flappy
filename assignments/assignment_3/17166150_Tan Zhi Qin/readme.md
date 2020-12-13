# PCG Maze Generation
The maze generation is implemented in Unity following [tutorial](https://catlikecoding.com/unity/tutorials/maze/) by Catlike Coding. The algorithm used to generate the maze is Growing Tree Algorithm. It is a very flexible algorithm as we can implement different types of algorithm by changing its cell selection method. 

## Cell Selection Method
Following are the cell selection method implemented:
1. Newest (Recursive Backtracking)
2. Random (Prim's)
3. Middle
4. Oldest
We can observe that the "newest" method yield long winding paths with more dead ends while using "random" method, we get more junctions leading to different path.
For "middle" and "oldest" method, the maze generated will have long straight path which is not a very good maze as it is very easy to follow.

## Maze Generation Algorithm
You can visualize different type of cell selection method by specifying it in the GameManager GameObject in Unity. The maze generation recording for all cell selection method is [here](./pcg_maze_generation.mp4).

## Unity Assets Used
For this project, I had used a few free assets from Unity Asset Store:
1. [Free HDR Sky](https://assetstore.unity.com/packages/2d/textures-materials/sky/free-hdr-sky-61217)
2. [Standard Assets (for Unity 2018.4)](https://assetstore.unity.com/packages/essentials/asset-packs/standard-assets-for-unity-2018-4-32351)

## Evaluation Results
The PCG maze generation is evaluated with actual player. The results at the end of each game is saved as csv in [this](./Evaluation%20Results) folder.

## References
1. https://catlikecoding.com/unity/tutorials/constructing-a-fractal/
2. http://weblog.jamisbuck.org/2011/1/27/maze-generation-growing-tree-algorithm
