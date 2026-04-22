using NFLBackend.Models.Dtos;

namespace NFLBackend.Services.Interfaces;

public interface IDailyGameService
{
    Task<DailyGameDto?> GetTodayAsync();
    Task<GuessResponseDto> CheckGuessAsync(int teamId, int seasonId);
}