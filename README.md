# webuidemo
from azure.cosmos import CosmosClient, PartitionKey, exceptions

url = "https://roie-cosmos-vision.documents.azure.com:443/"
key = '1OwJMb2Zs6YuxUIXQIIoMeAmtskfDwNsFBOUKJWKuf2icQjChm2iYCZ82m5wpCUnkGe9I2VgQ0JVACDbh3ZS9g=='
client = CosmosClient(url, credential=key)
database_name = 'roie-cosmos-vision'
database = client.get_database_client(database_name)
container_name = 'gpt4vresults-db'
container = database.get_container_client(container_name)

from flask import Flask, send_file, abort
app = Flask(__name__)

@app.route('/video/<id>')
def get_video(id):
    try:
        video_item = container.read_item(item=id, partition_key=id)
        return send_file(video_item['filePath'], mimetype='video/mp4')
    except exceptions.CosmosResourceNotFoundError:
        abort(404)

if __name__ == '__main__':
    app.run()
