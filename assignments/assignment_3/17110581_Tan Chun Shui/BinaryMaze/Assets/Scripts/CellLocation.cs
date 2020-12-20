using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[System.Serializable]
public class CellLocation
{
    public int x, z;

    public CellLocation(int x, int z)
    {
        this.x = x;
        this.z = z;
    }

    public static CellLocation operator + (CellLocation a, CellLocation b)
    {
        return new CellLocation(a.x + b.x, a.z + b.z);
    }
}
