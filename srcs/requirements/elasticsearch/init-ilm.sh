#!/bin/bash

# Attendre que Elasticsearch soit opérationnel
# until curl -s http://localhost:9200/_cluster/health; do
#   sleep 1
# done

# Configurer la politique ILM
curl -X PUT "localhost:9200/_ilm/policy/my_policy" -H 'Content-Type: application/json' -d'
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_size": "50GB",
            "max_age": "30d"
          }
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
'

# Configurer le modèle d'index pour utiliser la politique ILM
curl -X PUT "localhost:9200/_index_template/logstash_template" -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["logstash-*"],
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 1,
      "index.lifecycle.name": "my_policy",
      "index.lifecycle.rollover_alias": "logstash"
    }
  }
}
'