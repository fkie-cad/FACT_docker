# Docker image for FACT_core
The docker image provides an installation of all fact components (db, frontend,
backend). Currently, you have to build it yourself, but we plan to provide a
prebuilt image via Dockerhub. For instructions see [Advanced usage](#advanced-usage).

Because FACT uses docker itself, the docker socket from the host will be
passed to the container. Please make sure that your user is a member of the
`docker` group.

## Most simple usage
If you just want to run FACT and not worry about anything we've got your back.
Be aware that all state of FACT is only in the container so if you pull a new
FACT version everything (most importantly your database) will be lost.

> Note that the image is currently not uploaded so you have to
[build](#advanced-usage) it yourself

Simply run
```bash
# Pull docker containers needed on the host
# This is just needed the first time you use FACT
docker run \
	--rm \
	-it \
	--group-add $(getent group docker | cut -d: -f3) \
	-v /var/run/docker.sock:/var/run/docker.sock \
	fkiecad/fact pull-containers

# The docker daemon will write some things in there
mkdir /tmp/fact-docker-tmp && chgrp docker /tmp/fact-docker-tmp

# Start fact
docker run \
	-it \
	--name fact \
	--group-add $(getent group docker | cut -d: -f3) \
	-v /var/run/docker.sock:/var/run/docker.sock \
	-v /tmp/fact-docker-tmp:/tmp/fact-docker-tmp \
	-p 5000:5000 \
	fkiecad/fact start

```

## Advanced usage
For more advanced usage we provide a Python script to cover most usecases.
If your usecase is not supported feel free to open a PR or hack it up privately.

Run `./start.py --help` to get help abuot the usage of the script.

If you use `--config` and change anything related to the mongodb
database run `touch YOUR_FACT_WT_MONGODB_PATH/REINITIALIZE_DB`.
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
Then follow the instructions in [INSTALL.md](../INSTALL.md) for a distributed
setup.
You should also have a look at [start.py](./start.py) to see what arguments docker should
be started with.

# Workarounds used
As FACT uses docker heavily, we pass the docker socket to the container.

One use of docker is the unpacker. Docker is started with something along the
lines of
`docker run -v PATH_ON_DOCKER_HOST:HARDCODED_PATH_USED_IN_THE_CONTAINER unpacker`.

This means that when FACT runs inside an container it must have access to
`PATH_ON_DOCKER_HOST`.
Currently `PATH_ON_DOCKER_HOST` is always a subdirectory of `temp_dir_path` but
created dynamically (similar to `mktemp`). This means that we can't know in
advance what directories on the host will be needed in the container. To work
around this we simply mount `temp_dir_path` in the container.