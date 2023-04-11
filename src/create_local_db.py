import os
import io
import pandas as pd
import boto3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
load_dotenv()

# Set up your Spotify API credentials
client_id = os.getenv("SPOTIFY_API_KEY")
client_secret = os.getenv("SPOTIFY_API_SECRET_KEY")

# Authenticate with the Spotify API
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Search for tracks and fetch their features
search_query = "genre:pop"  # Replace this with your desired search query
results = sp.search(q=search_query, type="track", limit=50)  # Limit can be a maximum of 50

# Extract track features and create a pandas DataFrame
tracks = results["tracks"]["items"]

track_ids = [track["id"] for track in tracks]
track_features = sp.audio_features(track_ids)

features_df = pd.DataFrame(track_features)

# Set up your AWS credentials
aws_access_key_id = os.getenv("AMAZON_ACCESS_KEY")
aws_secret_access_key = os.getenv("AMAZON_SECRET_ACCESS_KEY")

# Initialize the S3 client
s3 = boto3.client("s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Set the bucket_name and s3_key variables
bucket_name = "mysongdatabase"
s3_key = "spotify_song_features.csv"

# Save the DataFrame to a CSV file in memory
csv_buffer = io.StringIO()
features_df.to_csv(csv_buffer, index=False)

# Upload the CSV file to your S3 bucket
s3.put_object(
    Bucket=bucket_name,
    Key=s3_key,
    Body=csv_buffer.getvalue(),
    ContentType="text/csv",
)

# Read the CSV file back from the S3 bucket into a pandas DataFrame
metadata_obj = s3.get_object(Bucket=bucket_name, Key=s3_key)
metadata_file = metadata_obj["Body"].read().decode("utf-8")

features_df = pd.read_csv(io.StringIO(metadata_file), index_col=0)
