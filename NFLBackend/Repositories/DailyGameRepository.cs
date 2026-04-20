using Supabase.Postgrest;
using NFLBackend.Repositories.Interfaces;
using NFLBackend.Models.Domain;
using NFLBackend.Data;

namespace NFLBackend.Repositories;


public class DailyGameRepository : IDailyGameRepository
{
    private readonly SupabaseClientFactory _client;

    public DailyGameRepository(SupabaseClientFactory client)
    {
        _client = client;
    }

    public async Task<DailyGamePuzzle?> GetByDateAsync(DateTime date)
    {
        var dateString = date.ToString("yyyy-MM-dd");
        
        var response = await _client.Client
            .From<DailyGamePuzzle>()
            .Filter("puzzle_date", Constants.Operator.Equals, dateString)
            .Get();

        return response.Models.FirstOrDefault();
    }
}