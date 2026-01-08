# Makefile for Cloud Deploy API Gateway

.PHONY: help install dev prod test clean migrate docker-up docker-down docker-build lint format

help:
	@echo "Cloud Deploy API Gateway - Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  install     Install dependencies"
	@echo "  dev         Run development server"
	@echo "  prod        Run production server"
	@echo "  test        Run tests"
	@echo "  clean       Clean up temporary files"
	@echo "  migrate     Run database migrations"
	@echo "  docker-up   Start Docker containers"
	@echo "  docker-down Stop Docker containers"
	@echo "  docker-build Build Docker image"
	@echo "  lint        Run code linting"
	@echo "  format      Format code"

install:
	pip install -r requirements_complete.txt

dev:
	ENVIRONMENT=development python run_production.py

prod:
	ENVIRONMENT=production python run_production.py

test:
	pytest test_api_complete.py -v

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf logs/*.log

migrate:
	alembic upgrade head

docker-up:
	docker-compose -f docker-compose.complete.yml up

docker-down:
	docker-compose -f docker-compose.complete.yml down

docker-build:
	docker build -f Dockerfile.complete -t cloud-deploy-api .

lint:
	flake8 .
	mypy .

format:
	black .
	isort .
