from pyspark.sql import SparkSession

spark = SparkSession.builder.remote("sc://localhost:15003").getOrCreate()

df = spark.readStream.format("iceberg").load("database.kafka_topic")

df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)").writeStream.format(
    "kafka"
).option("kafka.bootstrap.servers", "redpanda-0:9092").option(
    "checkpointLocation", "/opt/spark/checkpoint2"
).option("topic", "sink-topic").start()
