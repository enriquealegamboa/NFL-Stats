using NFLBackend.Models.Domain;
using NFLBackend.Repositories.Interfaces;
using NFLBackend.Services.Interfaces;

namespace NFLBackend.Services;

public class DailyGameService : IDailyGameService
{
    private readonly IDailyGameRepository _repo;

    public DailyGameService(IDailyGameRepository repo)
    {
        _repo = repo;
    }

    public async Task<DailyGamePuzzle?> GetTodayAsync()
    {
        var today = DateTime.UtcNow.Date;
        return await _repo.GetByDateAsync(today);
    }
}