# 🟦 Realtime Todo App  
### Vue 3 + TypeScript + Pinia + FastAPI + WebSockets + MongoDB

This project is a complete realtime application built with:

- **Frontend:** Vue 3, TypeScript, Pinia  
- **Backend:** FastAPI (Python)  
- **Realtime:** WebSockets (live sync between all clients)  
- **Database:** MongoDB (NoSQL)

The example implements a realtime Todo List where all connected browsers update instantly when data changes.

---

## 📁 Project Structure

project/
│
├─ backend/              # FastAPI backend
│   ├─ main.py
│   └─ requirements.txt
│
└─ frontend/             # Vue 3 + TypeScript frontend
    ├─ src/
    │   ├─ stores/items.ts
    │   ├─ App.vue
    │   └─ main.ts
    └─ package.json

---

# 🚀 1. Backend Setup (FastAPI + MongoDB)

## 1.1 Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

## 1.2 MongoDB Setup

### Option A — Install MongoDB locally

Install MongoDB Community Server and ensure the service is running.

### Option B — Using Docker

```bash
docker run -d -p 27017:27017 --name mongodb mongo
```

---

## 1.3 Run the backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Available endpoints

| Method | Endpoint        | Description |
|--------|-----------------|-------------|
| GET    | `/items`        | Get all items |
| POST   | `/items`        | Create item |
| PUT    | `/items/{id}`   | Update item |
| DELETE | `/items/{id}`   | Delete item |
| WS     | `/ws`           | WebSocket realtime stream |

---

# 🖥️ 2. Frontend Setup (Vue 3 + TS + Pinia)

## 2.1 Install dependencies

```bash
cd frontend
npm install
```

## 2.2 Run the dev server

```bash
npm run dev
```

Default URL:

```
http://localhost:5173
```

Ensure backend runs at:

```
http://localhost:8000
```

---

# 🔌 3. Realtime Sync (How It Works)

- Clients connect to the WebSocket endpoint `/ws`
- When any user creates/updates/deletes an item:
  - Backend updates MongoDB
  - Backend broadcasts `"items_updated"` to all clients
  - Pinia store updates instantly

No refresh required.

---

# 🔧 4. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGO_URL` | `mongodb://localhost:27017` | MongoDB connection string |
| `DB_NAME` | `realtime_demo` | MongoDB database |

Use a `.env` file or system variables if desired.

---

# 🔒 5. CORS Configuration

Backend must allow your frontend origin:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For development trouble, you may temporarily use:

```python
allow_origins=["*"]
```

---

# 🧪 6. Testing

1. Start backend  
2. Start frontend  
3. Open **two** browser windows at:

```
http://localhost:5173
```

4. Add/toggle/delete todos → both windows update instantly.

---

# 🛠️ 7. Useful Commands

### Stop and remove MongoDB container

```bash
docker stop mongodb && docker rm mongodb
```

### Clean install frontend deps

```bash
rm -rf node_modules
npm install
```

---

# 🧩 8. Tech Stack Overview

### Frontend
- Vue 3 (Composition API)
- TypeScript
- Pinia (state management)
- WebSockets (live updates)
- Vite

### Backend
- FastAPI
- Motor (MongoDB async driver)
- Pydantic models
- WebSocket broadcast manager

### Database

```json
{
  "_id": "642d6f...",
  "title": "Buy milk",
  "completed": false
}
```

---

# 📌 9. Future Improvements

- Authentication  
- Multiple WebSocket rooms  
- Redis Pub/Sub for scaling  
- Docker Compose for full stack automation  
- CI/CD pipeline  
- Offline-first sync  

---

# 📜 License

MIT License — free to use and modify.
