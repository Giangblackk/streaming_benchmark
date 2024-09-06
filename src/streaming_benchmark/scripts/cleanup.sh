docker restart data-producer-consumer
docker restart data-pipeline-engine
docker exec data-producer-consumer rm -rf /opt/spark/checkpoint
docker exec data-producer-consumer rm -rf /opt/spark/checkpoint2
docker exec data-pipeline-engine rm -rf /opt/spark/checkpoint
docker exec data-pipeline-engine rm -rf /opt/spark/checkpoint2
docker exec data-pipeline-engine rm -rf /opt/spark/warehouse

docker exec redpanda-0 rpk topic delete source-topic
docker exec redpanda-0 rpk topic delete sink-topic