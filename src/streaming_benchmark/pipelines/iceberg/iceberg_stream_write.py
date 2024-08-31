from pyspark.sql import SparkSession

spark = SparkSession.builder.remote("sc://localhost:15003").getOrCreate()

df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "redpanda-0:9092")
    .option("subscribe", "source-topic")
    .load()
)

df.writeStream.format("iceberg").outputMode("append").option(
    "checkpointLocation", "/opt/spark/checkpoint"
).toTable("database.kafka_topic")
