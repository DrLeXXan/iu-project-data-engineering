from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import psycopg2
import psycopg2.extras
import json
import datetime


app = FastAPI()

# Store connected WebSocket clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection)

manager = ConnectionManager()

# Postgres Database configuration
DB_CONFIG = {
    "dbname": "factory_db",
    "user": "factory_user",
    "password": "mypassword",
    "host": "postgres",
    "port": "5432",
}

async def query_postgres():
    """Query PostgreSQL for the latest aggregated data."""
    print("Querying PostgreSQL...")  # Debug log
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("""
            SELECT DISTINCT ON (engine_id)
                factory_id, engine_id, watermark, avg_temp_air, avg_temp_oil, avg_temp_exhaust,
                avg_vibration, avg_pressure_1, avg_pressure_2, avg_rpm
            FROM factory.aggregated_sensor_data
            WHERE factory_id = 'factory_001'
            ORDER BY engine_id, watermark DESC;
        """)
        rows = cursor.fetchall()

        # Convert rows to a list of dictionaries and serialize datetime objects
        result = []
        for row in rows:
            row_dict = dict(row)
            if isinstance(row_dict["watermark"], datetime.datetime):
                row_dict["watermark"] = row_dict["watermark"].isoformat() # Convert datetime to ISO format to avoid error
            result.append(row_dict)

        return result
    except Exception as e:
        print(f"Error querying PostgreSQL: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

async def websocket_handler():
    """Continuously query PostgreSQL and broadcast data to WebSocket clients."""
    print("Starting WebSocket handler...")
    while True:
        try:
            data = await query_postgres()
            if data:
                message = json.dumps(data)
                # print(f"Broadcasting data to WebSocket clients: {message}")
                await manager.broadcast(message)
            else:
                print("No data to broadcast.")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Error in WebSocket handler: {e}")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("WebSocket connection established.")
    try:
        while True:
            await asyncio.sleep(1)  # Keep the connection alive
    except WebSocketDisconnect:
        print("WebSocket disconnected.")
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Error in WebSocket endpoint: {e}")


@app.get("/")
async def get():
    with open("frontend/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get("/api/latest-data")
async def get_latest_data():
    """
    API endpoint to fetch the latest data for each engine from PostgreSQL.
    """
    try:
        data = await query_postgres()
        return {"status": "success", "data": data}
    except Exception as e:
        print(f"Error fetching data from PostgreSQL: {e}")
        return {"status": "error", "message": str(e)}


# Start the WebSocket handler on server startup
@app.on_event("startup")
async def startup_event():
    print("Starting WebSocket handler task...")
    asyncio.create_task(websocket_handler())
