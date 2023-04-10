import os
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from find_song_live_audio import live_speech_rec
from genius_get_song import search_song_typed

load_dotenv()

client_id = os.getenv("SPOTIFY_API_KEY")
client_secret = os.getenv("SPOTIFY_API_SECRET_KEY")
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def recommend_off_current():

    """
    Sentiment on the current song so get a few things like
    Mood, Genre, Artist
    Ask if they want to find any songs that are the same or allow them to change

    :return:
    """
    song_title, artist = live_speech_rec()

    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    print(f"Searching for song: {song_title}, artist: {artist}")

    results = sp.search(q=f"track: {song_title} {artist}", type="track", limit=10)

    print(results)
    if not results["tracks"]["items"]:
        print("No results found for the given song and artist.")
        return

    track_id = results["tracks"]["items"][0]["id"]
    features = sp.audio_features(track_id)[0]

    # print("Spotify track ID:", track_id)
    # print("Danceability:", features["danceability"])
    # print("Energy:", features["energy"])
    # print("Key:", features["key"])
    # print("Loudness:", features["loudness"])
    # print("Mode:", features["mode"])
    # print("Speechiness:", features["speechiness"])
    # print("Acousticness:", features["acousticness"])
    # print("Instrumentalness:", features["instrumentalness"])
    # print("Liveness:", features["liveness"])
    # print("Valence:", features["valence"])
    # print("Tempo:", features["tempo"])

    return features, track_id

def get_top_songs(genres, limit=50, num_songs=1000):
    genre_query = " OR ".join(f"genre:{genre}" for genre in genres)
    all_songs = []
    for offset in range(0, num_songs, limit):
        results = sp.search(q=genre_query, type="track", limit=limit, offset=offset)
        all_songs.extend(results["tracks"]["items"])
    return all_songs

def get_spotify_recommendations(track_id, sp, limit=5):
    seed_tracks = [track_id]
    recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=limit)

    recommended_tracks = []
    for track in recommendations["tracks"]:
        recommended_tracks.append({
            "song": track["name"],
            "artist": track["artists"][0]["name"],
            "id": track["id"]
        })

    return recommended_tracks

def recommend_off_current_typed(title, artist):

    """
    Sentiment on the current song so get a few things like
    Mood, Genre, Artist
    Ask if they want to find any songs that are the same or allow them to change

    :return:
    """
    song_title = title
    artist = artist

    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    print(f"Searching for song: {song_title}, artist {artist}")
    results = sp.search(q=f"track: {song_title} {artist}", type="track", limit=10)

    # print(results)
    if not results["tracks"]["items"]:
        print("No results found for the given song and artist.")
        return

    track_id = results["tracks"]["items"][0]["id"]
    features = sp.audio_features(track_id)[0]

    # print("Spotify track ID:", track_id)
    # print("Danceability:", features["danceability"])
    # print("Energy:", features["energy"])
    # print("Key:", features["key"])
    # print("Loudness:", features["loudness"])
    # print("Mode:", features["mode"])
    # print("Speechiness:", features["speechiness"])
    # print("Acousticness:", features["acousticness"])
    # print("Instrumentalness:", features["instrumentalness"])
    # print("Liveness:", features["liveness"])
    # print("Valence:", features["valence"])
    # print("Tempo:", features["tempo"])

    return features, track_id

def print_recommendations(recommendations):
    print("\nRecommended Songs:")
    print("-" * 40)
    for idx, track in enumerate(recommendations, start=1):
        print(f"{idx}. '{track['song']}' by {track['artist']}")
        print(f"   Spotify track ID: {track['id']}")
        print("-" * 40)


if __name__ == '__main__':
    type_or_sing = int(input("Type (1) or Sing (2) for input"))
    while True:
        if type_or_sing == 1:
            lyrics = input("What Lyrics do you remember?")
            titles, artists = search_song_typed(lyrics)
            found_correct_song = False
            for i in range(len(titles)):
                print(titles[i], artists[i])
                which = input("Does This Look Right??")
                if which.lower() == 'yes':
                    features, track_id = recommend_off_current_typed(titles[i], artists[i])

                    recommendations = get_spotify_recommendations(track_id, sp)

                    print_recommendations(recommendations)
                    found_correct_song = True
                    break

            if found_correct_song:
                break
            else:
                print("Let's try again.")
        else:
            features, track_id = recommend_off_current()
            recommendations = get_spotify_recommendations(track_id, sp)
            print_recommendations(recommendations)
            break
