#!/bin/bash

set -e

start () {
    # This path could be configurable
    # It is not really necessary to make it configurable since there is no
    # usecase to change the database path inside the docker container
    if [ -e /media/data/fact_wt_mongodb/REINITIALIZE_DB ]; then
        python3 /opt/FACT_core/src/init_database.py && \
            rm -rf /media/data/fact_wt_mongodb/REINITIALIZE_DB
    fi

    # TODO This only works when the radare server runs on the docker host
    # Probably the start_fact_frontend.py should not start radare but rather
    # let the user start the radare container (and use docker-compose)
    radare2_host=$(/sbin/ip route|awk '/default/ { print $3 }')

    # If the user provides a different configuration the patch will fail
    sed "s/RADARE2_HOST/$radare2_host/" /opt/FACT_core/0002_main_cfg.patch.template | patch --forward /opt/FACT_core/src/config/main.cfg || true

    exec /opt/FACT_core/start_all_installed_fact_components "$@"
}

case "$1" in
    "start")
        shift 1
        start $@
    ;;
    "start-branch")
        shift 1
        git --git-dir=/opt/FACT_core/.git fetch
        git --git-dir=/opt/FACT_core/.git checkout $1
        shift 1
        start $@
    ;;
    "pull-containers")
        # We can't to this in the Dockerfile, because the docker socket is not shared to there
        exec /opt/FACT_core/src/install.py \
            --backend-docker-images \
            --frontend-docker-images
    ;;
    "pytest")
        shift 1
        cd /opt/FACT_core
        pytest $@
    ;;
    *)
        # This script is supposed to always be called by start.py so refer to it here
        printf "See https://github.com/fkie-cad/FACT_docker for how to start this container\n"
        exit 0
esac
