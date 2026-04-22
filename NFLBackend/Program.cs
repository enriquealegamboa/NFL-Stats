using NFLBackend.Data;
using NFLBackend.Repositories;
using NFLBackend.Services;
using NFLBackend.Services.Interfaces;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Configuration.AddEnvironmentVariables();

// Supabase REST client
builder.Services.AddSingleton<SupabaseRestClient>();

// Repositories
builder.Services.AddScoped<GameStateRepository>();

// Services
builder.Services.AddScoped<IDailyGameService, DailyGameService>();

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();

app.MapControllers();

app.Run();