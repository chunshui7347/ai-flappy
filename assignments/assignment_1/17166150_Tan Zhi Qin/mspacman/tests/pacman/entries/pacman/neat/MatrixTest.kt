package pacman.entries.pacman.neat

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class MatrixTest {

    private lateinit var a: Matrix
    private lateinit var b: Matrix
    private lateinit var c: Matrix

    @BeforeEach
    fun setup() {
        a = Matrix(2, 3)
        a[0] = arrayOf(3.0, 2.0, 3.0)
        a[1] = arrayOf(2.0, 1.0, 7.4)

        b = Matrix(3, 4)
        b[0] = arrayOf(3.0, 2.0, 3.0, 8.0)
        b[1] = arrayOf(2.0, 1.0, 7.4, 1.9)
        b[2] = arrayOf(4.0, 7.0, 9.4, 1.9)

        c = Matrix(2, 3)
        c[0] = arrayOf(6.0, 9.2, 31.0)
        c[1] = arrayOf(2.8, 2.0, 3.3)
    }

    @Test
    fun transpose() {
        val transposeA = Matrix(3, 2)
        transposeA[0] = arrayOf(3.0, 2.0)
        transposeA[1] = arrayOf(2.0, 1.0)
        transposeA[2] = arrayOf(3.0, 7.4)

        val result = a.transpose()
        assertEquals(result, transposeA, "matrix transpose result should be:\n$transposeA\ngot:\n$result")
    }

    @Test
    fun map() {
        val mapResult = Matrix(2, 3)
        mapResult[0] = arrayOf(9.0, 4.0, 9.0)
        mapResult[1] = arrayOf(4.0, 1.0, 7.4 * 7.4)

        // assign to self
        a.map { x -> x * x }

        assertEquals(a, mapResult, "matrix mapping with func { x -> x * x } should result in:\n$mapResult\ngot:\n$a")
    }

    @Test
    fun matrixMultiply() {
        val correctAxB = Matrix(2, 4)
        correctAxB[0] = arrayOf(25.0, 29.0, 52.0, 33.5)
        correctAxB[1] = arrayOf(37.6, 56.800000000000004, 82.96000000000001, 31.96)

        val result = a * b
        assertEquals(result, correctAxB, "matrix multiplication result should be:\n$correctAxB\ngot:\n$result")
    }

    @Test
    fun numberMultiply() {
        val correctAx3 = Matrix(2, 3)
        correctAx3[0] = arrayOf(9.0, 6.0, 9.0)
        correctAx3[1] = arrayOf(6.0, 3.0, 7.4 * 3.0)

        val result = a * 3.0
        assertEquals(result, correctAx3, "matrix multiplication with scalar (3) result should be:\n$correctAx3\ngot:\n$result")
    }

    @Test
    fun add() {
        val addResult = Matrix(2, 3)
        addResult[0] = arrayOf(9.0, 11.2, 34.0)
        addResult[1] = arrayOf(4.8, 3.0, 10.7)

        val result = a + c
        assertEquals(result, addResult, "matrix multiplication result should be:\n$addResult\ngot:\n${result}")
    }
}