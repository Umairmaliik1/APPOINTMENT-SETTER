import os
base_dir = os.path.dirname(__file__)  # directory of this script
credentials_path = os.path.join(base_dir, "cred.json")
print(credentials_path)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
from google.cloud import pubsub_v1


project_id = "gen-lang-client-0194953633"
topic_id = "appointment-setter"


subscriber=pubsub_v1.SubscriberClient()
subscription_path="projects/gen-lang-client-0194953633/subscriptions/appointment-setter-sub"
# Construct the fully qualified topic path
topic_path = subscriber.topic_path(project_id, topic_id)

def callback(message):
    print(f"Received msg{message}")
    print(f"data:{message.data}")
    message.ack()

streaming_pull_future=subscriber.subscribe(subscription_path,callback=callback)

with subscriber:
    try:
        streaming_pull_future.result()
    except:
        streaming_pull_future.cancel()
        streaming_pull_future.result()
