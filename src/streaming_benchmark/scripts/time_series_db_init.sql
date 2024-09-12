CREATE TABLE latency_streaming (
   time         TIMESTAMPTZ     NOT NULL,
   key          TEXT            NOT NULL,
   latency      integer         NOT NULL
);

SELECT create_hypertable('latency_streaming', by_range('time'));