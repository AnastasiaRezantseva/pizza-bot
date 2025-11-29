VENV_DIR = .venv
ACTIVATE_VENV := . $(VENV_DIR)/bin/activate

$(VENV_DIR):
	python3 -m venv $(VENV_DIR)
	$(ACTIVATE_VENV) && pip install --upgrade pip
	$(ACTIVATE_VENV) && pip install --requirement requirements.txt

install: $(VENV_DIR)

black: $(VENV_DIR)
	$(ACTIVATE_VENV) && black .

ruff: $(VENV_DIR)
	$(ACTIVATE_VENV) && ruff check .

pytest: $(VENV_DIR)
	$(ACTIVATE_VENV) && PYTHONPATH=. pytest

test: black ruff pytest


DOCKER_NETWORK=pizza_bot_network

POSTGRES_VOLUME=postgres_data
POSTGRES_CONTAINER=postgres_17

BOT_IMAGE=rezantsevaanastasia/unn_pizza_bot
BOT_CONTAINER=pizza_bot

include .env
export $(shell sed 's/=.*//' .env)

docker_volume:
	docker volume create $(POSTGRES_VOLUME) || true

docker_net:
	docker network create $(DOCKER_NETWORK) || true

postgres_run: docker_volume docker_net
	docker run -d \
	  --name $(POSTGRES_CONTAINER) \
	  -e POSTGRES_USER="$(POSTGRES_USER)" \
	  -e POSTGRES_PASSWORD="$(POSTGRES_PASSWORD)" \
	  -e POSTGRES_DB="$(POSTGRES_DATABASE)" \
	  -p "$(POSTGRES_HOST_PORT):$(POSTGRES_CONTAINER_PORT)" \
	  -v $(POSTGRES_VOLUME):/var/lib/postgresql/data \
	  --health-cmd="pg_isready -U $(POSTGRES_USER)" \
	  --health-interval=10s \
	  --health-timeout=5s \
	  --health-retries=5 \
	  --network $(DOCKER_NETWORK) \
	  postgres:17

postgres_stop:
	docker stop $(POSTGRES_CONTAINER)
	docker rm $(POSTGRES_CONTAINER)

build:
	docker buildx build \
	  -t $(BOT_IMAGE) \
	  --platform linux/amd64,linux/arm64 \
	  -f Dockerfile \
	  --load \
	  .

push:
	docker push $(BOT_IMAGE)

run: docker_net
	docker run -d \
	  --name $(BOT_CONTAINER) \
	  --restart unless-stopped \
	  -e TELEGRAM_BASE_URI="${TELEGRAM_BASE_URI}" \
	  -e POSTGRES_HOST="$(POSTGRES_CONTAINER)" \
	  -e POSTGRES_PORT="5432" \
	  -e POSTGRES_USER="$(POSTGRES_USER)" \
	  -e POSTGRES_PASSWORD="$(POSTGRES_PASSWORD)" \
	  -e POSTGRES_DATABASE="$(POSTGRES_DATABASE)" \
	  -e TELEGRAM_TOKEN="$(TELEGRAM_TOKEN)" \
	  --network $(DOCKER_NETWORK) \
	  $(BOT_IMAGE)

stop:
	docker stop $(BOT_CONTAINER)
	docker rm $(BOT_CONTAINER)

logs:
	docker logs -f $(BOT_CONTAINER)

logs-postgres:
	docker logs -f $(POSTGRES_CONTAINER)

logs-tail:
	docker logs --tail 50 $(BOT_CONTAINER)

logs-timestamps:
	docker logs -t $(BOT_CONTAINER)

restart: stop run logs

status:
	docker ps -a