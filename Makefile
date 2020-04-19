PROJECT_NAME=cashback


help:  ## This help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

clean:  ## Clean python bytecodes, optimized files, logs, cache, coverage...
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf
	@rm -f .coverage
	@rm -rf htmlcov/
	@rm -f coverage.xml
	@rm -f *.log

conf-env:  ## Generate the .env file for local development
	@cp -n contrib/localenv .env
	@echo 'Please configure params from .env file before starting. Ask for one from your peers (may be easier ;)'

requirements-pip:  ## Install the app requirements
	@pip install --upgrade pip
	@pip install -r requirements/development.txt

install-linux: conf-env requirements-pip
	@echo "[OK] Installation completed"

test: clean  ## Run the test suite
	@pytest $(PROJECT_NAME) -x -s -vvv

test-ci: clean  ## Run the integration and normal test suite for circle-ci
	@pytest $(PROJECT_NAME) -x -s -vvv --ci -m "integration"

test-matching: clean ## Run only tests matching pattern
	@pytest $(PROJECT_NAME) -k $(test) -xs -s -vvv

test-integration: clean  ## Run the integration test suite
	@pytest $(PROJECT_NAME) -x -s -vvv -m "integration"

coverage: clean ## Run the test coverage
	@mkdir -p logs
	@pytest $(PROJECT_NAME) -x --cov=$(PROJECT_NAME)/

lint: clean  ## Run pylint linter
	@echo ">>> Running linter..."
	@pylint --rcfile=.pylintrc  $(PROJECT_NAME)/*

isort:  ## Run isort separately due to our specific imports order on the worker and other modules case
	@isort -m 3 -tc -y

style:  ## Run isort and black auto formatting code style in the project
	@black -t py37 -l 79 $(PROJECT_NAME)/. --exclude '/(\.git|\.venv|env|venv|build|dist)/'

style-check:  ## Check isort and black code style
	@black -t py37 -l 79 --check $(PROJECT_NAME)/. --exclude '/(\.git|\.venv|env|venv|build|dist)/'

migrations:		## Makes migration.
	@alembic -n alembic revision --autogenerate;

migrate: ## Upgrades database.
	@alembic -n alembic upgrade head;

initial-data:  ## Initial data in database
	@python initial_data.py

runserver-dev: clean ## Run local web server
	@uvicorn $(PROJECT_NAME).main:app --host="0.0.0.0" --port=8080 --reload

runserver: clean migrate initial-data ## Run live web server
	@uvicorn $(PROJECT_NAME).main:app --host="0.0.0.0" --port=8080 --workers=4

docker-compose-up: clean  ## Raise docker-compose for development environment
	@docker-compose up -d

docker-compose-stop: clean  ## Stop docker-compose for development environment
	@docker-compose stop

docker-compose-rm: docker-compose-stop ## Delete the development environment containers
	@docker-compose rm -f

docker-build-local-app: clean  ## Build local docker image (app)
	@./deploy/scripts/build-docker-image.sh $(PROJECT_NAME) --app

