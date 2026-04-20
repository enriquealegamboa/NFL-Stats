using NFLBackend.Data;
using NFLBackend.Repositories;
using NFLBackend.Repositories.Interfaces;
using NFLBackend.Services;
using NFLBackend.Services.Interfaces;

var builder = WebApplication.CreateBuilder(args);

// Controllers + Swagger
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Supabase config
var url = builder.Configuration["SUPABASE_URL"];
var key = builder.Configuration["SUPABASE_SECRET_KEY"];

// Dependency Injection
builder.Services.AddSingleton(new SupabaseClientFactory(url, key));

builder.Services.AddScoped<IDailyGameRepository, DailyGameRepository>();
builder.Services.AddScoped<IDailyGameService, DailyGameService>();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseAuthorization();
app.MapControllers();

app.Run();