using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Maze : MonoBehaviour
{
    public int width;   // Along x axis
    public int height;  // Along z axis
    public bool pathVisible;
    [Range(0.1f, 0.7f)]
    public float exitCellDistance = 0.4f;

    private Cell[,] cells;
    private int[,] cellDistances;
    private List<Cell> activeCells = new List<Cell>();
    private Cell entryCell;
    private Cell exitCell;
    private int currentLength = 0;

    public Cell CellPrefab;
    public Transform wallPrefab;
    public Material entryCellMaterial;
    public Material exitCellMaterial;
    public Material defaultCellMaterial;
    public float delay;

    public void Awake()
    {
        cells = new Cell[width, height];
        cellDistances = new int[width, height];
    }

    public IEnumerator Generate()
    { 
        // Initialize the first cell as entry cell
        Cell currentCell = PlaceRandomEntryCell();
        currentLength++;
        cellDistances[currentCell.Location.x, currentCell.Location.z] = currentLength;
        activeCells.Add(currentCell);
        yield return new WaitForSeconds(delay);


        // Start connecting
        while (activeCells.Count > 0)
        {
            int index = activeCells.Count - 1;
            currentCell = activeCells[index];
            currentLength = cellDistances[currentCell.Location.x, currentCell.Location.z];
            currentCell.name += "_length=" + currentLength;

            Cell nextCell = MakeConnection(currentCell);
            if (nextCell != null)
            {
                currentLength++;
                cellDistances[nextCell.Location.x, nextCell.Location.z] = currentLength;
                activeCells.Add(nextCell);
                yield return new WaitForSeconds(delay);
            }
            else
            {
                // Set exit cell if it is an edge cell and last cell in the active cells list and not entry cell
                if (IsEdgeCell(currentCell) && exitCell == null && currentCell != entryCell && exitCellDistanceCriteriaMet(currentCell))
                {
                    SetExitCell(currentCell);
                }

                activeCells.Remove(currentCell);
            }
        }

        CreateCellWalls();

        print("Generate complete");
    }

    public IEnumerator GenerateBinarySearch() {

        //Loop from z axis
        for (int z = 0; z < height; z++)
        {
            //Loop from x axis
            for (int x = 0; x < width; x ++)
            {
                //Start from the 0,0
                CellLocation current_location = new CellLocation(x, z);
                Cell currentCell = PlaceCell(current_location);
                //Random To Bottom or To Right
                List<int> possibleDirections = new List<int>();
                if (x > 0) possibleDirections.Add(2);
                if (z > 0) possibleDirections.Add(1);

                //Set the starting and end point
                if (x == 0 && z == 0) {
                    currentCell.Material = entryCellMaterial;
                    entryCell = currentCell;
                } else if (x == height-1 && z == width-1) {
                    SetExitCell(currentCell);
                }

                //Make the maze
                if (possibleDirections.Count > 0) {
                    possibleDirections.Shuffle();
                    CellDirection direction = (CellDirection) possibleDirections[0];
                    CellDirection fromDirection = direction.GetOpposite();
                    CellLocation nextLocation = currentCell.Location + direction.ToRelativeCellLocation();

                    currentCell.AddConnection(direction); // Direction that connects it to the newly generated cell
                    currentCell.name += "_" + direction;
                    cells[nextLocation.x, nextLocation.z].AddConnection(fromDirection);
                }

                currentLength++;
                cellDistances[currentCell.Location.x, currentCell.Location.z] = currentLength;
                activeCells.Add(currentCell);
                yield return new WaitForSeconds(delay);
            }
        }

        CreateCellWalls();

        print("Generate complete");
    }

    private bool exitCellDistanceCriteriaMet(Cell cell)
    {
        float ratio = cellDistances[cell.Location.x, cell.Location.z] / (float)(width * height);
        bool met = ratio >= exitCellDistance;
        print(cell.name + ", ratio: " + ratio + ", met:" + met);
        return met;
    }

    public void CreateCellWalls()
    {
        for (int i = 0; i < width; i ++)
        {
            for (int j = 0; j < height; j++)
            {
                cells[i, j].CreateWalls();
            }
        }
    }

    public Cell PlaceRandomEntryCell()
    {
        // Generate four possible start cells along the edges of the maze into a list  
        List<CellLocation> possibleStartCells = new List<CellLocation>()
        {
            new CellLocation(UnityEngine.Random.Range(0, width), 0),
            new CellLocation(UnityEngine.Random.Range(0, width), height - 1),
            new CellLocation(0, UnityEngine.Random.Range(0, height)),
            new CellLocation(width - 1, UnityEngine.Random.Range(0, height)),
        };

        // Randomly get a possible start cell after shufflering the list elements
        possibleStartCells.Shuffle();
        CellLocation location = possibleStartCells[0];
        Cell cell = PlaceCell(location);
        cell.Material = entryCellMaterial;
        entryCell = cell;
        return cell;      
    }

    public CellDirection GetDirectionThatLeadstoOutOfBound(Cell edgeCell)
    {
        if (!edgeCell)
        {
            throw new Exception("cell with location x:" + edgeCell.Location.x + ", z:" + edgeCell.Location.z + " is not a cell along the maze edges");
        }

        List<CellDirection> directions = CellDirections.GetCellDirections;
        for (int i = 0; i < CellDirections.count; i++)
        {
            CellLocation relativeLocation = edgeCell.Location + directions[i].ToRelativeCellLocation();
            if (relativeLocation.x < 0 || relativeLocation.x == width || relativeLocation.z < 0 || relativeLocation.z == height)
            {
                return directions[i];
            }
        }

        throw new Exception("cell with location x:" + edgeCell.Location.x + ", z:" + edgeCell.Location.z + " is not a cell along the maze edges");
    }

    public Cell MakeConnection(Cell currentCell)
    {
        List<int> randomizedCellDirections = CellDirections.GetRandomizedCellDirections; // e.g [2, 1, 0, 3]

        for (int i = 0; i < randomizedCellDirections.Count; i++)
        {
            // The random direction from the current cell
            CellDirection direction = (CellDirection) randomizedCellDirections[i];

            // The neighbor cell location from the direction
            CellLocation nextLocation = currentCell.Location + direction.ToRelativeCellLocation();

            if (CanPlaceCell(nextLocation))
            {
                CellDirection fromDirection = direction.GetOpposite();
                Cell nextCell = PlaceCell(nextLocation, fromDirection);
                currentCell.AddConnection(direction); // Direction that connects it to the newly generated cell
                currentCell.name += "_" + direction;

                return nextCell;
            }
        }

        return null;
    }

    private bool IsEdgeCell(Cell cell)
    {
        return (cell.Location.x == 0 || cell.Location.x == width - 1 || cell.Location.z == 0 || cell.Location.z == height - 1); 
    }

    public bool CanPlaceCell(CellLocation location)
    {
        return 
            location.x >= 0 && 
            location.x < width &&
            location.z >= 0 && 
            location.z < height &&
            cells[location.x, location.z] == null;
    }

    public Cell PlaceCell(CellLocation location)
    {
        Cell cell = Instantiate(CellPrefab);
        cell.transform.parent = transform;
        cell.Location = location;
        cells[location.x, location.z] = cell;
        cell.pathVisible = pathVisible;
        return cell;
    }

    public Cell PlaceCell(CellLocation location, CellDirection fromDirection)
    {
        Cell cell = PlaceCell(location);
        cell.AddConnection(fromDirection);
        return cell;
    }

    private void SetExitCellOppositeOfEntryCell()
    {
        int x, z;

        //entry cell located along south or north edges
        if (entryCell.Location.x == 0 || entryCell.Location.x == width - 1)
        {
            x = width - 1 - entryCell.Location.x; // returns 0  or width - 1
            z = UnityEngine.Random.Range(0, height);
        }
        // entry cell located along east or west edges
        else
        {
            z = height - 1 - entryCell.Location.z; // returns 0  or width - 1
            x = UnityEngine.Random.Range(0, width);
        }

        SetExitCell(cells[x, z]);
    }

    private void SetExitCell(Cell cell)
    {
        cell.Material = exitCellMaterial;
        CellDirection exitCellDirection = GetDirectionThatLeadstoOutOfBound(cell);
        cell.AddConnection(exitCellDirection);
        exitCell = cell;
    }
}
