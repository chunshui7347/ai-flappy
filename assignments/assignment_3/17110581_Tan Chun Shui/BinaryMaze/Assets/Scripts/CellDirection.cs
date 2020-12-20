using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public enum CellDirection
{
    // Towards positve x
    North,

    // Towards negative z
    East,

    // Towards negative x
    South,

    // Towards positive z
    West,
}

public static class CellDirections
{
    public const int count = 4;
    private static List<int> directionIndexes = new List<int>() { 0, 1, 2, 3 }; 

    public static List<int> GetRandomizedCellDirections
    {
        get
        {
            directionIndexes.Shuffle();
            return directionIndexes;
        }
    }

    public static List<CellDirection> GetCellDirections
    {
        get
        {
            return new List<CellDirection>() { CellDirection.North, CellDirection.East, CellDirection.South, CellDirection.West };
        }
    }

    public static CellDirection GetRandomDirection 
    {
        get
        {
            return (CellDirection) UnityEngine.Random.Range(0, count);
        }
    }

    private static CellDirection[] opposites =
    {
        CellDirection.South,
        CellDirection.West,
        CellDirection.North,
        CellDirection.East
    };

    private static CellLocation[] unitVectors = 
    {
        new CellLocation(1, 0),
        new CellLocation(0, -1),
        new CellLocation(-1, 0),
        new CellLocation(0, 1)
    };

    private static Quaternion[] rotations =
    {
        Quaternion.identity,
        Quaternion.Euler(0, 90, 0),
        Quaternion.Euler(0, 180, 0),
        Quaternion.Euler(0, 270, 0)
    };

    public static CellDirection GetOpposite(this CellDirection direction)
    {
        return opposites[(int)direction];
    }

    public static CellLocation ToRelativeCellLocation(this CellDirection cellDirection)
    {
        return unitVectors[(int)cellDirection];
    }

    public static Quaternion ToRotation(this CellDirection cellDirection)
    {
        return rotations[(int)cellDirection];
    }

}