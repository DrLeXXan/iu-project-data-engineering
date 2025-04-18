import base64
import requests
import time
import json
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from kafka import KafkaProducer


CRYPTOGRAPHY_SERVICE_FASTAPI_URL = "http://cryptography_service:8000"
ENGINE_FASTAPI_SERVER_URL = "http://traefik:80"


KAFKA_BROKER = "kafka:9093"


producer = KafkaProducer(
    bootstrap_servers= KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def fetch_public_key():
    try:
        public_key_pem = requests.get(f"{CRYPTOGRAPHY_SERVICE_FASTAPI_URL}/public-key").json()["public-key"]
        return serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    except Exception as e:
        print(f"Error fetching public key: {e}")
        return None


def verify_signature(public_key, data, signature_base64):
    try:
        signature = base64.b64decode(signature_base64)

        public_key.verify(
            signature,
            json.dumps(data).encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print(f"Signature valid")

        KAFKA_TOPIC = data["factory_id"]


        producer.send(KAFKA_TOPIC, json.dumps(data))
        producer.flush()

    except Exception as e:
        print(f"Signature verification failed: {e}")

def stream_and_verify(public_key):
    try:
        with requests.get(f"{ENGINE_FASTAPI_SERVER_URL}/stream", stream=True) as response:
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        sensor_data = data.get("data")
                        signature = data.get("signature")

                        if sensor_data and signature:
                            verify_signature(public_key, sensor_data, signature)
                        else:
                            print("Received incomplete data, skipping...")
                    except json.JSONDecodeError as e:
                        print(f"JSON parsing error: {e}")
                    except Exception as e:
                        print(f"Error processing data: {e}")
    except Exception as e:
        print(f"Error connecting to stream: {e}")


if __name__ == "__main__":
    time.sleep(5)

    public_key = fetch_public_key()


    if public_key:
        print("Public Key Retrieved. Starting verification...")
        stream_and_verify(public_key)
