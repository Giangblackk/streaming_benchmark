FROM spark:3.5.1-python3

# setup workdir
WORKDIR /opt/spark

USER root

RUN /opt/spark/bin/spark-sql --packages org.apache.spark:spark-connect_2.12:3.5.1,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 -e "SELECT 1"

# copy entrypoint script and chmod
COPY ./entrypoint.sh /opt/spark/

RUN chmod 755 /opt/spark/entrypoint.sh

ENTRYPOINT [ "/opt/spark/entrypoint.sh" ]