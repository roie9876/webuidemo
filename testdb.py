#python3 -m venv .venv
#source .venv/bin/activate
#pip3 install streamlit
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.http_constants import StatusCodes
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos import CosmosClient, PartitionKey
import streamlit as st

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# Create a BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=roiestoragevision;AccountKey=BMxvrmMk1Ng+zNg/QJblbhDwd/qXHJGKpVCcuF1t+p6enTw3Ohy7ku/LXOY2Tfjf1BdddGqw2VOR+AStZviCmg==;EndpointSuffix=core.windows.net")

# Get a reference to the container
container_client = blob_service_client.get_container_client("videosprocessed")

# List all blobs in the container
blob_list = container_client.list_blobs()
#for blob in blob_list:
#    print(blob.name)

# </imports>

# <environment_variables>
ENDPOINT = "https://roie-cosmos-vision.documents.azure.com:443/"
KEY = "1OwJMb2Zs6YuxUIXQIIoMeAmtskfDwNsFBOUKJWKuf2icQjChm2iYCZ82m5wpCUnkGe9I2VgQ0JVACDbh3ZS9g=="

#ENDPOINT = os.environ["https://roie-cosmos-vision.documents.azure.com:443/"]
#KEY = os.environ["1OwJMb2Zs6YuxUIXQIIoMeAmtskfDwNsFBOUKJWKuf2icQjChm2iYCZ82m5wpCUnkGe9I2VgQ0JVACDbh3ZS9g=="]
# </environment_variables>

# <constants>
DATABASE_NAME = "gpt4vresults-db"
CONTAINER_NAME = "gptoutput"
# </constants>


# <create_client>
client = CosmosClient(url=ENDPOINT, credential=KEY)
# </create_client>


# <create_database>
database = client.create_database_if_not_exists(id=DATABASE_NAME)
#print("Database\t", database.id)
# </create_database>

# <create_partition_key>
key_path = PartitionKey(path="/categoryId")
# </create_partition_key>

# <create_container>
container = database.create_container_if_not_exists(
    id=CONTAINER_NAME, partition_key=key_path, offer_throughput=400
)
#print("Container\t", container.id)
# </create_container>

# <build_query>
QUERY = "SELECT c.content, c.filename, c.shortdate FROM c"
results = container.query_items(
    query=QUERY, enable_cross_partition_query=True
)

items = [item for item in results]

import streamlit as st
#st.write(items)
import streamlit as st

# Assume `videos` is a list of dictionaries, each representing a video
videos = container.query_items(
    query=QUERY, enable_cross_partition_query=True
)
token= "?sp=r&st=2024-03-14T13:08:37Z&se=2024-08-13T20:08:37Z&spr=https&sv=2022-11-02&sr=c&sig=SSYTXamsqgvav3oqlEYrSw3tLBQOfE%2FjPeSkgKqq47M%3D"

for video in videos:
    # Get the filename of the video
    filename = video['filename']

    # Build the full URL of the video
    url = 'https://roiestoragevision.blob.core.windows.net/videosprocessed/reviewfordamage/' + filename + token

    # Display the video details
    st.write(video)

    # Display a video player for the video
    st.video(url)

#output = json.dumps(items, indent=True)
#print("Result list\t", output)
# </iterate_query_results>
