import os
from flask import Flask,request
from livekit import api
from livekit.api import LiveKitApi,ListRoomsRequest
from dotenv import load_dotenv
from flask_cors import CORS
import uuid


load_dotenv()
app=Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  

async def generate_room_name():
    name="room-"+str(uuid.uuid4())[:8]
    rooms=get_rooms()
    while name in rooms:
        name="room-"+str(uuid.uuid4())[:8]

    return name 

async def get_rooms():
    rooms=await api.room.list_rooms(ListRoomsRequest())
    await api.aclose
    return [room.name for room in rooms.rooms]
@app.route("/getToken")
async def get_token():
    room=request.args.get("room",None)

    if not room:
        room= await generate_room_name()

    token=api.AccessToken(os.getenv("LiveKit_APIKey"),os.getenv("LiveKit_Secret")) \
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room
                )
            )
    return token.to_jwt()

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

