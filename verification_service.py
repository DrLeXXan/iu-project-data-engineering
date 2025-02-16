from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
import base64
import requests
import time
import json
from kafka import KafkaProducer, KafkaConsumer


CRYPTOGRAPHY_SERVICE_FASTAPI_URL = "http://cryptography_service:8000"
ENGINE_FASTAPI_SERVER_URL = "http://traefik:8081"

KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "factory_data_verified"

producer = KafkaProducer(
    bootstrap_servers= KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )


def fetch_public_key():
    """Returns the public key which is received through the Cryptography API"""
    try:
        public_key_pem = requests.get(f"{CRYPTOGRAPHY_SERVICE_FASTAPI_URL}/public-key").json()["public-key"]
        return serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    except Exception as e:
        print(f"Error fetching public key: {e}")
        return None


def verify_signature(public_key, data, signature_base64) -> str:
    """Verifies the received signature before injecting the data chunks into apache cluster"""
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
        print(f"Signature valid for message: {data}")

        producer.send(KAFKA_TOPIC, json.dumps(data))
        producer.flush()

    except Exception as e:
        print(f"Signature verification failed: {e}")

def stream_and_verify(public_key) -> None:
    """Received the data stream from the smart factory (engine) API"""
    try:
        with requests.get(f"{ENGINE_FASTAPI_SERVER_URL}/stream", stream=True) as response:
            buffer = ""
            for chunk in response.iter_content(chunk_size=1024):
                buffer += chunk.decode("utf-8")

                while "\n" in buffer:
                    json_object, buffer = buffer.split("\n", 1)
                    json_object = json_object.strip()

                    if not json_object.startswith("{") or not json_object.endswith("}"):
                        print(f"Skipping malformed JSON: {json_object}")
                        continue

                    try:
                        data = json.loads(json_object)

                        sensor_data = data.get("data")
                        signature = data.get("signature")

                        if sensor_data and signature:
                            verify_signature(public_key, sensor_data, signature)
                        else:
                            print("Received incomplete data, skipping...")
                            # Skipping or store in database for analysis?

                    except json.JSONDecodeError as e:
                        print(f"JSON parsing error: {e}")
    except Exception as e:
        print(f"Error connecting to stream: {e}")


if __name__ == "__main__":
    time.sleep(5)

    public_key = fetch_public_key()


    if public_key:
        print("Public Key Retrieved. Starting verification...")
        stream_and_verify(public_key)
