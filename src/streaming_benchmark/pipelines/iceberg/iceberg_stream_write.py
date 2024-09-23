import typer
from pyspark.sql import SparkSession
from typing_extensions import Annotated

app = typer.Typer()


@app.command()
def iceberg_streaming_write(
    app_name: Annotated[
        str, typer.Option("-n", "--name", help="Spark app name")
    ] = "iceberg_stream_write",
    spark_remote: Annotated[
        str, typer.Option("-r", "--remote", help="URL to remote Spark Connect server")
    ] = "sc://localhost:15003",
    catalog_name: Annotated[
        str, typer.Option("-c", "--catalog", help="Iceberg Catalog name")
    ] = "nessie",
    table_name: Annotated[
        str, typer.Option("-t", "--table", help="Name of output Iceberg table")
    ] = "kafka_topic",
    source_topic_name: Annotated[
        str, typer.Option("--topic", help="Name of source Kafka topic")
    ] = "sink-topic",
    bootstrap_servers: Annotated[
        str,
        typer.Option(
            "--bootstrap",
            help="List of Kafka/Redpanda boostrap servers, separated by comma",
        ),
    ] = "redpanda-0:9092",
    checkpoint_location: Annotated[
        str,
        typer.Option(
            "--checkpoint", help="Location of checkpoint folder of Spark application"
        ),
    ] = "/opt/spark/checkpoint2",
):
    """Streaming read from a Kafka topic and write to an Iceberg table

    Args:
        app_name (str, optional): Spark app name. Default to "iceberg_stream_write".
        spark_remote (str, optional): URL to remote Spark Connect server. Default to "sc://localhost:15003".
        catalog_name (str, optional): Iceberg Catalog name. Default to "nessie".
        table_name (str, optional): Name of output Iceberg table. Default to "kafka_topic".
        source_topic_name (str, optional): Name of source Kafka topic. Default to "sink-topic".
        bootstrap_servers (str, optional): List of Kafka/Redpanda boostrap servers, separated by comma. Default to "redpanda-0:9092".
        checkpoint_location (str, optional): Location of checkpoint folder of Spark application. Default to "/opt/spark/checkpoint2".
    """
    spark: SparkSession = (
        SparkSession.builder.appName(app_name).remote(spark_remote).getOrCreate()
    )

    spark.catalog.setCurrentCatalog(catalog_name)

    df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", bootstrap_servers)
        .option("subscribe", source_topic_name)
        .option("startingOffsets", "earliest")
        .load()
    )

    df.selectExpr("key as id", "CAST(value as STRING)").writeStream.format(
        "iceberg"
    ).outputMode("append").option("checkpointLocation", checkpoint_location).toTable(
        table_name
    )


if __name__ == "__main__":
    app()
