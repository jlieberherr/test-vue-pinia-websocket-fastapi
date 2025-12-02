import os
import json
from typing import List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# ----- Mongo setup -----

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "realtime_classes_courses")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
classes_collection = db["classes"]
courses_collection = db["courses"]

# ----- FastAPI app -----

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Pydantic models -----

class ClassBase(BaseModel):
    alias: str = Field(..., example="C1")

class ClassCreate(ClassBase):
    pass

class ClassUpdate(BaseModel):
    alias: Optional[str] = None

class ClassDB(ClassBase):
    id: str


class CourseBase(BaseModel):
    subject: str = Field(..., example="M")
    class_ids: List[str] = Field(default_factory=list)  # store class IDs as strings

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    subject: Optional[str] = None
    class_ids: Optional[List[str]] = None

class CourseDB(CourseBase):
    id: str


class DataPayload(BaseModel):
    classes: List[ClassDB]
    courses: List[CourseDB]


# ----- Serializers -----

def class_serializer(doc) -> ClassDB:
    return ClassDB(
        id=str(doc["_id"]),
        alias=doc["alias"],
    )

def course_serializer(doc) -> CourseDB:
    return CourseDB(
        id=str(doc["_id"]),
        subject=doc["subject"],
        class_ids=[str(cid) for cid in doc.get("class_ids", [])],
    )

async def get_all_data() -> DataPayload:
    class_docs = await classes_collection.find({}).to_list(length=None)
    course_docs = await courses_collection.find({}).to_list(length=None)
    return DataPayload(
        classes=[class_serializer(c) for c in class_docs],
        courses=[course_serializer(c) for c in course_docs],
    )

# ----- WebSocket connection manager -----

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
        for ws in list(self.active_connections):
            try:
                await ws.send_text(message)
            except Exception:
                self.disconnect(ws)

manager = ConnectionManager()

async def broadcast_data():
    data = await get_all_data()
    msg = json.dumps({
        "type": "data_updated",
        "payload": data.dict(),
    })
    await manager.broadcast(msg)

# ----- Optional: seed initial data on startup -----

@app.on_event("startup")
async def seed_initial_data():
    # Only seed if both collections are empty
    if await classes_collection.count_documents({}) == 0 and await courses_collection.count_documents({}) == 0:
        # Create classes C1, C2, C3
        class_result = await classes_collection.insert_many(
            [
                {"alias": "C1"},
                {"alias": "C2"},
                {"alias": "C3"},
            ]
        )
        c1, c2, c3 = class_result.inserted_ids

        # Create courses using the inserted class IDs
        await courses_collection.insert_many(
            [
                {"subject": "M", "class_ids": [c1, c2]},
                {"subject": "F", "class_ids": [c1]},
                {"subject": "D", "class_ids": [c2, c3]},
            ]
        )

# ----- REST endpoints -----

@app.get("/data", response_model=DataPayload)
async def get_data():
    return await get_all_data()

# -- classes --

@app.get("/classes", response_model=List[ClassDB])
async def list_classes():
    docs = await classes_collection.find({}).to_list(length=None)
    return [class_serializer(d) for d in docs]

@app.put("/classes/{class_id}", response_model=ClassDB)
async def update_class(class_id: str, payload: ClassUpdate):
    update_data = {k: v for k, v in payload.dict(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await classes_collection.update_one(
        {"_id": ObjectId(class_id)},
        {"$set": update_data},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Class not found")

    doc = await classes_collection.find_one({"_id": ObjectId(class_id)})
    serialized = class_serializer(doc)
    await broadcast_data()
    return serialized

# -- courses --

@app.get("/courses", response_model=List[CourseDB])
async def list_courses():
    docs = await courses_collection.find({}).to_list(length=None)
    return [course_serializer(d) for d in docs]

@app.put("/courses/{course_id}", response_model=CourseDB)
async def update_course(course_id: str, payload: CourseUpdate):
    update_data = {}
    if payload.subject is not None:
        update_data["subject"] = payload.subject
    if payload.class_ids is not None:
        # store class IDs as ObjectId in Mongo
        update_data["class_ids"] = [ObjectId(cid) for cid in payload.class_ids]

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await courses_collection.update_one(
        {"_id": ObjectId(course_id)},
        {"$set": update_data},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Course not found")

    doc = await courses_collection.find_one({"_id": ObjectId(course_id)})
    serialized = course_serializer(doc)
    await broadcast_data()
    return serialized

# ----- WebSocket -----

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # send current data immediately
        data = await get_all_data()
        await websocket.send_text(json.dumps({
            "type": "data_updated",
            "payload": data.dict(),
        }))

        # keep connection open (we don't process client messages for now)
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/reset-data")
async def reset_data():
    # delete everything
    await classes_collection.delete_many({})
    await courses_collection.delete_many({})

    # insert classes
    result = await classes_collection.insert_many([
        {"alias": "C1"},
        {"alias": "C2"},
        {"alias": "C3"},
    ])
    c1, c2, c3 = result.inserted_ids

    # insert courses
    await courses_collection.insert_many([
        {"subject": "M", "class_ids": [c1, c2]},
        {"subject": "F", "class_ids": [c1]},
        {"subject": "D", "class_ids": [c2, c3]},
    ])

    return {"status": "OK", "message": "Database reset and seeded."}
