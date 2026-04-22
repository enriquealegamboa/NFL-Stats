using NFLBackend.Models.Dtos;
using NFLBackend.Repositories;
using NFLBackend.Services.Interfaces;

namespace NFLBackend.Services;

public class DailyGameService : IDailyGameService
{
    private readonly GameStateRepository _repo;

    public DailyGameService(GameStateRepository repo)
    {
        _repo = repo;
    }

    public async Task<DailyGameDto?> GetTodayAsync()
    {
        return await _repo.GetCurrentGameAsync();
    }

    public async Task<GuessResponseDto> CheckGuessAsync(int teamId, int seasonId)
    {
        var game = await _repo.GetCurrentGameAsync();

        if (game == null)
            throw new Exception("No active game");

        var teamCorrect = teamId == game.TeamId;
        var seasonCorrect = seasonId == game.SeasonId;
        var correct = teamCorrect && seasonCorrect;

        return new GuessResponseDto
        {
            Correct = correct,
            TeamCorrect = teamCorrect,
            SeasonCorrect = seasonCorrect,
            SeasonDirection = seasonCorrect
                ? "Correct"
                : seasonId > game.SeasonId ? "Lower" : "Higher",
            GameOver = correct,
            RemainingGuesses = correct ? 0 : 1
        };
    }
}