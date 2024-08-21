FROM docker.elastic.co/elasticsearch/elasticsearch:7.10.1

# Copier le script d'initialisation
COPY init-ilm.sh /usr/share/elasticsearch/config/init-ilm.sh

# Rendre le script exécutable
USER root
RUN chmod +x /usr/share/elasticsearch/config/init-ilm.sh

# Exécuter le script d'initialisation après le démarrage d'Elasticsearch
CMD ["/bin/bash", "-c", "/usr/local/bin/docker-entrypoint.sh elasticsearch", ";", "/usr/share/elasticsearch/config/init-ilm.sh"]

# Exposer le port 9200
EXPOSE 9200
