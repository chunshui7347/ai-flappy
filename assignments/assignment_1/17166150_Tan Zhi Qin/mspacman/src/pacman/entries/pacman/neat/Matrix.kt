package pacman.entries.pacman.neat

class Matrix(val rows: Int, val cols: Int, init: (Int, Int) -> Double = { _, _ -> 0.0 }) {
    private var vals: Array<Array<Double>>

    init {
        vals = Array(rows) { i -> Array(cols) { j -> init(i, j) } }
    }

    constructor(arr: Array<Double>) : this(1, arr.size, { _, j -> arr[j] })

    constructor(matrix: Matrix) : this(matrix.rows, matrix.cols, { i, j -> matrix[i, j] })

    fun transpose(): Matrix {
        val result = Matrix(cols, rows)

        for (i in 0 until rows)
            for (j in 0 until cols)
                result[j, i] = this[i, j]

        return result
    }

    fun map(func: (Double) -> Double) {
        for (i in 0 until rows)
            for (j in 0 until cols)
                this[i, j] = func(this[i, j])
    }

    operator fun get(i: Int): Array<Double> {
        return vals[i].copyOf()
    }

    operator fun set(i: Int, values: Array<Double>) {
        if (values.size != cols)
            throw IllegalArgumentException("This matrix expect cols of size $cols")

        vals[i] = values.copyOf()
    }

    operator fun get(i: Int, j: Int): Double {
        return vals[i][j]
    }

    operator fun set(i: Int, j: Int, value: Double) {
        vals[i][j] = value
    }

    operator fun times(other: Matrix): Matrix {
        if (cols != other.rows)
            throw IllegalArgumentException("Matrix a cols must be equal to matrix b rows")

        val result = Matrix(rows, other.cols)
        for (i in 0 until result.rows)
            for (j in 0 until result.cols) {
                var sum = 0.0
                for (k in 0 until cols) {
                    sum += this[i, k] * other[k, j]
                }
                result[i, j] = sum
            }

        return result
    }

    operator fun times(other: Double): Matrix {
        val result = Matrix(this)

        for (i in 0 until rows)
            for (j in 0 until cols)
                result[i, j] *= other
        return result
    }

    operator fun plusAssign(other: Matrix) {
        if (cols != other.cols || rows != other.rows)
            throw IllegalArgumentException("When adding matrices the dimensions of them must be the same")

        for (i in 0 until rows)
            for (j in 0 until cols)
                this[i, j] += other[i, j]
    }

    operator fun plus(other: Matrix): Matrix {
        if (cols != other.cols || rows != other.rows)
            throw IllegalArgumentException("When adding matrices the dimensions of them must be the same")

        val result = Matrix(this)
        result += other
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other !is Matrix)
            return false

        if (cols != other.cols)
            return false
        if (rows != other.rows)
            return false

        for (i in 0 until rows)
            for (j in 0 until cols)
                if (this[i, j] != other[i, j])
                    return false
        return true
    }

    override fun toString(): String {
        val builder = StringBuilder()
        builder.append('[')
        for (i in 0 until rows) {
            if (i > 0)
                builder.append(", \n")
            builder.append('[')
            for (j in 0 until cols) {
                if (j > 0)
                    builder.append(", ")
                builder.append(this[i, j])
            }
            builder.append(']')
        }
        builder.append(']')

        return builder.toString()
    }

    // auto generated, ignore this
    override fun hashCode(): Int {
        var result = rows
        result = 31 * result + cols
        result = 31 * result + vals.contentDeepHashCode()
        return result
    }
}