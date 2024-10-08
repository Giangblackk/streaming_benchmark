from pyspark.sql import SparkSession

spark: SparkSession = (
    SparkSession.builder.appName("iceberg_stream_write")
    .remote("sc://localhost:15003")
    .getOrCreate()
)

spark.catalog.setCurrentCatalog("nessie")

df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "redpanda-0:9092")
    .option("subscribe", "source-topic")
    .option("startingOffsets", "earliest")
    .load()
)

df.selectExpr("key as id", "CAST(value as STRING)").writeStream.format(
    "iceberg"
).outputMode("append").option("checkpointLocation", "/opt/spark/checkpoint").toTable(
    "kafka_topic"
)
