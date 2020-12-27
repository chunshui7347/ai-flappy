package examples.StarterPacMan;

import pacman.game.Constants.*;

public class BestMove {
    double score;
    MOVE move;

    public BestMove(double score, MOVE move) {
        this.score = score;
        this.move = move;
    }
}
