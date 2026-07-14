CREATE TABLE events (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    timestamp_event timestamptz,
    user_id bigint,
    anonymous_id VARCHAR(100),
    event_name VARCHAR(50),
    device_type VARCHAR(50),
    traffic_source VARCHAR(50),
    properties JSONB
);

CREATE INDEX idx_events_event_name_timestamp_event ON events(event_name, timestamp_event);
CREATE INDEX idx_events_user_id ON events(user_id);
CREATE INDEX idx_events_properties ON events USING GIN (properties);

CREATE TABLE ab_exposures (
    user_id bigint,
    timestamp_ab timestamptz,
    experiment_name VARCHAR(100),
    group_ab CHAR(1),
    PRIMARY KEY (user_id,experiment_name)
);

CREATE DATABASE superset_meta WITH OWNER postgres;