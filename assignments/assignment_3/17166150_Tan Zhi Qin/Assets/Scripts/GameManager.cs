using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System.IO;

public class GameManager : MonoBehaviour
{

    public SelectMethod selectMethod;
    public Maze mazePrefab;
    private Maze mazeInstance;
    public Object playerPrefab;
    private GameObject playerInstance;
    private Text timeText;
    private Text gameOverText;
    private bool gameOver;
    private float startTime;

    public Camera mapCamera;

    private void Start()
    {
        timeText = GameObject.Find("Timer").transform.GetChild(0).GetComponent<Text>();
        gameOverText = GameObject.Find("GameOverText").transform.GetChild(0).GetComponent<Text>();
        StartCoroutine(BeginGame());
    }

    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.F1))
        {
            RestartGame();
        }
        
        int diff = (int)Time.time - (int)startTime;
        int minutes = diff / 60;
        int seconds = diff % 60;
        timeText.text = string.Format("{0}:{1}", minutes.ToString("D2"), seconds.ToString("D2"));
        if (playerInstance != null & !gameOver) {
            if (playerInstance.transform.position.y < 0)
            {
                string gameOverTextF = "Game Over! Time Taken: {0}\nPress F1 to restart!";
                gameOverText.text = string.Format(gameOverTextF, timeText.text);
                gameOver = true;
                using (StreamWriter sw = new StreamWriter(string.Format("Evaluation Results\\{0}.csv", System.Enum.GetName(typeof(SelectMethod), selectMethod)), true))
                {
                    sw.WriteLine(string.Format("{0},{1},{2}", mazeInstance.GetFinalTotalDeadEnds(), mazeInstance.GetShortestDistance(), diff));
                }
            }
        }
    }

    private IEnumerator BeginGame()
    {
        ResetTime();
        gameOverText.text = "";
        mapCamera.clearFlags = CameraClearFlags.Skybox;
        mapCamera.rect = new Rect(0f, 0f, 1f, 1f);
        mazeInstance = Instantiate(mazePrefab) as Maze;
        IntVector2 startCoordinate = mazeInstance.RandomCoordinates;
        yield return StartCoroutine(mazeInstance.Generate(selectMethod, startCoordinate, this));
        playerInstance = Instantiate(playerPrefab, new Vector3(startCoordinate.x - mazeInstance.size.x * 0.5f + 0.5f, 0.5f, startCoordinate.z - mazeInstance.size.z * 0.5f + 0.5f), Quaternion.identity) as GameObject;
        mazeInstance.GetCell(startCoordinate).transform.GetChild(0).GetComponent<MeshRenderer>().material.SetColor("_Color", Color.green);
        mapCamera.clearFlags = CameraClearFlags.Depth;
        mapCamera.rect = new Rect(0f, 0f, 0.5f, 0.5f);
        gameOver = false;
    }

    private void RestartGame()
    {
        StopAllCoroutines();
        Destroy(mazeInstance.gameObject);
        if (playerInstance != null)
        {
            Destroy(playerInstance.gameObject);
        }
        StartCoroutine(BeginGame());
    }

    public void ResetTime()
    {
        startTime = Time.time;
    }
}

