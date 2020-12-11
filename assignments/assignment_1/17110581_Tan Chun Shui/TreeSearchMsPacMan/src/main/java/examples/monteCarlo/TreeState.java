package examples.monteCarlo;

import pacman.game.Game;

public class TreeState {

	boolean alive;
	Game game;
	
	public TreeState(boolean alive, Game game) {
		super();
		this.alive = alive;
		this.game = game;
	}

	public boolean isAlive() {
		return alive;
	}

	public void setAlive(boolean alive) {
		this.alive = alive;
	}

	public Game getGame() {
		return game;
	}

	public void setGame(Game game) {
		this.game = game;
	}
	
}
