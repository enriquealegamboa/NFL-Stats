namespace NFLBackend.Models.Dtos;

public class GuessResponseDto
{
    public bool Correct { get; set; }
    public bool TeamCorrect { get; set; }
    public bool SeasonCorrect { get; set; }
    public string SeasonDirection { get; set; } = "";
    public bool GameOver { get; set; }
    public int RemainingGuesses { get; set; }
}