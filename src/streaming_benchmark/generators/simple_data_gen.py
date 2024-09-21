import time

import dbldatagen as dg
import typer
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import IntegerType, StringType
from typing_extensions import Annotated


def simple_data_gen(
    app_name: Annotated[
        str, typer.Option("-n", "--name", help="Spark app name")
    ] = "simple_data_gen",
    spark_remote: Annotated[
        str, typer.Option("-r", "--remote", help="URL to remote Spark Connect server")
    ] = "sc://localhost",
    row_per_sec: Annotated[
        int, typer.Option(help="Number of generated row of data per seconds")
    ] = 1,
    num_partitions: Annotated[
        int,
        typer.Option(
            "-p", "--partitions", help="Number of partitions in data generation process"
        ),
    ] = 1,
    sec_to_run: Annotated[
        int, typer.Option(help="Number of seconds to run data generation")
    ] = 60,
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
    checkpoint_location: Annotated[
        str,
        typer.Option(
            "--checkpoint", help="Location of checkpoint folder of Spark application"
        ),
    ] = "/opt/spark/checkpoint",
):
    spark = SparkSession.builder.appName(app_name).remote(spark_remote).getOrCreate()

    testDataSpec = (
        dg.DataGenerator(spark, name=app_name, partitions=num_partitions)
        .withIdOutput()
        .withColumn("code1", IntegerType(), minValue=100, maxValue=200, random=True)
        .withColumn(
            "code2",
            StringType(),
            values=["online", "offline", "unknown"],
            percentNulls=0.05,
        )
    )

    dfTestData: DataFrame = testDataSpec.build(
        options={"rowsPerSecond": row_per_sec}, withStreaming=True
    )

    streaming_query = (
        dfTestData.selectExpr(
            "CAST(id as STRING) as key",
            "CAST(CONCAT_WS('-', CAST(code1 as STRING), code2) AS STRING) as value",
        )
        .writeStream.format("kafka")
        .option("kafka.bootstrap.servers", bootstrap_servers)
        .option("topic", source_topic_name)
        .option("checkpointLocation", checkpoint_location)
        .start()
    )

    time.sleep(sec_to_run)

    streaming_query.stop()


if __name__ == "__main__":
    typer.run(simple_data_gen)
