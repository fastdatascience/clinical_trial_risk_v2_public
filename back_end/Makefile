SHELL := /bin/bash -O globstar

run_dev:
	@echo "Running in dev context..."
	hypercorn --reload --config=hypercorn.toml 'app.main:app'

run:
	@echo "Running in production context..."
	hypercorn --config=hypercorn-prod.toml 'app.main:app'

cli:
	python -m cli

run_parallel:
	@echo "Starting Docker Redis container..."
	@docker run --rm -p 6379:6379 -d --name temp_redis redis:7.2-alpine
	@echo "Waiting for Redis to become ready..."
	@while ! docker exec temp_redis redis-cli ping; do \
	    echo "Waiting for Redis..."; \
	    sleep 1; \
	done
	@echo "Redis is ready. Proceeding with the rest of the jobs..."
	@echo "Running commands in parallel"
	@parallel ::: 'JAVA_HOME="/usr/lib64/jvm/java-17-openjdk-17" cd tika-grpc && mvn clean && mvn package && mvn exec:java' 'rq worker --with-scheduler'

py_generate_proto:
	python -m grpc_tools.protoc -I app/proto --python_out=app/grpc_client/document_parser --pyi_out=app/grpc_client/document_parser --grpc_python_out=app/grpc_client/document_parser app/proto/DocumentParser.proto


run_tika_dev:
	JAVA_HOME="/usr/lib64/jvm/java-17-openjdk-17" cd tika-grpc && mvn clean && mvn package && mvn exec:java


test:
	pytest -x --cov-report term-missing --cov-report html --cov-branch \
	       --cov clinical_trials_backend/

run_job_q:
	./run_q.sh

run_rq_job_q:
	rq worker --with-scheduler

lint:
	@echo
	ruff .
	@echo
	blue --check --diff --color .
	@echo
	mypy .
	@echo
	pip-audit


format:
	ruff --silent --exit-zero --fix .
	blue .


build:
	docker build -t clinical_trials_backend .


smoke_test: build
	docker run --rm -d -p 5000:5000 --name clinical_trials_backend clinical_trials_backend
	sleep 2; curl http://localhost:5000/hello
	docker stop clinical_trials_backend
