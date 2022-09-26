
BUILD_NUMBER?=0
PACKAGE_VERSION?=0.0.0.1
PACKAGE_NAME?=roles-svc-lambda

DEBUG?=true
DOCKER_MAKE?=true
POSTGRES_HOST?=docker
POSTGRES_PASSWORD?=secret


define run_docker_cmd
	docker-compose $(DOCKER_OPTS) run \
		$(2) \
		--rm \
		--use-aliases \
		-v `pwd`:/app \
		-v /`pwd`/configs/templates/aws:/home/granular/.aws \
		-e BUILD_NUMBER=$(BUILD_NUMBER) \
		-e PACKAGE_VERSION=$(PACKAGE_VERSION) \
		-e PACKAGE_NAME=$(PACKAGE_NAME) \
		-e SHELL=/bin/bash \
		-e POSTGRES_HOST=$(POSTGRES_HOST) \
		-e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
		-e ROLES_SVC_USER_PASSWORD=$(ROLES_SVC_USER_PASSWORD) \
		-e DEBUG=$(DEBUG) \
		interview-assessment \
		"$(1)"
endef

define run_cmd
	$(if $(filter $(DOCKER_MAKE),true), $(call run_docker_cmd,$(1),$(2)), $(call run_sh_cmd,$(1)))
endef

nginx:
	docker-compose $(DOCKER_OPTS) up -d nginx

init:
	
	docker-compose up --build -d
	make exec
up:
	docker-compose up -d
	make exec
down:
	docker-compose down
exec:
	docker exec -it interview-assessment bash
logs:
	docker-compose logs -f


build:
	$(if $(filter $(DOCKER_MAKE),true),docker-compose $(DOCKER_OPTS) build interview-assessment,:)

alembic: build
	@echo "--------------------------------------------------------------------------------"
	@echo "Upgrading Alembic"
	@echo "--------------------------------------------------------------------------------"
	$(call run_cmd,poetry install && poetry run deploy/tools/alembic_upgrade)

dev: build alembic $(if $(filter $(DOCKER_MAKE),true),nginx,)
	$(call run_cmd,poetry install && poetry shell)