package examples.monteCarlo;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;

import pacman.controllers.Controller;
import pacman.controllers.examples.AggressiveGhosts;
import pacman.game.Constants.DM;
import pacman.game.Constants.GHOST;
import pacman.game.Constants.MOVE;
import pacman.game.Game;

public class TreeNode {

    List<TreeNode> children;
    List<Integer> simulations;
    int directions;
    int time;
    TreeState state;
    TreeNode parent;
    MOVE move;
    int visited;
    float value;

    private boolean up = false;
    private boolean down = false;
    private boolean left = false;
    private boolean right = false;

    public TreeNode(TreeState state, TreeNode parent, MOVE move, int time) {
        super();
        this.state = state;
        this.parent = parent;
        this.move = move;
        this.visited = 0;
        this.directions = getDirections();
        this.value = 0;
        this.children = new ArrayList<TreeNode>();
        this.time = time;
        this.simulations = new ArrayList<Integer>();
    }


    public TreeNode expand() {

        int pacman = state.getGame().getPacmanCurrentNodeIndex();
        int junction = -1;
        MOVE nextMove = null;

        if (!state.isAlive()) {
            return this;
        }

        // Closest junctions
        if (!up && state.getGame().getNeighbour(pacman, MOVE.UP) != -1 && (parent == null || move.opposite() != MOVE.UP)) {
            junction = closestJunction(MOVE.UP);
            nextMove = MOVE.UP;
        } else if (!right && state.getGame().getNeighbour(pacman, MOVE.RIGHT) != -1 && (parent == null || move.opposite() != MOVE.RIGHT)) {
            junction = closestJunction(MOVE.RIGHT);
            nextMove = MOVE.RIGHT;
        } else if (!down && state.getGame().getNeighbour(pacman, MOVE.DOWN) != -1 && (parent == null || move.opposite() != MOVE.DOWN)) {
            junction = closestJunction(MOVE.DOWN);
            nextMove = MOVE.DOWN;
        } else if (!left && state.getGame().getNeighbour(pacman, MOVE.LEFT) != -1 && (parent == null || move.opposite() != MOVE.LEFT)) {
            junction = closestJunction(MOVE.LEFT);
            nextMove = MOVE.LEFT;
        }

        if (junction == -1) {
            return this;
        }

        if (junction != -1) {
            updateDirection(nextMove);

            TreeState childState = runTestUntilJunction(new AggressiveGhosts(), state.getGame(), junction, nextMove);
            if (childState == null || childState.getGame() == null) {
                return this;
            }

            int to = childState.getGame().getPacmanCurrentNodeIndex();
            int distance = (int) state.getGame().getDistance(pacman, to, DM.MANHATTAN);

            TreeNode child = new TreeNode(childState, this, nextMove, time + distance);
            children.add(child);
            return child;
        }

        return this;

    }

    private TreeState runTestUntilJunction(Controller<EnumMap<GHOST, MOVE>> ghostController, Game game, int junction, MOVE move) {

        Game clone = game.copy();
        int livesBefore = clone.getPacmanNumberOfLivesRemaining();
        int now = clone.getPacmanCurrentNodeIndex();
        while (now != junction) {

            int last = now;

            clone.advanceGame(move,
                    ghostController.getMove(clone.copy(),
                            System.currentTimeMillis()));

            now = clone.getPacmanCurrentNodeIndex();
            int livesNow = clone.getPacmanNumberOfLivesRemaining();

            if (livesNow < livesBefore)
                return new TreeState(false, clone);

            if (now == last) {
                break;
            }

        }

        return new TreeState(true, clone);

    }


    private void updateDirection(MOVE move) {
        switch (move) {
            case UP:
                up = true;
                break;
            case DOWN:
                down = true;
                break;
            case RIGHT:
                right = true;
                break;
            case LEFT:
                left = true;
                break;
        }
    }


    private int closestJunction(MOVE move) {

        int from = state.getGame().getPacmanCurrentNodeIndex();
        int current = from;
        if (current == -1)
            return -1;

        while (!MonteCarloController.junctions.contains(current) || current == from) {

            int next = state.getGame().getNeighbour(current, move);

            if (next == from)
                return -1;

            current = next;
            if (current == -1)
                return -1;

        }

        return current;

    }

    private int getDirections() {

        if (!state.isAlive())
            return 0;
        int node = state.getGame().getPacmanCurrentNodeIndex();
        int[] neighbors = state.getGame().getNeighbouringNodes(node);
        int count = 0;
        for (Integer i : neighbors) {
            if (parent == null || state.getGame().getMoveToMakeToReachDirectNeighbour(node, i) != move.opposite()) {
                count++;
            }
        }
        return count;

    }

    public TreeNode getParent() {
        return parent;
    }

    public TreeState getState() {
        return state;
    }

    public MOVE getMove() {
        return move;
    }

    public void setMove(MOVE move) {
        this.move = move;
    }

    public int getVisited() {
        return visited;
    }

    public void setVisited(int visited) {
        this.visited = visited;
    }

    public boolean isExpandable() {
        return directions != children.size() && state.isAlive();
    }

    public float getValue() {
        return value;
    }

    public void setValue(float value) {
        this.value = value;
    }

    public int getTime() {
        return time;
    }

    public List<Integer> getSimulations() {
        return simulations;
    }

}
