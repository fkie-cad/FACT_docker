VERSION=4.0

all: backend frontend scripts

common:
	docker build -f Dockerfile-common -t fact-core-common:${VERSION} .

backend: common
	docker build -f Dockerfile-backend -t fact-core-backend:${VERSION} .

frontend: common
	docker build -f Dockerfile-frontend -t fact-core-frontend:${VERSION} .

scripts:
	docker build -f Dockerfile-scripts -t fact-core-scripts:${VERSION} .
