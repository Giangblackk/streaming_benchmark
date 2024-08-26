import dbldatagen as dg
from pyspark.sql.types import FloatType, IntegerType, StringType
from pyspark.sql import SparkSession

spark = SparkSession.builder.remote("sc://localhost").getOrCreate()

row_count = 10 * 10
column_count = 10
testDataSpec = (
    dg.DataGenerator(spark, name="test_data_set1", rows=row_count, partitions=4)
    .withIdOutput()
    .withColumn(
        "r",
        FloatType(),
        expr="floor(rand() * 350) * (86400 + 3600)",
        numColumns=column_count,
    )
    .withColumn("code1", IntegerType(), minValue=100, maxValue=200)
    .withColumn("code2", "integer", minValue=0, maxValue=10, random=True)
    .withColumn("code3", StringType(), values=["online", "offline", "unknown"])
    .withColumn(
        "code4", StringType(), values=["a", "b", "c"], random=True, percentNulls=0.05
    )
    .withColumn(
        "code5", "string", values=["a", "b", "c"], random=True, weights=[9, 1, 1]
    )
)

dfTestData = testDataSpec.build()

dfTestData.selectExpr(
    "CAST(id AS STRING) as key", "CAST(code3 AS STRING) as value"
).write.format("kafka").option("kafka.bootstrap.servers", "redpanda-0:9092").option(
    "topic", "source-topic"
).save()
