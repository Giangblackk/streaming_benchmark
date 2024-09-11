from pyspark.sql import SparkSession

spark: SparkSession = (
    SparkSession.builder.appName("iceberg_stream_read")
    .remote("sc://localhost:15003")
    .getOrCreate()
)

spark.catalog.setCurrentCatalog("nessie")

df = spark.readStream.format("iceberg").load("kafka_topic")

df.selectExpr("id as key", "value").writeStream.format("kafka").option(
    "kafka.bootstrap.servers", "redpanda-0:9092"
).option("checkpointLocation", "/opt/spark/checkpoint2").option(
    "topic", "sink-topic"
).start()
