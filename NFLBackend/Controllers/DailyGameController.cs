using Microsoft.AspNetCore.Mvc;
using NFLBackend.Models.Dtos;
using NFLBackend.Services.Interfaces;

namespace NFLBackend.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DailyGameController : ControllerBase
{
    private readonly IDailyGameService _service;

    public DailyGameController(IDailyGameService service)
    {
        _service = service;
    }

    [HttpGet("today")]
    public async Task<IActionResult> GetToday()
    {
        var result = await _service.GetTodayAsync();

        if (result == null)
            return NotFound();

        return Ok(result);
    }

    [HttpPost("guess")]
    public async Task<IActionResult> Guess([FromBody] GuessRequestDto request)
    {
        var result = await _service.CheckGuessAsync(request.TeamId, request.SeasonId);
        return Ok(result);
    }
}