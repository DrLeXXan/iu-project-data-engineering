CREATE SCHEMA IF NOT EXISTS factory;

-- Create a new table for storing sensor data
CREATE TABLE factory.sensor_data (
    id SERIAL PRIMARY KEY,
    factory_id varchar(15) NOT NULL,
    engine_id varchar(15) NOT NULL,
    timestamp TIMESTAMPTZ,
    temp_air float,
    temp_oil float,
    temp_exhaust float,
    vibration float,
    pressure_1 float,
    pressure_2 float,
    rpm float
);

-- Create a new table for storing aggregated sensor data
CREATE TABLE factory.aggregated_sensor_data (
    id SERIAL PRIMARY KEY,
    factory_id varchar(15) NOT NULL,
    engine_id varchar(15) NOT NULL,
    watermark TIMESTAMPTZ,
    avg_temp_air FLOAT,
    avg_temp_oil FLOAT,
    avg_temp_exhaust FLOAT,
    avg_vibration FLOAT,
    avg_pressure_1 FLOAT,
    avg_pressure_2 FLOAT,
    avg_rpm FLOAT,
    batch_size INT
);
