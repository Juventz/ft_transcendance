FROM docker.elastic.co/logstash/logstash:7.10.1

USER root

RUN mkdir -p /usr/share/java
RUN curl -L -o /usr/share/java/postgresql.jar https://jdbc.postgresql.org/download/postgresql-42.7.3.jar

USER logstash