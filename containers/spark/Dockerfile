FROM spark:3.5.1-python3

# setup workdir
WORKDIR /opt/spark

USER root

# copy entrypoint script and chmod
COPY ./entrypoint.sh /opt/spark/

RUN chmod 755 /opt/spark/entrypoint.sh

ENTRYPOINT [ "/opt/spark/entrypoint.sh" ]