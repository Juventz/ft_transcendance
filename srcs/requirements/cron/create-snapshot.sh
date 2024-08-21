#!/bin/bash
# Script pour créer un snapshot Elasticsearch

# Format de la date pour le nom du snapshot
SNAPSHOT_NAME=$(date +%Y%m%d_%H%M%S)

# Commande pour créer un snapshot
curl -X PUT "elasticsearch:9200/_snapshot/my_fs_backup/$SNAPSHOT_NAME?wait_for_completion=true" -H 'Content-Type: application/json' -d'
{
  "indices": "*",
  "ignore_unavailable": true,
  "include_global_state": true
}'