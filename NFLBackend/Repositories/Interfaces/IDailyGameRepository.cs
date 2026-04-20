using NFLBackend.Models.Domain;

namespace NFLBackend.Repositories.Interfaces;

public interface IDailyGameRepository
{
    Task<DailyGamePuzzle?> GetByDateAsync(DateTime date);
}