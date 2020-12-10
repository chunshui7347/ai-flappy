# Generating Content: Maze Generation

For this assignment, go through the Unity 3D maze generation [tutorial](http://catlikecoding.com/unity/tutorials/maze/) by [Catlike Coding](http://catlikecoding.com/).

Apply a constructive PCG method to generate mazes in Unity.
* Hint: Get inspired by the set of constructive approaches described and visualised in this [blogpost](http://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap.html) and this [demo](http://jamisbuck.org/mazes/minecraft.html) by Jamis Buck.

Evaluate the generators using one or more of the methods covered in Section 4.6 and compare their performance.

* Hint: Try out expressivity analysis as a first step in your evaluation. Then, if time allows, involve actual players and ask for their feedback.
* Hint: How should you represent a maze? Directly as tiles or indirectly as rooms or corridors? What should a fitness function look like? The distance from start to exit, the complexity of the maze expressed as branching corridors, or some form of spatial navigation engagement function? Play with different fitness function designs, observe the generated mazes.