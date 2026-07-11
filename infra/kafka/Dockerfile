FROM apache/kafka:latest

USER root
RUN apk add --no-cache yq bash

COPY infra/kafka/topics.yml /topics.yml
COPY infra/kafka/create-topics-init.sh /create-topics-init.sh
RUN chmod +x /create-topics-init.sh

ENTRYPOINT ["/create-topics-init.sh"]
