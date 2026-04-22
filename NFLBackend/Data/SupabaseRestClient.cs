using System.Net.Http.Headers;

namespace NFLBackend.Data;

public class SupabaseRestClient
{
    private readonly HttpClient _http;

    private readonly string _url;
    private readonly string _key;

    public SupabaseRestClient(IConfiguration config)
    {
        _url = config["SUPABASE_URL"]!;
        _key = config["SUPABASE_SECRET_KEY"]!;

        _http = new HttpClient();
        _http.BaseAddress = new Uri(_url);

        _http.DefaultRequestHeaders.Add("apikey", _key);
        _http.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", _key);
    }

    public async Task<string> GetAsync(string path)
    {
        var response = await _http.GetAsync($"/rest/v1/{path}");
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadAsStringAsync();
    }
}