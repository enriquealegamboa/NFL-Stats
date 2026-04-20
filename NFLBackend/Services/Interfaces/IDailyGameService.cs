namespace NFLBackend.Services.Interfaces;

using NFLBackend.Models.Domain;

public interface IDailyGameService
{
    Task<DailyGamePuzzle?> GetTodayAsync();
}