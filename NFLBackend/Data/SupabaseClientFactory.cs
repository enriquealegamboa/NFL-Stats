namespace NFLBackend.Data;
using Supabase;

public class SupabaseClientFactory
{
    public Client Client { get; }

    public SupabaseClientFactory(string url, string key)
    {
        Client = new Client(url, key);
        Client.InitializeAsync().Wait();
    }
}