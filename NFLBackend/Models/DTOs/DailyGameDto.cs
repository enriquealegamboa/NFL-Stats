using System.Text.Json.Serialization;

namespace NFLBackend.Models.Dtos;


public class DailyGameDto
{
    [JsonPropertyName("team_id")]
    public int TeamId { get; set; }

    [JsonPropertyName("season_id")]
    public int SeasonId { get; set; }
}