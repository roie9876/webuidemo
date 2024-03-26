#python3 -m venv .venv
#source .venv/bin/activate
#pip3 install streamlit
import os
import re
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.http_constants import StatusCodes
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos import CosmosClient, PartitionKey
#import openai
from openai import AzureOpenAI
import streamlit as st
import urllib.parse

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os

# Create a BlobServiceClient object

connection_string = os.getenv("BLOB_CONNECTION_STRING")
blob_service_client = BlobServiceClient.from_connection_string(connection_string)




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
#QUERY = "SELECT c.content, c.filename, c.shortdate FROM c"
#results = container.query_items(
#    query=QUERY, enable_cross_partition_query=True
#)

#items = [item for item in results]
import re

QUERY = "SELECT c.content, c.filename, c.shortdate FROM c"
results = container.query_items(
    query=QUERY, enable_cross_partition_query=True
)

items = [item for item in results]

# Filter items where 'DangerProbability[Num]' exists in 'content' and 'Num' is greater than 8
filtered_items = []
for item in items:
    match = re.search(r'DangerProbability\[(\d+)\]', item['content'])
    if match and int(match.group(1)) > 3:
        filtered_items.append(item)




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


token = os.getenv("TOKEN")

filtered_videos = []
for video in videos:
    content = video['content']
    match = re.search(r'DangerProbability\[(\d+)\]', content)
    if match and int(match.group(1)) > 3:
        filtered_videos.append(video)

# Initialize an empty string
aggregated_content = ""

for video in filtered_videos:
     # Append the video's content to the aggregated_content string
    aggregated_content += video['content'] + " "
 

# Add the user's question as a user message in the conversation
conversation =[{"role": "system", "content":"״אתה עומד לקבל טקסטים ממספר אירועים שונים, כל אירוע יכול להיות עצמאי או קשור לאירוע אחר. האירועים הם תיעוד שמגיע ממצלמות שונות ומיקומים שונים, עליך לקבוע האם יש קשר בין האירועים על פי סמיכות זמנים, מקום, תיאור האירוע ולעשות הערכת מצב. במידה ואתה מזהה שיש קשר בין האירועים תסביר מדוע ומה צריך לעשות על מנת להפחית את הסיכון" }]
conversation.append({"role": "user", "content": aggregated_content})

response = client.chat.completions.create(
model="gpt-4-32k", # model = "deployment_name".

messages=conversation,
temperature=0
         )

# Append the assistant's response to the conversation
conversation.append({"role": "assistant", "content": response.choices[0].message.content})

#st.write(response.choices[0].message.content)
st.markdown(f'<div style="background-color:yellow;">{response.choices[0].message.content}</div>', unsafe_allow_html=True)


for video in filtered_videos:
     # Append the video's content to the aggregated_content string
    aggregated_content += video['content'] + " "
    # Get the filename of the video
    filename = video['filename']
    filename = urllib.parse.quote(filename)
    # Build the full URL of the video
    url = 'https://videostoragedemo.blob.core.windows.net/videosprocessed/reviewfordamage/' + filename + token

    # Display the video details
    st.write(video)# Display a video player for the video

    # Build the full URL of the video
    url = 'https://videostoragedemo.blob.core.windows.net/videosprocessed/reviewfordamage/' + filename + token
    st.video(url)