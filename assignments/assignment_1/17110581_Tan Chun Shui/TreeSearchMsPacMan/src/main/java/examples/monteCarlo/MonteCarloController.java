package examples.monteCarlo;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Date;
import java.util.EnumMap;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import pacman.controllers.Controller;
import pacman.controllers.examples.Legacy;
import pacman.game.Constants.DM;
import pacman.game.Constants.GHOST;
import pacman.game.Constants.MOVE;
import pacman.game.internal.Node;
import pacman.game.Game;

public class MonteCarloController extends Controller<MOVE> {

    public int lostLifeValue = -500;
    private int stimulationCount = 200;
    private int treeDepth = 40;
    private int powerPillPenalty = -100;
    private int minGhostDistance = 200;
    float C = (float) (1f / Math.sqrt(2));
    Controller<EnumMap<GHOST, MOVE>> ghosts = new Legacy();

    public static Set<Integer> junctions;
    int lastLevel = 1;

    @Override
    public MOVE getMove(Game game, long timeDue) {

        int level = game.getCurrentLevel();

        if (junctions == null || lastLevel != level) {
            junctions = getJunctions(game);
        }

        lastLevel = level;

        return MonteCartoTreeSearch(game, 10);

    }

    private MOVE MonteCartoTreeSearch(Game game, long ms) {

        long start = new Date().getTime();
        TreeNode v0 = new TreeNode(new TreeState(true, game), null, game.getPacmanLastMoveMade(), 0);

        while (new Date().getTime() < start + ms) {

            TreeNode v1 = treePolicy(v0);

            if (v1 == null)
                return MOVE.DOWN;

            int score = defaultPolicy(v1, v0);

            process(v1, score);

        }

        TreeNode bestNode = bestChild(v0, 0);
        MOVE move = MOVE.UP;
        if (bestNode != null)
            move = bestNode.getMove();
        return move;

    }

    private TreeNode treePolicy(TreeNode node) {

        if (node.isExpandable()) {
            if (node.getTime() <= treeDepth)
                return node.expand();
            else
                return node;
        }

        if (node.getState().isAlive())
            return treePolicy(bestChild(node, C));
        else
            return node;

    }

    private int defaultPolicy(TreeNode node, TreeNode root) {

        if (!node.getState().isAlive() ||
                node.getState().getGame().getPacmanNumberOfLivesRemaining() < root.getState().getGame().getPacmanNumberOfLivesRemaining())
            return lostLifeValue;

        Controller<EnumMap<GHOST, MOVE>> ghostController = ghosts;

        Game game = node.getState().getGame().copy();

        int prevLives = game.getPacmanNumberOfLivesRemaining();
        int ppBefore = game.getNumberOfActivePowerPills();
        int count = 0;
        int bonus = 0;
        while (!game.gameOver()) {
            if (count >= stimulationCount && game.getNeighbouringNodes(game.getPacmanCurrentNodeIndex()).length > 2)
                break;
            game.advanceGame(getTempMove(game.copy(), System.currentTimeMillis()),
                    ghostController.getMove(game.copy(), System.currentTimeMillis()));
            count++;
            int ppAfter = game.getNumberOfActivePowerPills();
            if (ppAfter < ppBefore && avgDistanceToGhosts(game) > minGhostDistance) {
                bonus += powerPillPenalty;
            }
            int nextLives = game.getPacmanNumberOfLivesRemaining();
            if (nextLives < prevLives) {
                break;
            }
        }

        int score = game.getScore();

        int nextLives = game.getPacmanNumberOfLivesRemaining();
        if (nextLives < prevLives) {
            score += lostLifeValue;
        }

        return score + bonus - root.getState().getGame().getScore();

    }


    private TreeNode bestChild(TreeNode v, float c) {

        float bestValue = Integer.MIN_VALUE;
        TreeNode urgent = null;

        for (TreeNode node : v.children) {
            float value = UCT(node, c);
            if (!node.getState().isAlive())
                value = -99999;

            if (value > bestValue) {

                Controller<EnumMap<GHOST, MOVE>> ghostController = ghosts;

                Game game = v.getState().getGame().copy();

                int prevLives = game.getPacmanNumberOfLivesRemaining();

                game.advanceGame(node.getMove(),
                        ghostController.getMove(game.copy(), System.currentTimeMillis()));

                int nextLives = game.getPacmanNumberOfLivesRemaining();

                if (c != 0 || nextLives >= prevLives) {
                    urgent = node;
                    bestValue = value;
                }
            }
        }

        return urgent;
    }


    private float UCT(TreeNode node, float c) {

        float reward = node.getValue() / node.getVisited();
        reward = normalize(reward);

        float n = 0;
        if (node.getParent() != null)
            n = node.getParent().getVisited();

        float nj = node.getVisited();

        float uct = (float) (reward + 2 * c * Math.sqrt((2 * Math.log(n)) / nj));

        return uct;

    }

    private float normalize(float x) {

        float min = -500;
        float max = 2000;
        float range = max - min;
        float inZeroRange = (x - min);
        float norm = inZeroRange / range;

        return norm;
    }

    
    private void process(TreeNode v, int score) {

        v.setVisited(v.getVisited() + 1);
        v.setValue(v.getValue() + score);
        v.getSimulations().add(score);
        if (v.getParent() != null)
            process(v.getParent(), score);

    }


    public static Set<Integer> getJunctions(Game game) {
        Set<Integer> junctions = new HashSet<Integer>();

        int[] juncArr = game.getJunctionIndices();
        for (Integer i : juncArr)
            junctions.add(i);

        junctions.addAll(getTurns(game));

        return junctions;

    }

    private static Collection<? extends Integer> getTurns(Game game) {

        List<Integer> turns = new ArrayList<Integer>();

        for (Node n : game.getCurrentMaze().graph) {

            int down = game.getNeighbour(n.nodeIndex, MOVE.DOWN);
            int up = game.getNeighbour(n.nodeIndex, MOVE.UP);
            int left = game.getNeighbour(n.nodeIndex, MOVE.LEFT);
            int right = game.getNeighbour(n.nodeIndex, MOVE.RIGHT);

            if (((down != -1) != (up != -1)) || ((left != -1) != (right != -1))) {
                turns.add(n.nodeIndex);
            } else if (down != -1 && up != -1 && left != -1 && right != -1) {
                turns.add(n.nodeIndex);
            }

        }

        return turns;
    }

    private int avgDistanceToGhosts(Game game) {
        int sum = 0;
        for (GHOST ghost : GHOST.values())
            sum += game.getDistance(game.getPacmanCurrentNodeIndex(), game.getGhostCurrentNodeIndex(ghost), DM.MANHATTAN);
        return sum / 4;
    }

    public MOVE getTempMove(Game game, long timeDue) {
		
		if (MonteCarloController.junctions == null)
		MonteCarloController.junctions = MonteCarloController.getJunctions(game);
			
		
		MOVE lastMove = game.getPacmanLastMoveMade();
		
		if (inJunction(game))
			return randomAction(lastMove);
		else
			return lastMove;
		
	}
	
	private boolean inJunction(Game game) {
		
		if (MonteCarloController.junctions.contains(game.getPacmanCurrentNodeIndex()))
			return true;
		
		return false;
	}

	private MOVE randomAction(MOVE except) {
		MOVE move = null;
		
		while(move == null){
			int random = (int) (Math.random() * 4);
			
			switch(random){
			case 0: move = MOVE.UP; break;
			case 1: move = MOVE.RIGHT; break;
			case 2: move = MOVE.DOWN; break;
			case 3: move = MOVE.LEFT; break;
			}
			
			if (move == except)
				move = null;
			
		}
		
		return move;
	}


}
