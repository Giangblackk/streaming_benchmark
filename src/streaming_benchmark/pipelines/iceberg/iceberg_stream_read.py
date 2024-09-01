from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("iceberg_stream_read")
    .remote("sc://localhost:15003")
    .getOrCreate()
)

df = (
    spark.readStream.format("iceberg")
    .option("stream-from-timestamp", "0000000000000")
    .load("database.kafka_topic")
)

df.selectExpr("id as key", "value").writeStream.format("kafka").option(
    "kafka.bootstrap.servers", "redpanda-0:9092"
).option("checkpointLocation", "/opt/spark/checkpoint2").option(
    "topic", "sink-topic"
).start()
