package examples.StarterPacMan;

import pacman.controllers.PacmanController;
import pacman.game.Constants.*;
import pacman.game.Game;

import java.util.*;

public class CustomPacMan extends PacmanController {
	@Override
	public MOVE getMove(Game game, long time) {

		int pacmanCurrentNodeIndex = game.getPacmanCurrentNodeIndex();

		ArrayList<CustomGhost> customGhostList = new ArrayList<>();
		customGhostList.add(new CustomGhost(GHOST.BLINKY, game.getGhostCurrentNodeIndex(GHOST.BLINKY)));
		customGhostList.add(new CustomGhost(GHOST.SUE, game.getGhostCurrentNodeIndex(GHOST.SUE)));
		customGhostList.add(new CustomGhost(GHOST.INKY,game.getGhostCurrentNodeIndex(GHOST.INKY)));
		customGhostList.add(new CustomGhost(GHOST.PINKY,game.getGhostCurrentNodeIndex(GHOST.PINKY)));

		HashSet<Integer> visitedIndices = new HashSet<>();
		visitedIndices.add(pacmanCurrentNodeIndex);

		HashSet<Integer> pillIndices = new HashSet<>();
		for (int index: game.getActivePillsIndices()) {
			pillIndices.add(index);
		}

		HashSet<Integer> powerPillIndices = new HashSet<>();
		for (int index: game.getActivePowerPillsIndices()) {
			powerPillIndices.add(index);
		}

		BestMove pacmanBestMove = getPacmanBestMove(
				game,
				pacmanCurrentNodeIndex,
				customGhostList,
				visitedIndices,
				pillIndices,
				powerPillIndices,
				100,
				0,
				MOVE.LEFT
		);

		return pacmanBestMove.move;
	}

	public BestMove getPacmanBestMove(
			Game game,
			int pacmanCurrentNodeIndex,
			ArrayList<CustomGhost> customGhostList,
			HashSet<Integer> visitedIndices,
			HashSet<Integer> pillIndices,
			HashSet<Integer> powerPillIndices,
			int depth,
			double score,
			MOVE selectedMove
	) {
		if (depth == 0 || score < 0) {
			return new BestMove(score, selectedMove);
		}

		BestMove bestMove=new BestMove(Integer.MIN_VALUE,MOVE.NEUTRAL);

		MOVE[] possibleMoves = game.getPossibleMoves(pacmanCurrentNodeIndex);

		for (MOVE move: possibleMoves) {
//			get pacman next possible indices
			int pacmanNextPossibleIndex = game.getNeighbour(pacmanCurrentNodeIndex, move);

			if (visitedIndices.contains(pacmanNextPossibleIndex) || move == MOVE.NEUTRAL) {
				continue;
			} else {
				visitedIndices.add(pacmanNextPossibleIndex);
			}
			int currentScore = 0;

			boolean containPill = false;
			if (pillIndices.contains(pacmanNextPossibleIndex)) {
				currentScore ++;
				containPill = true;
				pillIndices.remove(pacmanNextPossibleIndex);
			}

			boolean containPowerPill = false;
			if (powerPillIndices.contains(pacmanNextPossibleIndex)) {
				currentScore ++;
				containPowerPill = true;
				powerPillIndices.remove(pacmanNextPossibleIndex);
			}

//			get ghost move
			ArrayList<CustomGhost> ghostsWithNextPossibleIndex = new ArrayList<>();
			int edibleGhostCount=0;
			MOVE eatGhost = MOVE.NEUTRAL;
			findingGhostBestMoves:for (CustomGhost ghost: customGhostList) {
				BestMove ghostBestMove= getGhostBestMove(game, ghost, pacmanNextPossibleIndex);
				int ghostBestMoveIndex = game.getNeighbour(ghost.index, ghostBestMove.move);

//				determine if the pacman should eat the ghost
				if(game.isGhostEdible(ghost.name)){
					boolean isPacmanNearToEdibleGhost=Math.abs(game.getShortestPathDistance(pacmanNextPossibleIndex,ghostBestMoveIndex))<200;
					if(isPacmanNearToEdibleGhost && game.getGhostEdibleTime(ghost.name)>80){
						eatGhost=game.getNextMoveTowardsTarget(pacmanCurrentNodeIndex,ghostBestMoveIndex,DM.PATH);
						edibleGhostCount++;
					}
				}

				if(edibleGhostCount>2) {
					return new BestMove(400, eatGhost);
				}
				ghostsWithNextPossibleIndex.add(new CustomGhost(ghost.name,ghostBestMoveIndex));

//				if pacman will lose
				if (ghostBestMove.score == Integer.MAX_VALUE) {
					currentScore += Integer.MIN_VALUE;
					break findingGhostBestMoves;
				}
			}

//			loop recursively to get all possible score for pacman moves
			BestMove bestMoveTree = getPacmanBestMove(
					game,
					pacmanNextPossibleIndex,
					ghostsWithNextPossibleIndex,
					visitedIndices,
					pillIndices,
					powerPillIndices,
					depth - 1,
					score + currentScore,
					move
			);

//			get the highest score and the respective move
			if (bestMoveTree.score > bestMove.score) {
				bestMove.score = bestMoveTree.score;
				bestMove.move = move;
			}

//			revert to original game map to calculate other possible move score
			if (containPill) {
				pillIndices.add(pacmanNextPossibleIndex);
			}
			if (containPowerPill) {
				powerPillIndices.add(pacmanNextPossibleIndex);
			}
			visitedIndices.remove(pacmanNextPossibleIndex);
		}

		return bestMove;
	}

	public BestMove getGhostBestMove(Game game, CustomGhost ghost, int pacmanIndex) {
		MOVE[] moves = game.getPossibleMoves(ghost.index);
		int shortestDistance = Integer.MAX_VALUE;
		MOVE bestMove = MOVE.NEUTRAL;
		for (MOVE move: moves) {
//			get the shortest distance from current ghost to pacman
			int ghostNewIndex = game.getNeighbour(ghost.index, move);
			int distance = game.getShortestPathDistance(ghostNewIndex, pacmanIndex);
			if (distance < shortestDistance) {
				shortestDistance = distance;
				bestMove = move;
			}
		}

		double score = shortestDistance;

		if (shortestDistance < 5) {
			score = Integer.MAX_VALUE;
		}
		return new BestMove(score, bestMove);
	}

}
