﻿[System.Serializable]
public struct IntVector2
{

    public int x, z;

    public IntVector2(int x, int z)
    {
        this.x = x;
        this.z = z;
    }

    public static IntVector2 operator +(IntVector2 a, IntVector2 b)
    {
        return new IntVector2(a.x + b.x, a.z + b.z);
    }

    public bool Equals(IntVector2 o)
    {
        return this.x == o.x & this.z == o.z;
    }
}