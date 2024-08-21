## Introduction

This README provides basic instructions for testing the application using Docker containers. The application consists of four main services: `nginx`, `postgres`, `frontend`, and `user`. These services are orchestrated using Docker Compose.

## Getting Started

To begin testing, you'll need to have Docker and Docker Compose installed on your system. Once installed, you can use the following commands to manage and test the application.

### Starting the Services

To start all the required services, use the `make` command as follows:

```bash
make basic
```

This command is a shortcut for:

```bash
docker compose -f docker-compose.yml up -d --build nginx postgres frontend user
```

It builds and starts the `nginx`, `postgres`, `frontend`, and `user` services in detached mode.

### Verifying the Containers

After starting the services, you can verify that all containers are running using:

```bash
docker ps
```

### Accessing Container Logs

To view the logs of a specific container, use the `docker logs` command. Replace `container_name` with the name of the container you wish to inspect (`nginx`, `postgres`, `frontend`, or `user`):

```bash
docker logs container_name
```

### Executing Commands Inside a Container

If you need to execute commands inside a container, use:

```bash
docker exec -it container_name bash
```

This command opens a bash shell inside the specified container.

## Accessing the Services

The services can be accessed through the `nginx` server as configured in the [`nginx.conf`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Fklheb%2Fmy_github%2Ftranscendance%2Fsrcs%2Frequirements%2Fnginx%2Fconf%2Fnginx.conf%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/home/klheb/my_github/transcendance/srcs/requirements/nginx/conf/nginx.conf") file. Here are the routes for accessing the `frontend` and `user` services:

- **Frontend Service**: Accessible via https://localhost/. This route proxies requests to the `frontend` service running on port 8000.

- **User Service**: Accessible via https://localhost/api. This route proxies requests to the `user` service running on port 8001.

### Internal Service Communication

The services can communicate with each other using the following URLs:

- **Frontend to User Service**: http://frontend:8000 can call http://user:8001 for backend operations.

- **User Service to Frontend**: Similarly, http://user:8001 can call http://frontend:8000 for frontend resources.

## Conclusion

This README provides a basic overview of how to start the services, verify their status, access logs, execute commands inside containers, and access the services through `nginx`. For more detailed information, refer to the specific documentation of each service.
