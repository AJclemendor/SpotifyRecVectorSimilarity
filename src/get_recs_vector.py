import os
import pinecone
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()


client_id = os.getenv("SPOTIFY_API_KEY")
client_secret = os.getenv("SPOTIFY_API_SECRET_KEY")
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)



pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index_name = "song-recommendations"

# Establish a connection with the Pinecone index
pinecone.init(api_key=pinecone_api_key, environment="us-west1-gcp")
index = pinecone.Index(index_name=pinecone_index_name)

# Define a query vector

def get_vector_recs(feats):
    query = feats

    # Perform a similarity search and return the top 10 most similar items
    results = index.query(queries=[query], top_k=10)
    results = results['results'][0]['matches']

    print("Top 10 song recommendations:")
    print("-" * 40)

    for i, item in enumerate(results, start=1):
        item_id = item['id']
        track = sp.track(item_id)
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        print(f"{i}. {track_name} by {artist_name}")

    print("-" * 40)
