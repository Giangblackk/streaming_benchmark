from pyspark.sql import SparkSession, DataFrame
import pyspark.sql.functions as F

spark: SparkSession = (
    SparkSession.builder.appName("latency_report")
    .remote("sc://localhost")
    .getOrCreate()
)

source_df: DataFrame = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "redpanda-0:9092")
    .option("subscribe", "source-topic")
    .option("startingOffsets", "earliest")
    .load()
)

sink_df: DataFrame = (
    spark.readStream.format("kafka")
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

joined_df = (
    source_df.alias("source")
    .join(sink_df.alias("sink"), "key", "inner")
    .selectExpr(
        "source.key",
        "timestampdiff(MILLISECOND, source.timestamp, sink.timestamp) as latency",
    )
)


def write_stream_to_postgres(df: DataFrame, epoch_id: int):
    if not df.isEmpty():
        df.withColumn("epoch_id", F.lit(epoch_id)).withColumn(
            "time", F.current_timestamp()
        ).write.mode("append").format("jdbc").option(
            "url", "jdbc:postgresql://timescaledb:5432/postgres"
        ).option("driver", "org.postgresql.Driver").option(
            "dbtable", "latency_streaming"
        ).option("user", "postgres").option("password", "changethispassword").save()


joined_df.writeStream.foreachBatch(write_stream_to_postgres).option(
    "checkpointLocation", "/opt/spark/checkpoint2"
).start()
