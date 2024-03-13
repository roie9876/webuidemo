from azure.cosmos import CosmosClient, PartitionKey, exceptions
from flask import Flask, render_template, request
# Initialize Cosmos DB client
url = "https://roie-cosmos-vision.documents.azure.com:443/"
key = '1OwJMb2Zs6YuxUIXQIIoMeAmtskfDwNsFBOUKJWKuf2icQjChm2iYCZ82m5wpCUnkGe9I2VgQ0JVACDbh3ZS9g=='
client = CosmosClient(url, credential=key)
database_name = 'roie-cosmos-vision'
database = client.get_database_client(database_name)
container_name = 'gpt4vresults-db'
container = database.get_container_client(container_name)


app = Flask(__name__)
@app.route('/')
def index():
    # Fetch videos from Cosmos DB
    videos = list(container.query_items(
        query="SELECT * FROM c",
        enable_cross_partition_query=True
    ))

    # Render them in the UI
    return render_template('index.html', videos=videos)

@app.route('/video', methods=['POST'])
def add_video():
    # Add a new video to Cosmos DB
    video_data = request.get_json()
    container.upsert_item(video_data)

    return {'message': 'Video added'}, 201

if __name__ == '__main__':
    app.run()
