import time
import random


def validate_data(data):
    """Validates the sensor data before transmitting."""
    if not isinstance(data["engine_id"], str):
        print(f"Incorrect engine_id: {data['engine_id']}")
        return False
    if not isinstance(data["timestamp"], str):
        print(f"Incorrect timestamp: {data['timestamp']}")
        return False
    if not (50.0 <= data["temperature"] <= 100.0):
        print(f"Incorrect temperatur: {data['temperature']}")
        return False
    if not (0.1 <= data["vibration"] <= 5.0):
        print(f"Incorrect vibration: {data['vibration']}")
        return False
    if not (10.0 <= data["pressure"] <= 50.0):
        print(f"Incorrect pressure: {data['pressure']}")
        return False
    if not (500 <= data["rpm"] <= 5000):
        print(f"Incorrect RPM: {data['rpm']}")
        return False
    return True

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

            if validate_data(data):
                print(f"Send: {data}")
            else:
                print(f"Fehlerhafte Daten erkannt: {data}")
        time.sleep(1)  # 1 sec delay per measurement


if __name__ == "__main__":
    generate_sensor_data()