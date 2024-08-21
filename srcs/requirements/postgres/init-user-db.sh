#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 -U $POSTGRES_USER -d $POSTGRES_HOST <<-EOSQL
    -- Créer les bases de données
    CREATE DATABASE ${POSTGRES_USER_DB};

    -- Créer les utilisateurs et attribuer des mots de passe
    CREATE USER ${POSTGRES_USER_NAME} WITH PASSWORD '${POSTGRES_USER_PASSWORD}';

    -- Attribuer des privilèges aux utilisateurs pour leurs bases de données respectives
    GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_USER_DB} TO ${POSTGRES_USER_NAME};
EOSQL

# psql -v ON_ERROR_STOP=1 -U $POSTGRES_USER -d $POSTGRES_HOST <<-EOSQL
#     -- Créer les bases de données
#     CREATE DATABASE ${POSTGRES_USER_DB};

#     -- Créer les utilisateurs et attribuer des mots de passe
#     CREATE USER ${POSTGRES_USER_NAME} WITH PASSWORD '${POSTGRES_USER_PASSWORD}';

#     -- Attribuer des privilèges aux utilisateurs pour leurs bases de données respectives
#     GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_USER_DB} TO ${POSTGRES_USER_NAME};

#     -- Accorder le privilège CREATEDB à l'utilisateur
#     ALTER USER ${POSTGRES_USER_NAME} CREATEDB;
# EOSQL