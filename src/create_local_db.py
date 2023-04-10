import json
import os

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

client_id = os.getenv("SPOTIFY_API_KEY")
client_secret = os.getenv("SPOTIFY_API_SECRET_KEY")
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_top_songs_by_genre(genre, limit=50, num_songs=1000):
    all_songs = []
    for offset in range(0, num_songs, limit):
        results = sp.search(q=f"genre:{genre}", type="track", limit=limit, offset=offset)
        all_songs.extend(results["tracks"]["items"])
    return all_songs


genres = ["rap", "hip-hop", "trap", "gangsta-rap", "underground-hip-hop", "old-school-hip-hop", "alternative-hip-hop",
          "conscious-hip-hop", "rap", "hip-hop", "trap", "gangsta-rap", "underground-hip-hop", "old-school-hip-hop",
          "alternative-hip-hop", "conscious-hip-hop", "boom-bap", "jazz-rap", "hardcore-hip-hop", "experimental-hip-hop",
          "west-coast-hip-hop", "east-coast-hip-hop", "southern-hip-hop", "crunk", "hyphy", "grime", "horrorcore", "g-funk"]
all_songs = []

for genre in genres:
    print(f"Fetching songs for genre: {genre}")
    genre_songs = get_top_songs_by_genre(genre)
    all_songs.extend(genre_songs)

print(f"Fetched {len(all_songs)} songs.")

# Save fetched songs to a JSON file
with open("songs.json", "w") as f:
    json.dump(all_songs, f, indent=2)
