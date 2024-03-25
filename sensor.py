import cv2
import os 
import numpy as np
import threading
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import datetime

# define a video capture object
vid = cv2.VideoCapture(0)
location = "camera-1"
# initialize frame variable
frame1 = None

# Define the desired resolution
desired_width = 1280
desired_height = 720

# Define the frame rate and the duration of each video file
frame_rate = 20.0
duration = 10  # seconds

# Initialize the counter and the video file index
counter = 0
index = 0

# Azure storage details
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

# Function to upload file to Azure
def upload_to_azure(file_name):
    print(f"Uploading {file_name} to Azure Blob Storage")  # print the name of the file being uploaded
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container_name, file_name)
    with open(file_name, "rb") as data:
        blob_client.upload_blob(data)

try:
    while True:
        # Capture the video frame by frame
        ret, frame = vid.read()

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # if the first frame is None, initialize it
        if frame1 is None:
            frame1 = gray
            continue

        # compute the absolute difference between the current and previous frame
        frameDelta = cv2.absdiff(frame1, gray)

        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        # if the frame has a considerable amount of difference then there is motion
        if np.count_nonzero(thresh) > 500:
            # Resize the frame
            resized_frame = cv2.resize(frame, (desired_width, desired_height))

            # Get the current date and time
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            timestamp_location = f"{timestamp}, {location}"

            # Define the font and scale
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.5  # Increase or decrease this value to change the font size

            # Define the color and thickness
            color = (255, 255, 255)  # White color
            thickness = 2

            # Add the timestamp to the frame
            # Add the timestamp to the frame
            cv2.putText(resized_frame, timestamp_location, (10, 50), font, font_scale, color, thickness)

            # If the VideoWriter is not yet created, or if the counter has reached the limit, create a new one
            if 'out' not in locals() or counter >= frame_rate * duration:  # if 'out' is not yet defined or if counter has reached the limit
                if 'out' in locals():  # if 'out' is defined, release it
                    out.release()

                    # Start a new thread to upload the file to Azure
                    threading.Thread(target=upload_to_azure, args=(filename,)).start()

                # Define the codec and create VideoWriter object
                # Convert the timestamp to a format suitable for a filename
                timestamp_filename = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

                # Replace any special characters in the location that are not allowed in a filename
                location_filename = location.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")

                # Create the filename
                filename = f"{location_filename}_{timestamp_filename}q_{index}.mp4"

                # Define the codec and create VideoWriter object
                fourcc = cv2.VideoWriter_fourcc(*'H264')
                out = cv2.VideoWriter(filename, fourcc, frame_rate, (desired_width, desired_height))
                #fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                #out = cv2.VideoWriter(f'output{index}.mp4', fourcc, frame_rate, (desired_width, desired_height))

                # Reset the counter and increment the index
                counter = 0
                index += 1

            # write the resized frame
            out.write(resized_frame)

            # Increment the counter
            counter += 1

        # Update frame1 to the current frame
        frame1 = gray

        # Display the resulting frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # After the loop release the cap object
    vid.release()
    if 'out' in locals():  # if 'out' is defined
        out.release()

    # Destroy all the windows
    cv2.destroyAllWindows()