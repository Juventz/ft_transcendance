FROM alpine:latest

# Installer curl et cron
RUN apk add --no-cache curl dcron

# Ajouter le script de snapshot
COPY create-snapshot.sh /create-snapshot.sh
RUN chmod +x /create-snapshot.sh

# Ajouter le fichier crontab
COPY snapshot-cron /etc/crontabs/root

# S'assurer que le script de snapshot est exécutable
RUN chmod +x /etc/crontabs/root

# Démarrer cron en premier plan
CMD exec crond
