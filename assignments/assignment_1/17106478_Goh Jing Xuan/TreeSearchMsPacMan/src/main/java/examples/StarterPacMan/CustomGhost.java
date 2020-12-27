package examples.StarterPacMan;

import pacman.game.Constants.*;

public class CustomGhost {
    GHOST name;
    int index;

    public CustomGhost(GHOST ghostName,int index) {
        this.name = ghostName;
        this.index = index;
    }
}
