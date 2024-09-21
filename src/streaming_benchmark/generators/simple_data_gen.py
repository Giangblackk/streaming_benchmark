import time
import dbldatagen as dg
from pyspark.sql.types import IntegerType, StringType
from pyspark.sql import SparkSession, DataFrame

spark = (
    SparkSession.builder.appName("simple_data_gen")
    .remote("sc://localhost")
    .getOrCreate()
)

row_count = 100
row_per_sec = 1
sec_to_run = 60

testDataSpec = (
    dg.DataGenerator(spark, name="test_data_set1", rows=row_count, partitions=1)
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
    .option("kafka.bootstrap.servers", "redpanda-0:9092")
    .option("topic", "source-topic")
    .option("checkpointLocation", "/opt/spark/checkpoint")
    .start()
)

time.sleep(sec_to_run)

streaming_query.stop()
