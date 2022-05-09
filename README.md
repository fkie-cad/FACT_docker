# Docker image for FACT_core
This repository mainly contains the `Dockerfile` and `docker-compose.yml` to
build and run a containerized installation of FACT_core.
FACT is split in two images (backend and frontend).

Because FACT uses docker itself, the docker socket from the host will be
passed to the container. Please make sure that your user is a member of the
`docker` group.

## Usage
The following lines of shell should get you started to use FACT in docker.
```sh
$ docker pull \
    ghcr.io/fkie-cad/fact-core-frontend:4.0 \
    ghcr.io/fkie-cad/fact-core-backend:4.0 \
    ghcr.io/fkie-cad/fact-core-scripts:4.0
$ ./start.py pull
$ ./start.py compose-env \
    --firmware-file-storage-dir path_to_fw_data_dir
    # Have a look if it looks right
$ eval $(./start.py compose-env --firmware-file-storage-dir path_to_fw_data_dir)
$ export FACT_DOCKER_POSTGRES_PASSWORD=mypassword
$ docker compose up database
$ ./start.py initialize-db \
    --network fact-docker-fact-network
$ docker compose up
```

We provide a `docker-compose.yml` and a python script to get FACT in docker
running.
The `docker-compose.yml` is parameterized with environment variables.
All variables are prefixed by `FACT_DOCKER_`.
The variables can be set to sane defaults with `./start.py compose-env`.
For documentation about their meanings see `docker-compose.yml`.

Use `./start.py --help` to get help about the usage of the script.

## Development of FACT\_core in FACT\_docker
Since the FACT\_core is pretty invasive is might be desirable to not install FACT on your system and use this docker image instead.
To have access to a FACT installation you can for example start the container with `--entrypoint /bin/bash`.

## Bugs
FACT\_docker is in early stages and has some bugs that currently can't be fixed due to FACT\_core's architecture.
These bugs are documented here.

### Docker in docker
As FACT uses docker heavily, we pass the docker socket to the container.

One use of docker is the unpacker. Docker is started with something along the
lines of
`docker run -v PATH_ON_DOCKER_HOST:HARDCODED_PATH_USED_IN_THE_CONTAINER unpacker`.

This means that when FACT runs inside a container it must have access to
`PATH_ON_DOCKER_HOST`.
Currently `PATH_ON_DOCKER_HOST` is not always a subdirectory of `docker-mount-base-dir`.
This mostly affects tests (where test data is mounted in containers).
