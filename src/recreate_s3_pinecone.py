from manage_s3_bucket import create_s3_data
from create_vector_db import create_pinecone


create_s3_data()
print('s3 done')
create_pinecone()
print('pc done')