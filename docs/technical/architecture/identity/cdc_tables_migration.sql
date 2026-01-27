-- Change Data Capture (CDC) Tables Migration
-- Industry Standard Implementation
-- 
-- Creates tables for tracking all data changes across systems:
-- - sync_change_log: Stores all change events
-- - sync_processed_events: Tracks which events processed to which destinations

-- Change Log Table
CREATE TABLE IF NOT EXISTS `identity.sync_change_log` (
    event_id STRING NOT NULL,
    source STRING NOT NULL,
    entity_type STRING NOT NULL,
    entity_id STRING NOT NULL,
    change_type STRING NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    version INT64 NOT NULL,
    data JSON,
    metadata JSON,
    processed BOOL NOT NULL DEFAULT FALSE,
    processed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(timestamp)
CLUSTER BY entity_type, entity_id, source
OPTIONS(
    description="CDC change log for tracking all data changes across systems"
);

-- Processed Events Table
CREATE TABLE IF NOT EXISTS `identity.sync_processed_events` (
    event_id STRING NOT NULL,
    processed_at TIMESTAMP NOT NULL,
    destination STRING NOT NULL,
    status STRING NOT NULL,
    error_message STRING,
    PRIMARY KEY (event_id, destination) NOT ENFORCED
)
PARTITION BY DATE(processed_at)
CLUSTER BY event_id, destination
OPTIONS(
    description="Tracks which events have been processed to which destinations"
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_sync_change_log_entity 
ON `identity.sync_change_log`(entity_type, entity_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_sync_change_log_processed 
ON `identity.sync_change_log`(processed, timestamp);

CREATE INDEX IF NOT EXISTS idx_sync_processed_events_event 
ON `identity.sync_processed_events`(event_id, destination);

-- Views for common queries
CREATE OR REPLACE VIEW `identity.sync_change_log_summary` AS
SELECT 
    entity_type,
    entity_id,
    source,
    change_type,
    COUNT(*) as change_count,
    MAX(timestamp) as last_change,
    MAX(CASE WHEN processed THEN timestamp END) as last_processed
FROM `identity.sync_change_log`
GROUP BY entity_type, entity_id, source, change_type;

CREATE OR REPLACE VIEW `identity.sync_pending_changes` AS
SELECT 
    event_id,
    source,
    entity_type,
    entity_id,
    change_type,
    timestamp,
    TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), timestamp, SECOND) as age_seconds
FROM `identity.sync_change_log`
WHERE processed = FALSE
ORDER BY timestamp ASC;
