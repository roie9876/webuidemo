# Import necessary modules from azure.cosmos and flask
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from flask import Flask, render_template, request

# Initialize Cosmos DB client
# url is the endpoint of the Cosmos DB
url = "https://roie-cosmos-vision.documents.azure.com:443/"
# key is the primary key for the Cosmos DB
key = '1OwJMb2Zs6YuxUIXQIIoMeAmtskfDwNsFBOUKJWKuf2icQjChm2iYCZ82m5wpCUnkGe9I2VgQ0JVACDbh3ZS9g=='
# Create a CosmosClient using the url and key
client = CosmosClient(url, credential=key)

# Define the database name and get the database client
database_name = 'gpt4vresults-db'
database = client.get_database_client(database_name)

# Define the container name and get the container client
container_name = 'gptoutput'
container = database.get_container_client(container_name)

# Initialize Flask app
app = Flask(__name__)

# Define the route for the index page
@app.route('/')
def index():
    # Fetch videos from Cosmos DB
    # Query all items in the container
    videos = list(container.query_items(
        query="SELECT * FROM c",
        enable_cross_partition_query=True
    ))

    # Render them in the UI
    # Pass the videos to the index.html template
    return render_template('index.html', videos=videos)

# Define the route for adding a video, only accessible via POST
@app.route('/video', methods=['POST'])
def add_video():
    # Add a new video to Cosmos DB
    # Get the video data from the request's JSON
    video_data = request.get_json()
    # Upsert the item (insert if not exists, update if exists) in the container
    container.upsert_item(video_data)

    # Return a success message
    return {'message': 'Video added'}, 201

# Run the Flask app
if __name__ == '__main__':
    app.run()