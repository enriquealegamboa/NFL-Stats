using NFLBackend.Models.Dtos;

namespace NFLBackend.Repositories.Interfaces;

public interface IGameStateRepository
{
    Task<DailyGameDto?> GetCurrentGameAsync();
}