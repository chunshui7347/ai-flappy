package pacman.entries.pacman.neat

fun <T : Comparable<T>> Array<T>.maxIndex(): Int {
    // get the move that have the max value
    var maxIndexMove = 0
    var maxVal = this[maxIndexMove]
    for (i in this.indices)
        if (this[i] > maxVal) {
            maxVal = this[i]
            maxIndexMove = i
        }

    return maxIndexMove
}