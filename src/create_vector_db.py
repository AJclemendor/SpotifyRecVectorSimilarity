import os
import pandas as pd
import boto3
import io
from dotenv import load_dotenv
import pinecone

load_dotenv()

aws_access_key_id = os.getenv("AMAZON_ACCESS_KEY")
aws_secret_access_key = os.getenv("AMAZON_SECRET_ACCESS_KEY")
s3 = boto3.client("s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
bucket_name = "mysongdatabase"
s3_key = "spotify_song_features.csv"

metadata_obj = s3.get_object(Bucket=bucket_name, Key=s3_key)
metadata_file = metadata_obj["Body"].read().decode("utf-8")
features_df = pd.read_csv(io.StringIO(metadata_file))

pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone.init(api_key=pinecone_api_key)

pinecone_index_name = "song-recommendations"

# create an index
pinecone.create_index(name=pinecone_index_name, dimension=features_df.shape[1] - 2, metric="euclidean", shards=1)

def create_pinecone(batch_size=1000):
    song_ids = features_df["id"].tolist()
    # exclude the "genre" column when preparing song_vectors -- would get weird rating and pinecone doesnt give WAB
    song_vectors = features_df.drop(["id", "genre"], axis=1).values.tolist()
    song_data = dict(zip(song_ids, song_vectors))

    # upsert the song_data into the pinecone index
    with pinecone.Index(index_name=pinecone_index_name) as index:
        # split data into batches and upload them by parts
        for i in range(0, len(song_ids), batch_size):
            batch_ids = song_ids[i:i+batch_size]
            batch_vectors = song_vectors[i:i+batch_size]
            batch_data = dict(zip(batch_ids, batch_vectors))
            vectors = [(song_id, song_vector) for song_id, song_vector in batch_data.items()]
            index.upsert(vectors=vectors)


if __name__ == '__main__':
    create_pinecone()
