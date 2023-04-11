import os
import re
import time
import lyricsgenius
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

GENIUS_API_KEY = os.getenv("GENIUS_API_KEY")
genius = lyricsgenius.Genius(GENIUS_API_KEY, timeout=10)  # Increase the timeout to 10 seconds -- was getting timeouted bc i had to make alot of cals

def clean_transcription(text):
    # Remove extra whitespace and special characters
    text = re.sub(r'\W+', ' ', text)
    return text.strip()

def calculate_confidence(input_lyrics, song_lyrics):
    input_words = set(input_lyrics.lower().split())
    song_words = set(song_lyrics.lower().split())
    common_words = input_words.intersection(song_words)
    return len(common_words) / len(input_words)

def search_song(lyrics):
    results = genius.search_lyrics(lyrics)
    print("Results:", results)  #  debugging purposes

    #  section w results
    song_section = None
    for section in results['sections']:
        if section['type'] == 'lyric':
            song_section = section
            break

    if song_section is not None:
        for hit in song_section['hits']:
            song_title = hit['result']['title']
            artist = hit['result']['primary_artist']['name']

            retries = 3
            while retries > 0:
                try:
                    song = genius.search_song(song_title, artist)
                    if song is not None:
                        song_lyrics = song.lyrics
                        # print(song_lyrics)
                        confidence = calculate_confidence(lyrics, song_lyrics)

                        # Return song title artist confidence
                        return song_title, artist, confidence
                except requests.exceptions.Timeout:
                    print("Request timed out. Retrying...")
                    retries -= 1
                    time.sleep(1)  # avoid genius api delay timeout

            # get lyrics + title w artist
            song = genius.search_song(song_title, artist)
            if song is not None:
                song_lyrics = song.lyrics
                confidence = calculate_confidence(lyrics, song_lyrics)


                return song_title, artist, confidence

    else:
        print("No song section found.")
        # Handle  no song  found
        return None, None, None

    #   no matching songs are found
    return None, None, None


def search_song_typed(lyrics):
    hits = []
    artists = []
    results = genius.search_lyrics(lyrics)
    for section in results['sections']:
        for hit in section['hits']:
            hits.append(hit['result']['title'])
            artists.append(hit['result']['primary_artist']['name'])

    return hits, artists

def load_lyrics(title):
    try:
        song = genius.search_song(title)
        return song.lyrics
    except TimeoutError:
        time.sleep(1)
        print("Try Again -- Note does not rlly try again")
        return None


if __name__ == "__main__":
    song_title = "Bohemian Rhapsody"
    print("Fetching lyrics for:", song_title)
    lyrics = load_lyrics(song_title)
    print(lyrics)
