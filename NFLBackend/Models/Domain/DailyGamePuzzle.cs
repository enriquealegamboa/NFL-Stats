using Supabase.Postgrest.Attributes;
using Supabase.Postgrest.Models;

namespace NFLBackend.Models.Domain;

[Table("daily_game_puzzle")]
public class DailyGamePuzzle : BaseModel
{
    [PrimaryKey("puzzle_date", false)]
    public DateTime PuzzleDate { get; set; }

    [Column("game_id")]
    public int GameId { get; set; }
}