FROM nginx:1.21.0-alpine

# Copy the Nginx configuration file
COPY ./conf/nginx.conf /etc/nginx/nginx.conf

# Install apache2-utils
RUN apk add --no-cache apache2-utils

# Install openssl
RUN apk add --no-cache openssl

# Create directories for SSL certificates
RUN mkdir -p /etc/nginx/ssl

# Generate a self-signed SSL certificate
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt \
    -subj "/C=FR/ST=Paris/L=Paris/O=42/OU=42/CN=transcendence"

# Declare environment variables as arguments
ARG KIBANA_USER
ARG KIBANA_PASSWORD

# Create a password file and add a user
RUN htpasswd -bc /etc/nginx/htpasswd.users ${KIBANA_USER} ${KIBANA_PASSWORD}

EXPOSE 443
