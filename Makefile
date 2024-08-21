DOCKER_COMPOSE_FILE = ./srcs/docker-compose.yml

all:
	@if [ ! -d "./srcs/data" ]; then mkdir ./srcs/data ; fi
	@if [ ! -d "./srcs/data/postgresql" ]; then mkdir ./srcs/data/postgresql ; fi
	@if [ ! -d "./srcs/data/elasticsearch" ]; then mkdir ./srcs/data/elasticsearch ; fi
	@if [ ! -d "./srcs/data/grafana" ]; then mkdir ./srcs/data/grafana ; fi
	@if [ ! -d "./srcs/data/img" ]; then mkdir ./srcs/data/img ; fi
	@if [ ! -d "./srcs/data/backup" ]; then mkdir ./srcs/data/backup ; fi
	@docker compose -f $(DOCKER_COMPOSE_FILE) up -d --build

down:
	@docker compose -f $(DOCKER_COMPOSE_FILE) down -v
	@printf "\033[32m[+] Removing data directory...\033[0m\n"
	@sudo rm -rf ./srcs/data/postgresql
	@sudo rm -rf ./srcs/data/img
	@sudo rm -rf ./srcs/data/backup
	@printf "\033[32m[+] Removing user logs directory...\033[0m\n"
	@sudo rm -rf ./srcs/logs/*

basic:
	@if [ ! -d "./srcs/data" ]; then mkdir ./srcs/data ; fi
	@if [ ! -d "./srcs/data/postgresql" ]; then mkdir ./srcs/data/postgresql ; fi
	@if [ ! -d "./srcs/data/elasticsearch" ]; then mkdir ./srcs/data/elasticsearch ; fi
	@if [ ! -d "./srcs/data/grafana" ]; then mkdir ./srcs/data/grafana ; fi
	@if [ ! -d "./srcs/data/img" ]; then mkdir ./srcs/data/img ; fi
	@docker compose -f $(DOCKER_COMPOSE_FILE) up -d --build nginx front auth game

logs:
	@docker compose -f $(DOCKER_COMPOSE_FILE) logs -f

clean: down
	@printf "\033[32m[+] Stopping all containers...\033[0m\n"
	@if [ -n "$(shell docker ps -a -q)" ]; then docker stop $(shell docker ps -a -q); fi
	@printf "\033[32m[+] Removing all containers...\033[0m\n"
	@if [ -n "$(shell docker ps -a -q)" ]; then docker rm $(shell docker ps -a -q); fi
	@printf "\033[32m[+] Removing all images...\033[0m\n"
	@if [ -n "$(shell docker images -q)" ]; then docker rmi -f $(shell docker images -q); fi
	@printf "\033[32m[+] Removing all volumes...\033[0m\n"
	@if [ -n "$(shell docker volume ls -q)" ]; then docker volume rm $(shell docker volume ls -q); fi
	@printf "\033[32m[+] Removing all networks...\033[0m\n"
	@if [ -n "$(shell docker network ls -q)" ]; then docker network rm $(shell docker network ls -q); fi
	
re: clean all

rebuild: clean all

prune: clean
	@printf "\033[32m[+] Pruning Docker system...\033[0m\n"
	@docker container prune -f
	@docker image prune -a -f
	@docker volume prune -f
	@docker network prune -f
	@docker system prune -a -f
	@sudo rm -rf ./srcs/data

.PHONY: all down test logs clean re rebuild prune