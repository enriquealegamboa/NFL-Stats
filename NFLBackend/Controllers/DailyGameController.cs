using Microsoft.AspNetCore.Mvc;
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
            return NotFound("No game for today");

        return Ok(result);
    }
}