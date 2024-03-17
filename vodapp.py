#python3 -m venv .venv
#source .venv/bin/activate
#pip3 install streamlit
import os
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.http_constants import StatusCodes
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos import CosmosClient, PartitionKey

from openai import AzureOpenAI
import streamlit as st

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# Create a BlobServiceClient object

connection_string = os.getenv("BLOB_CONNECTION_STRING")
blob_service_client = BlobServiceClient.from_connection_string(connection_string)


#upload file to blob 
container_client_videoin = blob_service_client.get_container_client("videosin")

# List all blobs in the container
blob_list = container_client_videoin.list_blobs()

# Display blobs in the UI
for blob in blob_list:
    st.write(blob.name)

# File uploader widget
uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    # Create a blob client for the uploaded file
    blob_client = blob_service_client.get_blob_client("videosin", uploaded_file.name)

    # Upload the file to the blob storage
    blob_client.upload_blob(uploaded_file)




connection_string = os.getenv("BLOB_CONNECTION_STRING")
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Get a reference to the container
container_client = blob_service_client.get_container_client("videosprocessed")

# List all blobs in the container
blob_list = container_client.list_blobs()
#for blob in blob_list:
#    print(blob.name)

# </imports>

# <environment_variables>
ENDPOINT = os.getenv("ENDPOINT")
KEY = os.getenv("KEY")


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





client = AzureOpenAI(
  api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version = "2023-05-15",
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")  # Your Azure OpenAI resource's endpoint value.
)

conversation=[{"role": "system", "content": "You are a helpful assistant."}]

# Assume `videos` is a list of dictionaries, each representing a video
videos = container.query_items(
    query=QUERY, enable_cross_partition_query=True
)
token= "?sp=r&st=2024-03-14T13:08:37Z&se=2024-08-13T20:08:37Z&spr=https&sv=2022-11-02&sr=c&sig=SSYTXamsqgvav3oqlEYrSw3tLBQOfE%2FjPeSkgKqq47M%3D"

token= "?sp=r&st=2024-03-14T13:08:37Z&se=2024-08-13T20:08:37Z&spr=https&sv=2022-11-02&sr=c&sig=SSYTXamsqgvav3oqlEYrSw3tLBQOfE%2FjPeSkgKqq47M%3D"

# Get the user's question about the content
user_question = st.text_input("Ask a question about the content:")

for video in videos:
    # Get the filename of the video
    filename = video['filename']

    # Build the full URL of the video
    url = 'https://roiestoragevision.blob.core.windows.net/videosprocessed/reviewfordamage/' + filename + token

    # Display the video details
    st.write(video)

    # Display a video player for the video
    st.video(url)

    # Get the content of the video
    content = video['content']

    # Display the content
    #st.write(content)

    if user_question:
        # Add the user's question as a user message in the conversation
        {"role": "system", "content": "אתה תקבל טקסט שמתאר סרטון וידאו עליך לענות על שאלות מתוך הטקטס'"},
        conversation.append({"role": "user", "content": user_question+" "+content})

        response = client.chat.completions.create(
            model="gt4", # model = "deployment_name".
            messages=conversation
        )

        conversation.append({"role": "assistant", "content": response.choices[0].message.content})

        # Display the assistant's response
        st.write(response.choices[0].message.content)