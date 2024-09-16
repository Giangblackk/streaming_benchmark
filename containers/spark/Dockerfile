FROM spark:3.5.2-python3

# setup workdir
WORKDIR /opt/spark

USER root

ENV SPARK_VERSION=3.5.2
ENV SPARK_MAJOR_VERSION=3.5
ENV ICEBERG_VERSION=1.6.1
ENV NESSIE_VERSION=0.96.0

RUN /opt/spark/bin/spark-sql --packages org.apache.spark:spark-connect_2.12:${SPARK_VERSION},org.projectnessie.nessie-integrations:nessie-spark-extensions-${SPARK_MAJOR_VERSION}_2.12:${NESSIE_VERSION},org.apache.iceberg:iceberg-spark-runtime-${SPARK_MAJOR_VERSION}_2.12:${ICEBERG_VERSION},org.apache.spark:spark-sql-kafka-0-10_2.12:${SPARK_VERSION} -e "SELECT 1"

RUN curl https://jdbc.postgresql.org/download/postgresql-42.7.4.jar -Lo /opt/spark/jars/postgresql-42.7.4.jar

# Download AWS bundle
RUN curl -s https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-aws-bundle/${ICEBERG_VERSION}/iceberg-aws-bundle-${ICEBERG_VERSION}.jar -Lo /opt/spark/jars/iceberg-aws-bundle-${ICEBERG_VERSION}.jar

RUN pip3 install grpcio==1.66.1 protobuf==5.28.0 pandas==2.0.3 pyarrow==17.0.0 grpcio-status==1.66.1

# copy entrypoint script and chmod
COPY ./entrypoint.sh /opt/spark/

RUN chmod 755 /opt/spark/entrypoint.sh

ENTRYPOINT [ "/opt/spark/entrypoint.sh" ]