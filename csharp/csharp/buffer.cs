using System;
using System.Linq;
using System.Runtime.CompilerServices;

public static class Buffer
{
    private static int size;
    private static double[] data;


    public static void SetSize(int _size)
    {
        size = _size;
        data = new double[size];
    }

    public static void Append(double[] x)
    {
        int newDataLength = x.Length;
        int existingDataLength = size - newDataLength;

        // Shift the existing data to the left and append new data at the end
        double[] tempArr = new double[size];
        Array.Copy(data, newDataLength, tempArr, 0, existingDataLength);
        Array.Copy(x, 0, tempArr, existingDataLength, newDataLength);
        data = tempArr;
    }

    public static double[] Get()
    {
        return data;
    }

    public static double[] GetPart(int start = 65536)
    {
        return data.Skip(Math.Max(0, data.Length - start)).ToArray();
    }
}
