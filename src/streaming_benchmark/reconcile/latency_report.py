from pyspark.sql import SparkSession, DataFrame

spark = (
    SparkSession.builder.appName("latency_report")
    .remote("sc://localhost")
    .getOrCreate()
)

source_df: DataFrame = (
    spark.read.format("kafka")
    .option("kafka.bootstrap.servers", "redpanda-0:9092")
    .option("subscribe", "source-topic")
    .option("startingOffsets", "earliest")
    .load()
)

sink_df: DataFrame = (
    spark.read.format("kafka")
    .option("kafka.bootstrap.servers", "redpanda-0:9092")
    .option("subscribe", "sink-topic")
    .option("startingOffsets", "earliest")
    .load()
)

source_df = source_df.selectExpr(
    "to_timestamp(timestamp) as timestamp", "cast(key as string)"
)

sink_df = sink_df.selectExpr(
    "to_timestamp(timestamp) as timestamp", "cast(key as string)"
)

source_df.createOrReplaceTempView("source")
sink_df.createOrReplaceTempView("sink")

latency_df: DataFrame = spark.sql("""
SELECT source.key as key, timestampdiff(MILLISECOND, source.timestamp, sink.timestamp) as latency
FROM source join sink on source.key = sink.key
""")
latency_df.createOrReplaceTempView("latency_table")

percentiles: DataFrame = spark.sql("""
SELECT percentile(latency, array(0.5, 0.99)) as p50_p99_ms
FROM latency_table
""")

percentiles.show(truncate=False)
