VENV_DIR = .venv
ACTIVATE_VENV := . $(VENV_DIR)/bin/activate

$(VENV_DIR):
	python3 -m venv $(VENV_DIR)
	$(ACTIVATE_VENV) && pip install --upgrade pip
	$(ACTIVATE_VENV) && pip install --requirement requirements.txt

install: $(VENV_DIR)

# Run black formatter
black: $(VENV_DIR)
	$(ACTIVATE_VENV) && black .

# Run ruff linter
ruff: $(VENV_DIR)
	$(ACTIVATE_VENV) && ruff check .


# Run all tests (includes black, ruff, and pytest)
test: black ruff 

BOT_IMAGE=rezantsevaanastasia/unn_aiogram_echo_bot
BOT_CONTAINER=aiogram_echo_bot

include .env
export $(shell sed 's/=.*//' .env)

build:
	docker buildx build \
	  -t $(BOT_IMAGE) \
	  --platform linux/amd64,linux/arm64 \
	  -f Dockerfile \
	  --load \
	  .
push:
	docker push $(BOT_IMAGE)

run: 
	docker run -d \
	  --name $(BOT_CONTAINER) \
	  --restart unless-stopped \
	  -e TELEGRAM_TOKEN="$(TELEGRAM_TOKEN)" \
	  $(BOT_IMAGE)

stop:
	docker stop $(BOT_CONTAINER)
	docker rm $(BOT_CONTAINER)