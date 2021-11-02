# Docker image for FACT_core
The docker image provides an installation of all fact components (db, frontend,
backend). Currently, you have to build it yourself, but we plan to provide a
prebuilt image via Dockerhub. For instructions see [Usage](#usage).

Because FACT uses docker itself, the docker socket from the host will be
passed to the container. Please make sure that your user is a member of the
`docker` group.

## Usage
For more advanced usage we provide a Python script to cover most usecases.
If your usecase is not supported feel free to open a PR or hack it up privately.

Probably the most imporant command is `./start.py build`.
After that you might run:
```sh
$ mkdir ~/fact_mongo && mkdir ~/fact_data
$ ./start.py run --wt-mongodb-path ~/fact_mongo --fw-data-path ~/fact_data
```

Use `./start.py --help` to get help about the usage of the script.

If you use `--config` and change anything related to the mongodb
database run ```touch <your fact_wt_mongodb path>/REINITIALIZE_DB```
(i.e. `touch /media/data/fact_wt_mongodb/REINITIALIZE_DB`).
This will tell the container to (re)initialize the database.
If you use the container the first time the script does this automatically for
you.
Also be aware that the `temp_dir_path` in `main.cfg` has to match the path
specified by `--docker-dir`.

## Entrypoint
The docker entrypoint accepts three arguments.
`start` to start the container.

`pull-containers` to pull docker containers needed on the host.

`start-branch` to checkout a different branch before running FACT.

## Distributed setup
If you want to have a distributed setup you have to build the three images.
For this you can simply adapt the Dockerfile to install the respective
components and change the entrypoint.
Then follow the instructions in
[INSTALL.md](https://github.com/fkie-cad/FACT_core/blob/master/INSTALL.md) for
a distributed setup.
You should also have a look at [start.py](./start.py) to see what arguments docker should
be started with.

# Workarounds used
If you tinker around with the docker image you might encounter some strange
behavior caused by the following workarounds.

## Docker in docker
As FACT uses docker heavily, we pass the docker socket to the container.

One use of docker is the unpacker. Docker is started with something along the
lines of
`docker run -v PATH_ON_DOCKER_HOST:HARDCODED_PATH_USED_IN_THE_CONTAINER unpacker`.

This means that when FACT runs inside an container it must have access to
`PATH_ON_DOCKER_HOST`.
Currently `PATH_ON_DOCKER_HOST` is always a subdirectory of `temp_dir_path` and
created dynamically (similar to `mktemp`) or it is a subdirectory of the
`fw-data-path`.
Can't know in advance what directories on the host will be needed in the
container because of the dynamically created directorys. To work
around this we simply mount `temp_dir_path` in the container.
