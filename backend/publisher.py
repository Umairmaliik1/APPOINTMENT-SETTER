import os
base_dir = os.path.dirname(__file__)  # directory of this script
credentials_path = os.path.join(base_dir, "cred.json")
print(credentials_path)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
from google.cloud import pubsub_v1
from pubsub import pub

# Set path to your service account JSON file


# Define project and topic
project_id = "gen-lang-client-0194953633"
topic_id = "appointment-setter"

# Create a publisher client
publisher = pubsub_v1.PublisherClient()

# Construct the fully qualified topic path
topic_path = publisher.topic_path(project_id, topic_id)

# Prepare the message data
data = "Hello! You published me youre hook."
data = data.encode("utf-8")

# Publish the message
future = publisher.publish(topic_path, data)

# Wait for the result and print message ID
print(f"Published message ID: {future.result()}")

# def listen_alice(arg):
#     print(arg['headline'])
#     print(arg['news'])

# def listen_bob(arg):
#     print(arg['headline'])
#     print(arg['news'])

# pub.subscribe(listen_alice,'girl')
# pub.subscribe(listen_bob,'boy')

# pub.sendMessage('girl',arg={
#     'headline':'YOU ARE A GIRL.',
#     'news':'its a bad news'}
#     )