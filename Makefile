SHELL := /bin/bash

isort:
	isort .

black:
	brunette .

clean: isort black

lint:
	isort --check-only . --diff
	flake8 --show-source .
	brunette . --check -t py38

include .env
export $(shell sed 's/=.*//' .env)

build:
	docker build --build-arg OPENAI_API_KEY_ARG=${OPENAI_API_KEY} -t youtube_chat .

run:
	docker run -d -it --init \
	--ipc=host \
	--volume=$(CURDIR):/app \
	--publish="4545:4545" \
	--publish="7860:7860" \
	--publish="7861:7861" \
	--env-file .env \
	youtube_chat bash