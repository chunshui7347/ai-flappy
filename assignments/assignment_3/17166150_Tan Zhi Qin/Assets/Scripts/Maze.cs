using UnityEngine;
using UnityEngine.UI;
using static System.Math;
using System.Collections;
using System.Collections.Generic;

public class Maze : MonoBehaviour
{

    public IntVector2 size;

    public MazeCell cellPrefab;

    public float generationStepDelay;

    public MazePassage passagePrefab;
    public MazeWall[] wallPrefabs;

    private MazeCell[,] cells;
    private IntVector2 exitCoordinate;
    private int shortestDistance;
    private int totalDeadEnds;

    public IntVector2 RandomCoordinates
    {
        get
        {
            return new IntVector2(Random.Range(0, size.x), Random.Range(0, size.z));
        }
    }

    public bool ContainsCoordinates(IntVector2 coordinate)
    {
        return coordinate.x >= 0 && coordinate.x < size.x && coordinate.z >= 0 && coordinate.z < size.z;
    }

    public MazeCell GetCell(IntVector2 coordinates)
    {
        return cells[coordinates.x, coordinates.z];
    }

    public IEnumerator Generate(SelectMethod selectMethod, IntVector2 startCoordinate, GameManager gm)
    {
        GameObject.Find("InfoText").transform.GetChild(0).GetComponent<Text>().text = "No info yet";
        WaitForSeconds delay = new WaitForSeconds(generationStepDelay);
        cells = new MazeCell[size.x, size.z];
        List<MazeCell> activeCells = new List<MazeCell>();
        firstStep(activeCells);
        while (activeCells.Count > 0)
        {
            yield return delay;
            nextSteps(activeCells, selectMethod);
        }
        CreateRandomExits();
        totalDeadEnds = GetTotalDeadEnds();
        DijkstraShortestDistanceToExit(startCoordinate);
        GameObject.Find("InfoText").transform.GetChild(0).GetComponent<Text>().text = string.Format("TotalDeadEnds: {0}\tShortestDistToExit: {1}", totalDeadEnds, shortestDistance);
        gm.ResetTime();
    }

    private void firstStep(List<MazeCell> activeCells)
    {
        activeCells.Add(CreateCell(RandomCoordinates));
    }

    private void nextSteps(List<MazeCell> activeCells, SelectMethod selectMethod)
    {
        int currentIndex = activeCells.Count - 1;
        if (selectMethod == SelectMethod.newestOrRecursiveBacktrack)
        {
            currentIndex = activeCells.Count - 1;
        }
        else if (selectMethod == SelectMethod.randomOrPrims)
        {
            currentIndex = Random.Range(0, activeCells.Count);
        }
        else if (selectMethod == SelectMethod.middle)
        {
            currentIndex = activeCells.Count / 2;
        }
        else if (selectMethod == SelectMethod.oldest)
        {
            currentIndex = 0;
        }
        MazeCell currentCell = activeCells[currentIndex];
        if (currentCell.IsFullyInitialized)
        {
            activeCells.RemoveAt(currentIndex);
            return;
        }
        MazeDirection direction = currentCell.RandomUninitializedDirection;
        IntVector2 coordinates = currentCell.coordinates + direction.ToIntVector2();
        if (ContainsCoordinates(coordinates))
        {
            MazeCell neighbor = GetCell(coordinates);
            if (neighbor == null)
            {
                neighbor = CreateCell(coordinates);
                CreatePassage(currentCell, neighbor, direction);
                activeCells.Add(neighbor);
            }
            else
            {
                CreateWall(currentCell, neighbor, direction);
            }
        }
        else
        {
            CreateWall(currentCell, null, direction);
        }
    }

    private MazeCell CreateCell(IntVector2 coordinates)
    {
        MazeCell newCell = Instantiate(cellPrefab) as MazeCell;
        cells[coordinates.x, coordinates.z] = newCell;
        newCell.coordinates = coordinates;
        newCell.name = "Maze Cell " + coordinates.x + ", " + coordinates.z;
        newCell.transform.parent = transform;
        newCell.transform.localPosition = new Vector3(coordinates.x - size.x * 0.5f + 0.5f, 0f, coordinates.z - size.z * 0.5f + 0.5f);
        return newCell;
    }

    private void CreatePassage(MazeCell cell, MazeCell otherCell, MazeDirection direction)
    {
        MazePassage passage = Instantiate(passagePrefab) as MazePassage;
        passage.Initialize(cell, otherCell, direction);
        passage = Instantiate(passagePrefab) as MazePassage;
        passage.Initialize(otherCell, cell, direction.GetOpposite());
    }

    private void CreateWall(MazeCell cell, MazeCell otherCell, MazeDirection direction)
    {
        MazeWall wall = Instantiate(wallPrefabs[Random.Range(0, wallPrefabs.Length)]) as MazeWall;
        wall.Initialize(cell, otherCell, direction);
        if (otherCell != null)
        {
            wall = Instantiate(wallPrefabs[Random.Range(0, wallPrefabs.Length)]) as MazeWall;
            wall.Initialize(otherCell, cell, direction.GetOpposite());
        }
    }

    private void CreateRandomExits()
    {
        int rand = Random.Range(0, MazeDirections.Count);
        if (rand == 0)
        {
            // left
            exitCoordinate = new IntVector2(0, Random.Range(0, size.z));
            Destroy(GetCell(exitCoordinate).GetEdge(MazeDirection.West).gameObject);
        }
        else if (rand == 1)
        {
            // top
            exitCoordinate = new IntVector2(Random.Range(0, size.x), size.z - 1);
            Destroy(GetCell(exitCoordinate).GetEdge(MazeDirection.North).gameObject);
        }
        else if (rand == 2)
        {
            // right
            exitCoordinate = new IntVector2(size.x - 1, Random.Range(0, size.z));
            Destroy(GetCell(exitCoordinate).GetEdge(MazeDirection.East).gameObject);
        }
        else
        {
            // bottom
            exitCoordinate = new IntVector2(Random.Range(0, size.x), 0);
            Destroy(GetCell(exitCoordinate).GetEdge(MazeDirection.South).gameObject);
        }
        GetCell(exitCoordinate).transform.GetChild(0).GetComponent<MeshRenderer>().material.SetColor("_Color", Color.blue);
    }

    public int GetTotalDeadEnds()
    {
        int totalDeadEnds = 0;
        for (int i = 0; i < size.x; i++)
        {
            for (int j = 0; j < size.z; j++)
            {
                if (cells[i, j].IsDeadEnd())
                {
                    totalDeadEnds += 1;
                }
            }
        }
        return totalDeadEnds;
    }

    private void DijkstraShortestDistanceToExit(IntVector2 startCoordinate)
    {
        shortestDistance = size.x * size.z;
        for (int i = 0; i < MazeDirections.Count; i++)
        {
            MazeDirection md = (MazeDirection)i;
            if (GetCell(startCoordinate).IsPath(md))
            {
                InnerDijkstraShortestDistanceToExit(startCoordinate + md.ToIntVector2(), 1, md);
            }
        }
    }

    private void InnerDijkstraShortestDistanceToExit(IntVector2 currCoordinate, int currDist, MazeDirection moveDirection)
    {
        if (GetCell(currCoordinate).IsDeadEnd() | currDist > shortestDistance)
        {
            return;
        }
        if (currCoordinate.Equals(exitCoordinate))
        {
            shortestDistance = Min(shortestDistance, currDist);
        }
        for (int i = 0; i < MazeDirections.Count; i++)
        {
            MazeDirection md = (MazeDirection)i;
            if (GetCell(currCoordinate).IsPath(md) & !moveDirection.GetOpposite().Equals(md))
            {
                InnerDijkstraShortestDistanceToExit(currCoordinate + md.ToIntVector2(), currDist + 1, md);
            }
        }
    }

    public int GetShortestDistance()
    {
        return shortestDistance;
    }
    public int GetFinalTotalDeadEnds()
    {
        return totalDeadEnds;
    }
}