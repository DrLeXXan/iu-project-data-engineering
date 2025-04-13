from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import requests
import time
from numpy import random
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
    factory_ids = ["factory_001","factory_002","factory_003","factory_004","factory_005","factory_006","factory_007","factory_008","factory_009","factory_010"]
    machine_ids = ["engine_001", "engine_002","engine_003", "engine_004", "engine_005", "engine_006"]
    while True:
        for factory_id in factory_ids:
            for machine_id in machine_ids:
                data = {
                    "factory_id": factory_id,
                    "engine_id": machine_id,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "temp_air": float(round(random.normal(loc=100, size=(1))[0], 2)),
                    "temp_oil": float(round(random.normal(loc=90, size=(1))[0], 2)),
                    "temp_exhaust": float(round(random.normal(loc=760, size=(1))[0], 2)),
                    "vibration": float(round(random.normal(loc=2.8, scale=0.5, size=(1))[0], 2)),
                    "pressure_1": float(round(random.normal(loc=150, size=(1))[0], 2)),
                    "pressure_2": float(round(random.normal(loc=150, size=(1))[0], 2)),
                    "rpm": int(round(random.normal(loc=3000, size=(1))[0],0))
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
