-- Create a new database schema (optional)
CREATE SCHEMA IF NOT EXISTS factory;

-- Create a users table
CREATE TABLE factory.sensor_data (
    factory_id varchar(15) NOT NULL,
    engine_id varchar(15) NOT NULL,
    timestamp timestamp,
    temp_air float,
    temp_oil float,
    temp_exhaust float,
    vibration float,
    pressure_1 float,
    pressure_2 float,
    rpm float,
    CRTED timestamp NOT NULL DEFAULT NOW()
);
