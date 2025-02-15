from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import requests
import time
import random
import json
import base64

CRYPTOGRAPHY_SERVICE_FASTAPI_URL = "http://cryptography_service:8000"

app = FastAPI()

def fetch_private_key():
    try:
        private_key_pem = requests.get(f"{CRYPTOGRAPHY_SERVICE_FASTAPI_URL}/private-key").json()["private-key"]
        return serialization.load_pem_private_key(private_key_pem.encode("utf-8"),password=None)
    except Exception as e:
        print(f"Error fetching private key: {e}")
        return None
    
private_key = fetch_private_key()

def sign_data(data, private_key): 

    message = json.dumps(data).encode()

    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    return signature


def generate_sensor_data():
    """Generates continues (simulated) sensor data for four IoT-Engines."""
    machine_ids = ["engine_001", "engine_002", "engine_003", "engine_004"]
    while True:
        for machine_id in machine_ids:
            data = {
                "engine_id": machine_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": round(random.uniform(50.0, 100.0), 2),
                "vibration": round(random.uniform(0.1, 5.0), 2),
                "pressure": round(random.uniform(5.0, 50.0), 2),
                "rpm": random.randint(1000, 3000),
            }

            

            signature = sign_data(data, private_key)
            signature_base64 = base64.b64encode(signature).decode("utf-8")

            chunk = {
                        "data": data, 
                        "signature": signature_base64
                    }
            
            yield json.dumps(chunk, ensure_ascii=False) + "\n"

        time.sleep(1)  # 1 sec delay per measurement


@app.get("/stream")
async def stream_data():
    return StreamingResponse(generate_sensor_data(), media_type="text/event-stream")
