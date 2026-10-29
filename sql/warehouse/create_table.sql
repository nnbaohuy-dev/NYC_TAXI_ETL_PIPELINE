CREATE SCHEMA IF NOT EXISTS warehouse;
-- 1. DIM DATE

CREATE TABLE IF NOT EXISTS warehouse.dim_date
(
    date_key        INTEGER PRIMARY KEY,
    full_date       DATE NOT NULL UNIQUE,
    year            SMALLINT NOT NULL,
    quarter         SMALLINT NOT NULL,
    month           SMALLINT NOT NULL,
    month_name      VARCHAR(20) NOT NULL,
    day             SMALLINT NOT NULL,
    day_of_week     SMALLINT NOT NULL,
    day_name        VARCHAR(20) NOT NULL,
    week_of_year    SMALLINT NOT NULL,
    is_weekend      BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse.dim_location
(
    location_id     INTEGER PRIMARY KEY,
    borough         VARCHAR(100),
    zone            VARCHAR(150),
    service_zone    VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS warehouse.dim_vendor
(
    vendor_id       SMALLINT PRIMARY KEY,
    vendor_name     VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse.dim_payment_type
(
    payment_type_id     SMALLINT PRIMARY KEY,
    payment_type_name   VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse.dim_rate_code
(
    ratecode_id       SMALLINT PRIMARY KEY,
    ratecode_name     VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse.fact_trip
(
    pickup_date_key     INTEGER NOT NULL,
    dropoff_date_key    INTEGER NOT NULL,
    pickup_datetime     TIMESTAMP NOT NULL,
    dropoff_datetime    TIMESTAMP NOT NULL,
    vendor_id               SMALLINT,
    ratecode_id            SMALLINT,
    pickup_location_id      INTEGER,
    dropoff_location_id     INTEGER,
    payment_type_id         SMALLINT,
    passenger_count         NUMERIC(10, 2),
    trip_distance           NUMERIC(12, 3),
    trip_duration           NUMERIC(12, 2),
    average_speed_mph       NUMERIC(12, 2),
    fare_amount             NUMERIC(12, 2),
    extra                   NUMERIC(12, 2),
    mta_tax                  NUMERIC(12, 2),
    tip_amount              NUMERIC(12, 2),
    tolls_amount             NUMERIC(12, 2),
    improvement_surcharge    NUMERIC(12, 2),
    total_amount             NUMERIC(12, 2),
    congestion_surcharge     NUMERIC(12, 2),
    airport_fee              NUMERIC(12, 2),
    source_file             VARCHAR(255),
    load_timestamp           TIMESTAMP NOT NULL,

    CONSTRAINT fk_fact_trip_pickup_date
        FOREIGN KEY (pickup_date_key)
        REFERENCES warehouse.dim_date(date_key),


    CONSTRAINT fk_fact_trip_dropoff_date
        FOREIGN KEY (dropoff_date_key)
        REFERENCES warehouse.dim_date(date_key),


    CONSTRAINT fk_fact_trip_vendor
        FOREIGN KEY (vendor_id)
        REFERENCES warehouse.dim_vendor(vendor_id),


    CONSTRAINT fk_fact_trip_rate_code
        FOREIGN KEY (ratecode_id)
        REFERENCES warehouse.dim_rate_code(ratecode_id),


    CONSTRAINT fk_fact_trip_pickup_location
        FOREIGN KEY (pickup_location_id)
        REFERENCES warehouse.dim_location(location_id),


    CONSTRAINT fk_fact_trip_dropoff_location
        FOREIGN KEY (dropoff_location_id)
        REFERENCES warehouse.dim_location(location_id),


    CONSTRAINT fk_fact_trip_payment_type
        FOREIGN KEY (payment_type_id)
        REFERENCES warehouse.dim_payment_type(payment_type_id)
)
PARTITION BY RANGE (pickup_datetime);


CREATE TABLE IF NOT EXISTS warehouse.processed_files (
    file_name TEXT PRIMARY KEY,
    processed_at TIMESTAMP NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE IF NOT EXISTS warehouse.staging
(
    pickup_date_key     INTEGER NOT NULL,
    dropoff_date_key    INTEGER NOT NULL,
    pickup_datetime     TIMESTAMP NOT NULL,
    dropoff_datetime    TIMESTAMP NOT NULL,
    vendor_id               SMALLINT,
    ratecode_id            SMALLINT,
    pickup_location_id      INTEGER,
    dropoff_location_id     INTEGER,
    payment_type_id         SMALLINT,
    passenger_count         NUMERIC(10, 2),
    trip_distance           NUMERIC(12, 3),
    trip_duration           NUMERIC(12, 2),
    average_speed_mph       NUMERIC(12, 2),
    fare_amount             NUMERIC(12, 2),
    extra                   NUMERIC(12, 2),
    mta_tax                  NUMERIC(12, 2),
    tip_amount              NUMERIC(12, 2),
    tolls_amount             NUMERIC(12, 2),
    improvement_surcharge    NUMERIC(12, 2),
    total_amount             NUMERIC(12, 2),
    congestion_surcharge     NUMERIC(12, 2),
    airport_fee              NUMERIC(12, 2),
    source_file             VARCHAR(255),
    load_timestamp           TIMESTAMP NOT NULL
)