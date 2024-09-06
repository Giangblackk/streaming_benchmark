FROM spark:3.5.1-python3

# setup workdir
WORKDIR /opt/spark

USER root

RUN /opt/spark/bin/spark-sql --packages org.apache.spark:spark-connect_2.12:3.5.1,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 -e "SELECT 1"

RUN curl https://jdbc.postgresql.org/download/postgresql-42.7.4.jar -Lo /opt/spark/jars/postgresql-42.7.4.jar

RUN pip3 install grpcio==1.66.1 protobuf==5.28.0 pandas==2.0.3 pyarrow==17.0.0 grpcio-status==1.66.1

# copy entrypoint script and chmod
COPY ./entrypoint.sh /opt/spark/

RUN chmod 755 /opt/spark/entrypoint.sh

ENTRYPOINT [ "/opt/spark/entrypoint.sh" ]