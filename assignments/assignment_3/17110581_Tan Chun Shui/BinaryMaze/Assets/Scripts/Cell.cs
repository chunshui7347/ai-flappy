using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Cell : MonoBehaviour
{
    public Transform connectionPrefab;
    public Transform wallPrefab;
    public bool pathVisible = true;
    private Transform floor;
    private CellLocation location;
    private Dictionary<CellDirection, Transform> connections = new Dictionary<CellDirection, Transform>()
    {
        { CellDirection.North, null },
        { CellDirection.East, null },
        { CellDirection.South, null },
        { CellDirection.West, null },
    };
    private Dictionary<CellDirection, Transform> edges = new Dictionary<CellDirection, Transform>()
    {
        { CellDirection.North, null },
        { CellDirection.East, null },
        { CellDirection.South, null },
        { CellDirection.West, null },
    };

    public void Awake()
    {
        floor = transform.Find("Floor");
    }

    public CellLocation Location
    {
        set
        {
            transform.localPosition = new Vector3(value.x, 0, value.z);
            name = "Cell " + value.x + ", " + value.z;
            location = value;
        }
        get
        {
            return location;
        }
    }

    public void AddConnection(CellDirection direction)
    {
        Transform connection = Instantiate(connectionPrefab);
        connection.transform.parent = transform;
        connection.localPosition = Vector3.zero;
        connection.localRotation = direction.ToRotation();
        connection.gameObject.SetActive(pathVisible);
        connections[direction] = connection;
    }

    public void RemoveConnection(CellDirection direction)
    {
        if (connections[direction] != null)
        {
            Destroy(edges[direction].gameObject);
            connections[direction] = null;
        }
    }

    public Transform CreateWall(CellDirection direction)
    {
        Transform wall = Instantiate(wallPrefab);
        wall.transform.parent = transform;
        wall.localPosition = Vector3.zero;
        wall.localRotation = direction.ToRotation();
        return wall;
    }

    public Material Material
    {
        set
        {
            floor.GetComponent<MeshRenderer>().material = value;
        }
    }

    public void CreateWalls()
    {
        // Loop through each direction
        foreach(KeyValuePair<CellDirection, Transform> connection in connections)
        {
            CellDirection direction = connection.Key;
            Transform pointer = connection.Value;

            // If no connection to neighboring cell on the direction and no wall is there, create a wall there
            if (pointer == null && edges[direction] == null)
            {
                Transform wall = CreateWall(direction);
                edges[direction] = wall;
            }
            // If connection to neighbor cell exists and a wall exist, remove the wall
            else if (pointer != null && edges[direction] != null)
            {
                Destroy(edges[direction].gameObject);
                edges[direction] = null;
            }
        }
    }
}
