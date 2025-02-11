import time
import random
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

import base64


app = FastAPI()

private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )  

public_key = private_key.public_key()

# Serialize the public key to PEM format
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode("utf-8")

    
def sign_data(data): 

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


            signature = sign_data(data)
            signature_base64 = base64.b64encode(signature).decode("utf-8")

            chunk = {
                        "data": data, 
                        "public_key": public_pem, 
                        "signature": signature_base64
                    }
            
            yield json.dumps(chunk, indent=2)

        time.sleep(1)  # 1 sec delay per measurement

@app.get("/stream")
async def stream_data():
    return StreamingResponse(generate_sensor_data(), media_type="text/event-stream")

@app.get("/")
def home():
    return {"message": "FastAPI Streaming Server is Running"}