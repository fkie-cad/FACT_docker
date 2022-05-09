#!/bin/bash

set -e

case "$1" in
    "start-backend")
        # We can't use exec since it will crash somehow
        shift 1
        /opt/FACT_core/start_fact_backend "$@"
        exit $?
    ;;
    "start-frontend")
        shift 1
        /opt/FACT_core/start_fact_frontend "$@"
        exit $?
    ;;
    "initialize-db")
        exec /usr/bin/python3 /opt/FACT_core/src/init_postgres.py
    ;;
    "pull-containers")
        # We can't to this in the Dockerfile, because the docker socket is not shared to there
        exec /opt/FACT_core/src/install.py \
            --backend-docker-images \
            --frontend-docker-images
    ;;
    *)
        # This script is supposed to always be called by start.py so refer to it here
        printf "See https://github.com/fkie-cad/FACT_docker for how to start this container\n"
        exit 1
esac
