import pyspark.sql.functions as F
import typer
from pyspark.sql import DataFrame, SparkSession
from typing_extensions import Annotated

app = typer.Typer()


@app.command()
def latency_streaming_report(
    app_name: Annotated[
        str, typer.Option("-n", "--name", help="Spark app name")
    ] = "latency_streaming_report",
    spark_remote: Annotated[
        str, typer.Option("-r", "--remote", help="URL to remote Spark Connect server")
    ] = "sc://localhost",
    bootstrap_servers: Annotated[
        str,
        typer.Option(
            "--bootstrap",
            help="List of Kafka/Redpanda boostrap servers, separated by comma",
        ),
    ] = "redpanda-0:9092",
    source_topic_name: Annotated[
        str, typer.Option("--topic", help="Name of source Kafka topic")
    ] = "source-topic",
    sink_topic_name: Annotated[
        str, typer.Option("--topic", help="Name of sink Kafka topic")
    ] = "sink-topic",
    checkpoint_location: Annotated[
        str,
        typer.Option(
            "--checkpoint", help="Location of checkpoint folder of Spark application"
        ),
    ] = "/opt/spark/checkpoint2",
    db_uri: Annotated[
        str, typer.Option("--uri", help="JDBC Database URI to time series database")
    ] = "jdbc:postgresql://timescaledb:5432/postgres",
    table_name: Annotated[
        str, typer.Option("-t", "--table", help="Name of output latency report table")
    ] = "latency_streaming",
    db_username: Annotated[
        str, typer.Option("--user", help="User name of time series database")
    ] = "postgres",
    db_password: Annotated[
        str, typer.Option("--password", help="Password of time series database")
    ] = "changethispassword",
):
    """Measure streaming latency between corresponding messages in source and sink topic, then save to time series database

    Args:
        app_name (str, optional): Spark app name. Default to "latency_streaming_report".
        spark_remote (str, optional): URL to remote Spark Connect server. Default to "sc://localhost".
        bootstrap_servers (str, optional): List of Kafka/Redpanda boostrap servers, separated by comma. Default to "redpanda-0:9092".
        source_topic_name (str, optional): Name of source Kafka topic. Default to "source-topic".
        sink_topic_name (str, optional): Name of sink Kafka topic. Default to "sink-topic".
        checkpoint_location (str, optional): Location of checkpoint folder of Spark application". Default to "/opt/spark/checkpoint2".
        db_uri (str, optional): JDBC Database URI to time series database. Default to "jdbc:postgresql://timescaledb:5432/postgres".
        table_name (str, optional): Defaults to "Name of output latency report table. Default to "latency_streaming".
        db_username (str, optional): User name of time series database. Default to "postgres".
        db_password (str, optional): Password of time series database. Default to "changethispassword".
    """
    spark: SparkSession = (
        SparkSession.builder.appName(app_name).remote(spark_remote).getOrCreate()
    )

    source_df: DataFrame = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", bootstrap_servers)
        .option("subscribe", source_topic_name)
        .option("startingOffsets", "earliest")
        .load()
    )

    sink_df: DataFrame = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", bootstrap_servers)
        .option("subscribe", sink_topic_name)
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
            ).write.mode("append").format("jdbc").option("url", db_uri).option(
                "driver", "org.postgresql.Driver"
            ).option("dbtable", table_name).option("user", db_username).option(
                "password", db_password
            ).save()

    joined_df.writeStream.foreachBatch(write_stream_to_postgres).option(
        "checkpointLocation", checkpoint_location
    ).start()


if __name__ == "__main__":
    app()
