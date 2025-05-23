import os
from google.cloud import pubsub_v1
from langchain.tools import tool


base_dir = os.path.dirname(__file__)  # directory of this script
credentials_path = os.path.join(base_dir, "cred.json")
print(credentials_path)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path


@tool
def publish_data(name,email,doc_category,datetime)->str:
    project_id = "gen-lang-client-0194953633"
    topic_id = "appointment-setter"
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    attribute={
        'name':name,
        'email':email,
        'doc_category':doc_category,
        'datetime':datetime
    }
    future = publisher.publish(topic_path, **attribute)
    return f"Data Published{future.result()}."
