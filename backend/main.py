import os
import json
from typing import List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "realtime_demo")
COLLECTION_NAME = "items"

app = FastAPI()

# CORS (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
items_collection = db[COLLECTION_NAME]


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class ItemBase(BaseModel):
    title: str = Field(..., example="Buy milk")
    completed: bool = Field(default=False)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None


class ItemDB(ItemBase):
    id: str


def item_serializer(doc) -> ItemDB:
    return ItemDB(
        id=str(doc["_id"]),
        title=doc["title"],
        completed=doc["completed"],
    )


async def get_all_items() -> List[ItemDB]:
    cursor = items_collection.find({})
    docs = await cursor.to_list(length=None)
    return [item_serializer(doc) for doc in docs]


# --- WebSocket connection manager ---

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # Broadcast to all clients, clean up dead connections if needed
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


async def broadcast_items():
    """Get current items and broadcast to all connected websocket clients."""
    items = await get_all_items()
    message = json.dumps(
        {
            "type": "items_updated",
            "payload": [item.dict() for item in items],
        }
    )
    await manager.broadcast(message)


# --- REST endpoints ---

@app.get("/items", response_model=List[ItemDB])
async def list_items():
    return await get_all_items()


@app.post("/items", response_model=ItemDB, status_code=201)
async def create_item(item: ItemCreate):
    result = await items_collection.insert_one(
        {"title": item.title, "completed": item.completed}
    )
    new_doc = await items_collection.find_one({"_id": result.inserted_id})
    serialized = item_serializer(new_doc)

    # notify all websocket clients
    await broadcast_items()

    return serialized


@app.put("/items/{item_id}", response_model=ItemDB)
async def update_item(item_id: str, item: ItemUpdate):
    update_data = {k: v for k, v in item.dict(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await items_collection.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": update_data},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    updated_doc = await items_collection.find_one({"_id": ObjectId(item_id)})
    serialized = item_serializer(updated_doc)

    # notify all websocket clients
    await broadcast_items()

    return serialized


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: str):
    result = await items_collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    # notify all websocket clients
    await broadcast_items()
    return


# --- WebSocket endpoint ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Optionally send current items immediately on connect
        items = await get_all_items()
        await websocket.send_text(
            json.dumps(
                {"type": "items_updated", "payload": [i.dict() for i in items]}
            )
        )

        # For this example, we don't expect messages from clients,
        # but we keep the connection open.
        while True:
            _ = await websocket.receive_text()
            # You can handle client messages here (e.g., ping/pong, commands)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
