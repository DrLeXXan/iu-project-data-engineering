import time
import random
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


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

def verification(signature, data):

    message = json.dumps(data).encode()

    public_key.verify(
        signature,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )




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


            singature = sign_data(data)


            try:
                verification(singature, data)
            except InvalidSignature:
                # Dont forward to Kafka
                # Raise alarm
                print("ALARM")
            else:
                # Forward to Kafka
                print("Verified")



        time.sleep(10)  # 1 sec delay per measurement


if __name__ == "__main__":

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )  
    print(private_key)

    public_key = private_key.public_key()
    print(public_key)

    generate_sensor_data()