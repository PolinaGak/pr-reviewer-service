.PHONY: build run test lint migrate up

build:
	docker-compose build

up:
	docker-compose up --build

migrate:
	docker-compose run --rm app alembic upgrade head

test:
	docker-compose run --rm app pytest tests/ -v

lint:
	docker-compose run --rm app black app/ tests/

down:
	docker-compose down -v

install:
	pip install -r requirements.txt
	pip install -r dev_requirements.txt