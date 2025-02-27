-- Create a new database schema (optional)
CREATE SCHEMA IF NOT EXISTS factory;

-- Create a users table
CREATE TABLE factory.sensor_data (
    engine_id varchar(10) NOT NULL,
    timestamp timestamp,
    temperature float,
    vibration float,
    pressure float,
    rpm float,
    hash varchar
);
