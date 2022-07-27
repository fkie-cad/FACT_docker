ifndef FACT_DOCKER_VERSION
    $(error FACT_DOCKER_VERSION is not set)
endif

all: backend frontend scripts

common:
	docker build \
		-f Dockerfile-common \
		--build-arg=FACT_DOCKER_VERSION=${FACT_DOCKER_VERSION} \
		-t fact-core-common:${FACT_DOCKER_VERSION} \
		.

backend: common
	docker build \
		-f Dockerfile-backend \
		--build-arg=FACT_DOCKER_VERSION=${FACT_DOCKER_VERSION} \
		-t fact-core-backend:${FACT_DOCKER_VERSION} \
		.

frontend: common
	docker build \
		-f Dockerfile-frontend \
		--build-arg=FACT_DOCKER_VERSION=${FACT_DOCKER_VERSION} \
		-t fact-core-frontend:${FACT_DOCKER_VERSION} \
		.

scripts:
	docker build \
		-f Dockerfile-scripts \
		--build-arg=FACT_DOCKER_VERSION=${FACT_DOCKER_VERSION} \
		-t fact-core-scripts:${FACT_DOCKER_VERSION} \
		.
