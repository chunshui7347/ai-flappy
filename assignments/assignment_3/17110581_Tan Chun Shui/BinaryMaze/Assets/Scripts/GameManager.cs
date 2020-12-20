using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameManager : MonoBehaviour
{
    public Maze mazePrefab;
    private Maze mazeInstance;

    private void Awake()
    {
        StartCoroutine(BeginGame());
    }

    private IEnumerator BeginGame()
    {
        print("start game");
        mazeInstance = Instantiate(mazePrefab, new Vector3(0.5f, 0f, 0.5f), Quaternion.identity) as Maze;
        yield return mazeInstance.GenerateBinarySearch();
    }

    private void RestartGame()
    {
        StopAllCoroutines();
        Destroy(mazeInstance.gameObject);
        StartCoroutine(BeginGame());
    }

    public void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
        {
            RestartGame();
        }
    }
}
