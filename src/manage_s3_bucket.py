import os
import io
import pandas as pd
import boto3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
load_dotenv()


client_id = os.getenv("SPOTIFY_API_KEY")
client_secret = os.getenv("SPOTIFY_API_SECRET_KEY")
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

aws_access_key_id = os.getenv("AMAZON_ACCESS_KEY")
aws_secret_access_key = os.getenv("AMAZON_SECRET_ACCESS_KEY")

def create_s3_data():
    genres = ["pop", "rock", "hip-hop", "country", "jazz", "classical", "electronic", "reggae", "blues", "metal",
              "pop rap", "trap", "pop dance", "dance pop", "rap", "hip hop", "edm", "latin pop", "trap latino",
              "post-teen pop", "tropical house", "southern hip hop", "indie pop", "gangster rap", "alt z",
              "atl hip hop", "colombian pop", "j-pop", "underground hip hop", "canadian contemporary r&b",
              "k-pop boy group", "chicago rap", "hip pop", "conscious hip hop", "stomp and holler", "toronto rap",
              "alternative hip hop", "emo rap", "miami hip hop", "desi hip hop", "argentine hip hop", "mexican hip hop"]

    limit = 50
    total_songs_per_genre = 200

    all_track_info = []

    for genre in genres:
        search_query = f"genre:{genre}"
        for offset in range(0, total_songs_per_genre, limit):
            results = sp.search(q=search_query, type="track", limit=limit, offset=offset)
            tracks = results["tracks"]["items"]
            track_ids = [track["id"] for track in tracks]
            track_features = sp.audio_features(track_ids)
            valid_track_features = [tf for tf in track_features if tf is not None]  # Filter out None values

            # Extract genre information for each track
            for track, features in zip(tracks, valid_track_features):
                if features:
                    track_info = features
                    track_info["genre"] = genre
                    all_track_info.append(track_info)

    # Add genre information to the features_df DataFrame
    features_df = pd.DataFrame(all_track_info,
                               columns=['id', 'genre', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                                        'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo'])
    # features_df.drop(columns=['id'], inplace=True)

    # S3 client
    s3 = boto3.client("s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    # Set the bucket_name and s3_key variables
    bucket_name = "mysongdatabase"
    s3_key = "spotify_song_features.csv"

    # Save the DataFrame to a CSV file in memory
    csv_buffer = io.StringIO()
    features_df.to_csv(csv_buffer, index=False)

    # Upload the CSV file to your S3 bucket, replacing the existing file
    s3.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=csv_buffer.getvalue(),
        ContentType="text/csv",
    )

    # Read the CSV file back from the S3 bucket into a pandas DataFrame
    metadata_obj = s3.get_object(Bucket=bucket_name, Key=s3_key)
    metadata_file = metadata_obj["Body"].read().decode("utf-8")

    weight_dict = {
        'danceability': 3.0,
        'energy': 9.0,
        'key': 3.0,
        'loudness': 1.0,
        'mode': 1.0,
        'speechiness': 2.0,
        'acousticness': 2.0,
        'instrumentalness': 1.0,
        'liveness': 3.0,
        'valence': 1.0,
        'tempo': 4.0,
        'genre': 50
    }

    for feature, weight in weight_dict.items():
        if feature != 'genre':
            features_df[feature] *= weight

    features_df = pd.read_csv(io.StringIO(metadata_file), index_col=0)


if __name__ == '__main__':
    create_s3_data()