-- Create database
CREATE DATABASE IF NOT EXISTS mydb;

-- Create user with mysql_native_password plugin
CREATE USER IF NOT EXISTS 'myuser'@'%' IDENTIFIED WITH mysql_native_password BY 'mypassword';

-- Grant privileges
GRANT ALL PRIVILEGES ON mydb.* TO 'myuser'@'%';
FLUSH PRIVILEGES;

-- Use the database
USE mydb;

-- Create airports table
CREATE TABLE IF NOT EXISTS airports (
    AirportCode VARCHAR(10) PRIMARY KEY,
    CityCode VARCHAR(10),
    CountryCode VARCHAR(10),
    CountryName VARCHAR(100),
    Latitude DECIMAL(10, 6),
    Longitude DECIMAL(10, 6)
);