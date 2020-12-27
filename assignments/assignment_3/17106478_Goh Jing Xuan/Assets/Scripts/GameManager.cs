//using UnityEngine;
//using System.Collections;

//public class GameManager : MonoBehaviour
//{
//	public Maze mazePrefab;
//	private Maze mazeInstance;
//	public Player playerPrefab;
//	private Player playerInstance;

//	private void Start()
//	{
//		StartCoroutine(BeginGame());
//	}

//	private void Update()
//	{
//		if (Input.GetKeyDown(KeyCode.Space))
//		{
//			RestartGame();
//		}
//	}

//    private IEnumerator BeginGame()
//    {
//        Camera.main.clearFlags = CameraClearFlags.Skybox;
//        Camera.main.rect = new Rect(0f, 0f, 1f, 1f);
//        mazeInstance = Instantiate(mazePrefab) as Maze;
//        yield return StartCoroutine(mazeInstance.Generate());
//        playerInstance = Instantiate(playerPrefab) as Player;
//        playerInstance.SetLocation(mazeInstance.GetCell(mazeInstance.RandomCoordinates));
//        Camera.main.clearFlags = CameraClearFlags.Depth;
//        Camera.main.rect = new Rect(0f, 0f, 0.5f, 0.5f);
//    }

//    private void restartgame()
//    {
//        stopallcoroutines();
//        destroy(mazeinstance.gameobject);
//        if (playerinstance != null)
//        {
//            destroy(playerinstance.gameobject);
//        }
//        startcoroutine(begingame());
//    }
//}

using UnityEngine;
using System.Collections;

public class GameManager : MonoBehaviour
{

	public Maze mazePrefab;

	private Maze mazeInstance;

	private void Start()
	{
		BeginGame();
	}

	private void Update()
	{
		if (Input.GetKeyDown(KeyCode.Space))
		{
			RestartGame();
		}
	}

	private void BeginGame()
	{
		mazeInstance = Instantiate(mazePrefab) as Maze;
		StartCoroutine(mazeInstance.Generate());
	}

	private void RestartGame()
	{
		StopAllCoroutines();
		Destroy(mazeInstance.gameObject);
		BeginGame();
	}
}