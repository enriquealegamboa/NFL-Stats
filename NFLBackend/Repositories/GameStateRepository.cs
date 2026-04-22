using System.Text.Json;
using NFLBackend.Data;
using NFLBackend.Models.Dtos;

namespace NFLBackend.Repositories;

public class GameStateRepository
{
    private readonly SupabaseRestClient _client;

    public GameStateRepository(SupabaseRestClient client)
    {
        _client = client;
    }

    public async Task<DailyGameDto?> GetCurrentGameAsync()
    {
        var json = await _client.GetAsync(
            "daily_game_puzzle?select=team_id,season_id&order=puzzle_date.desc&limit=1"
        );

        var data = JsonSerializer.Deserialize<List<DailyGameDto>>(json);

        return data?.FirstOrDefault();
    }
}